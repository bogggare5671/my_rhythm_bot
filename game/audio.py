# game/audio.py

import os
import subprocess
from .config import SOUND_FOLDER

def play_sound(filename: str):
    """
    Проигрывает WAV-файл через aplay, тихо, без вывода в консоль.
    """
    path = os.path.join(SOUND_FOLDER, filename)
    subprocess.Popen(
        ["aplay", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
