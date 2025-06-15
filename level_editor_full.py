import json
import os
import serial
import time

# Пути к файлам и настройка
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LEVELS_PATH = os.path.join(BASE_DIR, 'levels.json')
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

# Доступные звуки
SOUND_FOLDER = os.path.join(BASE_DIR, 'sounds')
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
    files = AVAILABLE_SOUNDS
    sounds = {}
    print("\nВыбери звук для каждой кнопки:")
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
                pass
            print("❌ Неверный ввод")
    return sounds


def capture_pattern_from_arduino(count):
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    print("Нажимай кнопки по порядку...")
    pattern = []
    presses = 0
    last_time = time.time()

    ser.write(b"ALLOW_INPUT\n")
    while presses < count:
        line = ser.readline().decode().strip()
        if line.startswith("BTN"):
            btn = int(line.split()[1])
            now = time.time()
            pause = round(now - last_time, 2) if presses > 0 else 0.0
            last_time = now
            pattern.append([btn, pause])
            presses += 1
            print(f"{presses}: кнопка {btn}, пауза {pause}")
    ser.write(b"BLOCK_INPUT\n")
    return pattern


def import_level_template():
    path = input("Путь к файлу JSON с уровнем: ")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lvl = json.load(f)
        if all(k in lvl for k in ('name','pattern_variants','sounds')):
            print(f"Импорт уровня '{lvl['name']}' успешен")
            return lvl
        else:
            print("❌ Шаблон уровня не содержит необходимых полей")
    except Exception as e:
        print(f"❌ Ошибка импорта шаблона: {e}")
    return None


def edit_level(level):
    while True:
        print(f"\n== Редактирование: {level['name']} ==")
        for i, variant in enumerate(level.get("pattern_variants", [])):
            print(f"[{i}] {variant}")
        print("[H] Вручную добавить паттерн")
        print("[A] Добавить паттерн с платы")
        print("[I] Импортировать уровень из шаблона")
        print("[D] Удалить паттерн")
        print("[Z] Назад")
        choice = input("Выбор: ").strip().lower()
        if choice == 'h':
            pattern = []
            print("Ввод: 'номер пауза' или 'done' для завершения")
            while True:
                line = input(">>> ")
                if line == 'done': break
                try:
                    btn, pause = line.split()
                    pattern.append([int(btn), float(pause)])
                except:
                    print("Неверный ввод")
            level.setdefault('pattern_variants', []).append(pattern)
        elif choice == 'a':
            try:
                count = int(input("Сколько нажатий? "))
                pattern = capture_pattern_from_arduino(count)
                level.setdefault('pattern_variants', []).append(pattern)
            except:
                print("Ошибка при чтении с платы")
        elif choice == 'i':
            tmpl = import_level_template()
            if tmpl:
                level.update(tmpl)
        elif choice == 'd':
            try:
                idx = int(input("Номер паттерна для удаления: "))
                level['pattern_variants'].pop(idx)
            except:
                print("Ошибка удаления")
        elif choice == 'z':
            break


def run_editor():
    levels = load_levels()
    while True:
        print("\n=== УРОВНИ ===")
        for i, lvl in enumerate(levels):
            print(f"[{i+1}] {lvl['name']}")
        print("[N] Новый уровень")
        print("[I] Импорт уровня из файла")
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
        elif choice == 'i':
            lvl = import_level_template()
            if lvl: levels.append(lvl)
        elif choice == 's':
            save_levels(levels)
            break
        else:
            try:
                idx = int(choice)-1
                if 0 <= idx < len(levels): edit_level(levels[idx])
            except:
                print("Неверный выбор")


if __name__ == "__main__":
    run_editor()
