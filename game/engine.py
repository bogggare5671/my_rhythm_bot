# game/engine.py

import time
import random
import json

from .config import (
    LEVELS_PATH,
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
    """Ждём RESET (START) от Arduino; дублируем в терминал."""
    lcd("Нажми СТАРТ")
    while True:
        if read_line() == "RESET":
            lcd("Новый игрок!")
            return

def wait_for_input(pattern, sound_map):
    """
    Считывает нажатия до длины pattern.
    - Первая пауза до первого нажатия не проверяется.
    - Проверяем интервалы между 2-м и далее нажатиями.
    Возвращает: "OK", "WRONG", "TIMEOUT" или "RESET".
    """
    result = []
    times = []
    start_time = None

    # Слушаем до тех пор, пока не наберём нужное число нажатий
    while len(result) < len(pattern):
        line = read_line()
        if not line:
            continue

        # Полезный лог в терминал
        print(f"[RAW BTN] '{line}'")

        # RESET прерывает ввод
        if line == "RESET":
            return "RESET"

        parts = line.strip().split()
        # Должно быть минимум два токена: BTN и номер
        if len(parts) != 2 or parts[0] != "BTN":
            continue

        # Пробуем распарсить номер кнопки
        try:
            btn = int(parts[1])
        except ValueError:
            continue

        now = time.time()
        # Устанавливаем стартовый таймер после первого клика
        if start_time is None:
            start_time = now

        # Глобальный таймаут от первого клика
        if now - start_time > TIMEOUT_SECONDS:
            return "TIMEOUT"

        # Сохраняем результат и время
        result.append(btn)
        times.append(now)

        # Звуковой отклик
        play_sound(sound_map.get(str(btn), f"{btn}.wav"))
        print(f"[INPUT] BTN {btn}")

    # Проверка интервалов между нажатиями (начиная со второго)
    deltas = [times[i] - times[i-1] for i in range(1, len(times))]
    expected_deltas = [step[1] for step in pattern][1:]
    for got, exp in zip(deltas, expected_deltas):
        print(f"[TIMING] got={got:.2f}s, exp={exp:.2f}s")
        if exp > 0 and abs(got - exp) > exp * TIMING_TOLERANCE:
            lcd("Ошибка ритма!")
            print("[ERROR] Rhythm mismatch")
            return "WRONG"

    # Проверка правильности последовательности
    expected_buttons = [step[0] for step in pattern]
    print(f"[RESULT] expected={expected_buttons}, got={result}")
    if result != expected_buttons:
        lcd("Ошибка последовательности!")
        print("[ERROR] Sequence mismatch")
        return "WRONG"

    return "OK"

def run_game():
    levels = load_levels()
    lcd("Ритм-Бот готов")
    lcd("Нажми CТАРТ")

    while True:
        wait_for_start()
        session_start = time.time()
        level = 0
        flawless = True
        restart = False

        while level < len(levels):
            if time.time() - session_start > SESSION_LIMIT:
                lcd("Время вышло")
                flawless = False
                break

            current = levels[level]
            lcd(current["name"])
            pattern = random.choice(current["pattern_variants"])
            print(f"[PATTERN] Level {level+1}: {pattern}")

            block_input()
            for btn, pause in pattern:
                show(btn)
                play_sound(current["sounds"][str(btn)])
                print(f"[SHOW] LED {btn}, pause={pause}")
                time.sleep(pause)
                led_off(btn)
                print(f"[SHOW] LED OFF {btn}")
                time.sleep(0.1)
            allow_input()

            lcd("Повтори ритм")
            print("[LCD] Повтори ритм")
            resp = wait_for_input(pattern, current["sounds"])

            if resp == "RESET":
                restart = True
                break
            elif resp == "TIMEOUT":
                lcd("Время ожидания")
                flawless = False
                break
            elif resp == "OK":
                lcd("Молодец!")
                play_sound("success.wav")
                time.sleep(AFTER_LEVEL_PAUSE)
                level += 1
            else:  # WRONG
                play_sound("fail.wav")
                time.sleep(AFTER_LEVEL_PAUSE)
                flawless = False

        if restart:
            print("[RUN] Restart session")
            continue

        if level == len(levels) and flawless:
            lcd("Все уровни!")
            lcd("Поздравляем!")
            prize()
            play_sound("prize.wav")
        else:
            lcd("Без приза :(")

if __name__ == "__main__":
    run_game()
