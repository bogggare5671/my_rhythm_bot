import os
import subprocess
from subprocess import DEVNULL

from .config import SOUND_FOLDER

def play_sound(filename: str):
    """
    Проигрывает звуковой файл из папки SOUND_FOLDER,
    дожидаясь его полного окончания (чтобы не обрезать и не было щелчков).
    """
    path = os.path.join(SOUND_FOLDER, filename)
    print(f"[Audio] Attempting to play: {path}")
    if not os.path.isfile(path):
        print(f"[Audio] ⚠️ File not found: {path}")
        return
    try:
        # Добавляем -D default, чтобы микширование с фоном работало
        ret = subprocess.run(
            ["aplay", "-q", "-D", "default", path],
            stdout=DEVNULL,
            stderr=DEVNULL
        )
        if ret.returncode != 0:
            print(f"[Audio] ⚠️ aplay returned {ret.returncode}")
    except Exception as e:
        print(f"[Audio] ❌ Error: {e}")
