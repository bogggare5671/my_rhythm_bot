import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))

LEVELS_PATH = os.path.join(ROOT_DIR, 'levels.json')
SOUND_FOLDER = os.path.join(ROOT_DIR, 'sounds')

SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

TIMEOUT_SECONDS = 10
TIMING_TOLERANCE = 1.5
SESSION_LIMIT = 300
AFTER_LEVEL_PAUSE = 2