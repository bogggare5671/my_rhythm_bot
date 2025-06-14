# game/engine.py

import time
import random
import json

from .config import (
    LEVELS_PATH, SOUND_FOLDER,
    TIMEOUT_SECONDS, TIMING_TOLERANCE,
    SESSION_LIMIT, AFTER_LEVEL_PAUSE
)
from .serial_io import (
    block_input, allow_input, show, led_off,
    prize, read_line
)
from .lcd import lcd
from .audio import play_sound


def load_levels():
    with open(LEVELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def wait_for_start():
    """
    Ждём, пока пользователь нажмёт RESET (START) на Arduino.
    При этом выводим приглашение на LCD.
    """
    lcd("Нажми СТАРТ")
    while True:
        line = read_line()
        if line == "RESET":
            lcd("Новый игрок!")
            return


def wait_for_input(expected_pattern):
    """
    Считывает нажатия кнопок, пока не будет столько же,
    сколько шагов в expected_pattern.
    Возвращает "OK", "WRONG", "TIMEOUT" или "RESET".
    """
    result = []
    times = []
    start_time = time.time()

    while len(result) < len(expected_pattern):
        # таймаут
        if time.time() - start_time > TIMEOUT_SECONDS:
            return "TIMEOUT"

        line = read_line()
        if line.startswith("BTN"):
            btn = int(line.split()[1])
            now = time.time()

            result.append(btn)
            times.append(now)
            # звук по нажатию
            play_sound(f"{btn}.wav")

            if len(result) == 1:
                # сброс таймера после первого нажатия
                start_time = now

        elif line == "RESET":
            return "RESET"

    # проверяем интервалы
    deltas = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    expected_deltas = [step[1] for step in expected_pattern][:-1]

    for i, (got, exp) in enumerate(zip(deltas, expected_deltas), start=1):
        if abs(got - exp) > exp * TIMING_TOLERANCE:
            lcd("Ошибка ритма!")
            return "WRONG"

    # проверяем последовательность кнопок
    if result == [step[0] for step in expected_pattern]:
        return "OK"

    lcd("Ошибка!")
    return "WRONG"


def run_game():
    levels = load_levels()
    lcd("Ритм-Бот готов")

    while True:
        # старт новой сессии
        wait_for_start()
        session_start = time.time()
        level = 0
        flawless = True

        # прогон всех уровней
        while level < len(levels):
            if time.time() - session_start > SESSION_LIMIT:
                lcd("Время вышло")
                flawless = False
                break

            current = levels[level]
            name = current["name"]
            pattern_variants = current["pattern_variants"]
            sound_map = current["sounds"]

            # выбираем и показываем уровень
            lcd(name)
            pattern = random.choice(pattern_variants)

            block_input()
            for btn, pause in pattern:
                show(btn)
                play_sound(sound_map[str(btn)])
                time.sleep(pause)
                led_off(btn)
                time.sleep(0.1)
            allow_input()

            lcd("Повтори ритм")
            resp = wait_for_input(pattern)

            if resp == "RESET":
                # сброс до первого уровня
                level = 0
                flawless = True
                break
            elif resp == "TIMEOUT":
                flawless = False
                break
            elif resp == "OK":
                lcd("Молодец!")
                play_sound("success.wav")
                time.sleep(AFTER_LEVEL_PAUSE)
                level += 1
            else:  # "WRONG"
                lcd("Неверно!")
                play_sound("fail.wav")
                time.sleep(AFTER_LEVEL_PAUSE)
                flawless = False

        # итоги сессии
        if level == len(levels) and flawless:
            lcd("Все уровни!")
            lcd("Поздравляем!")
            prize()
            play_sound("prize.wav")
        else:
            # если вышли раньше по ошибке или таймауту
            lcd("Без приза :(")


# если кто-то хочет запустить именно эту функцию напрямую:
if __name__ == "__main__":
    run_game()
