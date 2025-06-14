#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_arduino.py

Тест работы Arduino-скетча с I2C-LCD на кириллице:
  • Конвертирует UTF-8 → коды LiquidCrystal_I2C_Cyrillic
  • Отправляет на экран несколько строк
  • Мигает светодиодами
  • Принимает и выводит BTN/RESET
  • Проверяет выдачу приза
"""

import serial
import time

# === Настройки ===
SERIAL_PORT = '/dev/ttyUSB0'  # ваш порт
BAUDRATE     = 9600
TIMEOUT      = 1              # s

# === Карта UTF-8 → CP1251 коды для LiquidCrystal_I2C_Cyrillic ===
RU_MAP = {
    'Б': 0x80, 'Г': 0x81, 'Ё': 0x82, 'Ж': 0x83, 'З': 0x84, 'И': 0x85, 'Й': 0x86,
    'Л': 0x87, 'П': 0x88, 'У': 0x89, 'Ф': 0x8A, 'Ч': 0x8B, 'Ш': 0x8C, 'Ъ': 0x8D,
    'Ы': 0x8E, 'Э': 0x8F, 'Ю': 0x90, 'Я': 0x91,
    'б': 0x92, 'в': 0x93, 'г': 0x94, 'ё': 0x95, 'ж': 0x96, 'з': 0x97, 'и': 0x98,
    'й': 0x99, 'к': 0x9A, 'л': 0x9B, 'м': 0x9C, 'н': 0x9D, 'п': 0x9E, 'т': 0x9F,
    'ч': 0xA0, 'ш': 0xA1, 'ъ': 0xA2, 'ы': 0xA3, 'ь': 0xA4, 'э': 0xA5,
    'ю': 0xA6, 'я': 0xA7,
    'Д': 0xA8, 'Ц': 0xA9, 'Щ': 0xAA, 'д': 0xAB, 'ф': 0xAC, 'ц': 0xAD, 'щ': 0xAE
}

# === Таблица «кириллица → латиница» для букв-«двойников» ===
ASCII_EQUIV = {
    'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H',
    'О':'O','Р':'P','С':'S','Т':'T','Х':'X',
    'а':'a','в':'b','е':'e','к':'k','м':'m','н':'h',
    'о':'o','р':'p','с':'s','т':'t','х':'x'
}

def rus_to_lcd(s: str) -> bytes:
    """
    Преобразует UTF-8 строку в байты CP1251-кодов
    для LiquidCrystal_I2C_Cyrillic:
     - символы из RU_MAP → специальные коды (0x80–0xAE)
     - символы из ASCII_EQUIV → их латинский эквивалент
     - всё остальное (ASCII, цифры, знаки) остаётся без изменений
    """
    out = bytearray()
    for ch in s:
        if ch in RU_MAP:
            out.append(RU_MAP[ch])
        elif ch in ASCII_EQUIV:
            out += ASCII_EQUIV[ch].encode('ascii')
        else:
            b = ch.encode('ascii', errors='ignore')
            if b:
                out += b
    return bytes(out)

# === Открываем порт ===
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=TIMEOUT)
time.sleep(2)

# === Команды на Arduino ===
def send_lcd(text: str):
    payload = rus_to_lcd(text)
    ser.write(b"LCD " + payload + b"\n")
    time.sleep(0.1)

def show_led(n: int):
    ser.write(f"SHOW {n}\n".encode()); time.sleep(0.1)

def hide_led(n: int):
    ser.write(f"LED OFF {n}\n".encode()); time.sleep(0.1)

def allow_input():
    ser.write(b"ALLOW_INPUT\n"); time.sleep(0.1)

def block_input():
    ser.write(b"BLOCK_INPUT\n"); time.sleep(0.1)

def prize():
    ser.write(b"PRIZE\n"); time.sleep(0.1)

def read_responses(duration=5.0):
    deadline = time.time() + duration
    while time.time() < deadline:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print(f">>> {line}")

# === Тестовая последовательность ===
if __name__ == "__main__":
    print("1) Тест LCD — выводим приветствие")
    send_lcd("Ритм-Бот готов")
    time.sleep(2)

    print("2) Мигаем LED0, LED1 и LED2")
    show_led(0); time.sleep(1); hide_led(0)
    show_led(1); time.sleep(1); hide_led(1)
    show_led(2); time.sleep(1); hide_led(2)

    print("3) Проверяем ввод кнопок (5 сек) — нажмите на Arduino")
    allow_input()
    read_responses(5)
    block_input()

    print("4) Тест сервопривода (приз)")
    prize()
    time.sleep(2)

    print("Готово.")
    ser.close()
