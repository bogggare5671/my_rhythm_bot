
import json
import os
import serial
import time

LEVELS_PATH = "/root/my_rhythm_bot/levels.json"
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

SOUND_FOLDER = "/root/my_rhythm_bot/sounds"
AVAILABLE_SOUNDS = [f for f in os.listdir(SOUND_FOLDER) if f.endswith(".wav")]

def load_levels():
    if os.path.exists(LEVELS_PATH):
        with open(LEVELS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_levels(levels):
    with open(LEVELS_PATH, "w", encoding="utf-8") as f:
        json.dump(levels, f, indent=2, ensure_ascii=False)
    print("✅ Уровни сохранены")

def choose_sounds():
    files = [f for f in os.listdir(SOUND_FOLDER) if f.endswith(".wav")]
    sounds = {}
    print("\nВыбери звуки для каждой кнопки:")
    for idx, f in enumerate(files):
        print(f"[{idx}] {f}")
    for i in range(3):
        while True:
            try:
                choice = int(input(f"Кнопка {i}: "))
                if 0 <= choice < len(files):
                    sounds[str(i)] = files[choice]
                    break
            except:
                print("❌ Неверный ввод")
    return sounds

def capture_pattern_from_arduino(count):
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print("Нажимай кнопки по порядку...")
    pattern = []
    presses = 0
    last_time = time.time()

    # Уведомляем Arduino разрешить ввод
    ser.write(b"ALLOW_INPUT\n")
    while presses < count:
        line = ser.readline().decode().strip()
        if line.startswith("BTN"):
            btn = int(line.split()[1])
            now = time.time()
            pause = round(now - last_time, 2)
            last_time = now
            pattern.append([btn, pause])
            presses += 1
            print(f"{presses}: кнопка {btn}, пауза {pause}")
    ser.write(b"BLOCK_INPUT\n")
    return pattern

def edit_level(level):
    while True:
        print(f"\n== {level['name']} ==")
        for i, variant in enumerate(level["pattern_variants"]):
            print(f"[{i}] {variant}")
        print("[H] Добавить паттерн вручную")
        print("[A] Добавить паттерн с платы")
        print("[D] Удалить паттерн")
        print("[Z] Назад")
        choice = input("Выбор: ").strip().lower()
        if choice == 'h':
            pattern = []
            print("Ввод: 'номер пауза' (пример: 0 0.6), 'done' — завершить")
            while True:
                line = input(">>> ")
                if line == 'done':
                    break
                try:
                    btn, pause = line.split()
                    pattern.append([int(btn), float(pause)])
                except:
                    print("Неверный ввод, попробуй снова.")
            level["pattern_variants"].append(pattern)
        elif choice == 'a':
            try:
                count = int(input("Сколько нажатий? "))
                pattern = capture_pattern_from_arduino(count)
                level["pattern_variants"].append(pattern)
            except:
                print("Ошибка при чтении с платы.")
        elif choice == 'd':
            try:
                index = int(input("Номер паттерна для удаления: "))
                if 0 <= index < len(level["pattern_variants"]):
                    level["pattern_variants"].pop(index)
            except:
                print("Ошибка выбора.")
        elif choice == 'z':
            break

def run_editor():
    levels = load_levels()
    while True:
        print("\n=== УРОВНИ ===")
        for i, level in enumerate(levels):
            print(f"[{i+1}] {level['name']}")
        print("[N] Новый уровень")
        print("[S] Сохранить и выйти")
        choice = input("Выбор: ").strip().lower()
        if choice == 'n':
            name = input("Название уровня: ")
            sounds = choose_sounds()
            levels.append({
                "name": name,
                "pattern_variants": [],
                "sounds": sounds
            })
        elif choice == 's':
            save_levels(levels)
            break
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(levels):
                    edit_level(levels[index])
            except:
                print("Ошибка выбора")

if __name__ == "__main__":
    run_editor()
