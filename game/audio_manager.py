import subprocess
import atexit
from subprocess import DEVNULL

_silence_proc = None

def start_background_silence():
    """
    Запускает непрерывный поток тишины через ALSA с плагином dmix (default),
    чтобы избежать щелчков и позволить микшировать остальные звуки.
    """
    global _silence_proc
    if _silence_proc is None:
        _silence_proc = subprocess.Popen([
            "aplay", "-q",
            "-D", "default",         # использовать устройство default (dmix)
            "-r", "44100",           # частота дискретизации
            "-f", "S16_LE",          # формат PCM 16-bit little-endian
            "-c", "1",               # моно
            "-t", "raw",             # сырой PCM
            "/dev/zero"
        ], stdout=DEVNULL, stderr=DEVNULL)

def stop_background_silence():
    """
    Останавливает фоновый процесс тишины.
    """
    global _silence_proc
    if _silence_proc:
        _silence_proc.terminate()
        _silence_proc = None

# Гарантируем остановку при выходе программы
atexit.register(stop_background_silence)
