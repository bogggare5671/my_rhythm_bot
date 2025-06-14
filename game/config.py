# Путь к файлу уровней и папке со звуками
LEVELS_PATH   = "/root/my_rhythm_bot/levels.json"
SOUND_FOLDER  = "/root/my_rhythm_bot/sounds"

# Настройки порта и скорости UART
SERIAL_PORT   = "/dev/ttyUSB0"
BAUDRATE      = 9600

# Таймаут ожидания ввода игрока, допуск тайминга, лимит сессии и пауза после уровня
TIMEOUT_SECONDS   = 20      # сек
TIMING_TOLERANCE  = 1.5     # ±150%
SESSION_LIMIT     = 300     # 5 минут
AFTER_LEVEL_PAUSE = 2       # сек
