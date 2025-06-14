def rus_to_lcd(text):
    table = {
        'А': '\x41', 'Б': '\xA0', 'В': '\x42', 'Г': '\xA1', 'Д': '\xE0',
        'Е': '\x45', 'Ж': '\xA3', 'З': '\xA4', 'И': '\xA5', 'Й': '\xA6',
        'К': '\x4B', 'Л': '\xA7', 'М': '\x4D', 'Н': '\x48', 'О': '\x4F',
        'П': '\xA8', 'Р': '\x50', 'С': '\x43', 'Т': '\x54', 'У': '\xA9',
        'Ф': '\xAA', 'Х': '\x58', 'Ц': '\xE1', 'Ч': '\xAB', 'Ш': '\xAC',
        'Щ': '\xE2', 'Ъ': '\xAD', 'Ы': '\xAE', 'Ь': '\xAF', 'Э': '\xE3',
        'Ю': '\xE4', 'Я': '\xE5',
        'а': '\x61', 'б': '\xB0', 'в': '\x62', 'г': '\xB1', 'д': '\xE6',
        'е': '\x65', 'ж': '\xB3', 'з': '\xB4', 'и': '\xB5', 'й': '\xB6',
        'к': '\x6B', 'л': '\xB7', 'м': '\x6D', 'н': '\x68', 'о': '\x6F',
        'п': '\xB8', 'р': '\x70', 'с': '\x63', 'т': '\x74', 'у': '\xB9',
        'ф': '\xBA', 'х': '\x78', 'ц': '\xE7', 'ч': '\xBB', 'ш': '\xBC',
        'щ': '\xE8', 'ъ': '\xBD', 'ы': '\xBE', 'ь': '\xBF', 'э': '\xE9',
        'ю': '\xEA', 'я': '\xEB'
    }
    return ''.join([table.get(c, c) for c in text])

import serial
import time
import subprocess
import json
import os
import random
from play_sound_clean import process_and_play as play_sound

LEVELS_PATH = "/root/my_rhythm_bot/levels.json"
SOUND_FOLDER = "/root/my_rhythm_bot/sounds"
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
TIMEOUT_SECONDS = 20
TIMING_TOLERANCE = 1.5
SESSION_LIMIT = 300
AFTER_LEVEL_PAUSE = 2

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)

def lcd(text):
    msg = f"LCD {rus_to_lcd(text)}\n"
    ser.write(msg.encode())
    time.sleep(0.1)

lcd("Привет, мир!")

with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)


def show_pattern(pattern, sound_map):
    ser.write(b"BLOCK_INPUT\n")
    for btn, pause in pattern:
        ser.write(f"SHOW {btn}\n".encode())
        play_sound(sound_map[str(btn)])
        time.sleep(pause)
        ser.write(f"LED OFF {btn}\n".encode())
        time.sleep(0.1)
    ser.write(b"ALLOW_INPUT\n")

def wait_for_input(expected_rhythm):
    result = []
    times = []
    start_time = time.time()

    while len(result) < len(expected_rhythm):
        if time.time() - start_time > TIMEOUT_SECONDS:
            return "TIMEOUT"

        line = ser.readline().decode().strip()
        if line.startswith("BTN"):
            btn = int(line.split()[1])
            now = time.time()
            result.append(btn)
            times.append(now)
            play_sound(f"{btn}.wav")
            if len(result) == 1:
                start_time = now
        elif line == "RESET":
            return "RESET"

    deltas = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    expected_deltas = [p[1] for p in expected_rhythm][:-1]

    for i in range(len(deltas)):
        delta = deltas[i]
        expected = expected_deltas[i]
        if abs(delta - expected) > expected * TIMING_TOLERANCE:
            lcd("Ошибка ритма!")
            return "WRONG"

    if result == [p[0] for p in expected_rhythm]:
        return "OK"
    else:
        lcd("Ошибка!")
        return "WRONG"

def wait_for_start():
    lcd("Нажми СТАРТ")
    while True:
        line = ser.readline().decode().strip()
        if line == "RESET":
            lcd("Новый игрок!")
            return

lcd("Ритм-Бот Готов")

while True:
    wait_for_start()
    session_start = time.time()
    level = 0
    flawless = True

    while level < len(levels):
        if time.time() - session_start > SESSION_LIMIT:
            lcd("Время вышло")
            break

        current = levels[level]
        pattern = random.choice(current["pattern_variants"])
        sound_map = current["sounds"]

        lcd(current["name"])
        show_pattern(pattern, sound_map)
        lcd("Повтори ритм")

        response = wait_for_input(pattern)

        if response == "RESET":
            level = 0
            flawless = True
            break
        elif response == "TIMEOUT":
            lcd("Время ожидания")
            flawless = False
            break
        elif response == "OK":
            lcd("Молодец!")
            play_sound("success.wav")
            time.sleep(AFTER_LEVEL_PAUSE)
            level += 1
        else:
            lcd("Неверно!")
            play_sound("fail.wav")
            time.sleep(AFTER_LEVEL_PAUSE)
            flawless = False

    if level == len(levels):
        lcd("Все уровни!")
        if flawless:
            lcd("Поздравляем!")
            ser.write(b"PRIZE\n")
            play_sound("prize.wav")
        else:
            lcd("Без приза :(")
