from .serial_io import send_lcd
import time

# Карта UTF-8 → CP1251 для LiquidCrystal_I2C_Cyrillic
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

# Таблица «кириллица → латиница» для букв-«двойников»
ASCII_EQUIV = {
    'А': 'A','В': 'B','Е': 'E','К': 'K','М': 'M','Н': 'H',
    'О': 'O','Р': 'P','С': 'C','Т': 'T','Х': 'X',
    'а': 'a','в': 'b','е': 'e','к': 'k','м': 'm','н': 'h',
    'о': 'o','р': 'p','с': 'c','т': 't','х': 'x'
}


def rus_to_lcd(s: str) -> bytes:
    """
    Преобразует UTF-8 строку в байты:
     • RU_MAP → специальные коды (0x80–0xAE)
     • ASCII_EQUIV → латинские эквиваленты
     • остальные ASCII-символы без изменений
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


def lcd(text: str):
    """
    Отправляет на Arduino команду вида:
      LCD <payload>\n
    где payload — результат rus_to_lcd(text).
    Логирует в терминал.
    """
    # очистка экрана (обрабатывается на Arduino)
    send_lcd(b"LCD CLEAR\n")
    time.sleep(0.05)

    # подготовка и отправка текста
    payload = rus_to_lcd(text)
    cmd = b"LCD " + payload + b"\n"
    send_lcd(cmd)
    time.sleep(0.05)

    # лог в терминал
    print(f"[LCD] {text}")
