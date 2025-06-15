import subprocess
from game.audio_manager import start_background_silence, stop_background_silence
from game.engine import run_game

if __name__ == "__main__":
    # Автоматическая компиляция и загрузка скетча перед стартом
    print("[DEPLOY] Запускаем deploy.sh...")
    result = subprocess.run(["/bin/bash", "deploy.sh"])
    if result.returncode != 0:
        print("[DEPLOY] ❌ Не удалось загрузить скетч, выход.")
        exit(1)
    # Запускаем фоновый поток тишины
    start_background_silence()
    try:
        # Основной игровой цикл
        run_game()
    except KeyboardInterrupt:
        # Обрабатываем Ctrl+C, чтобы выйти чисто
        print("\n[INFO] Interrupted by user, shutting down...")
    finally:
        # Останавливаем фоновый процесс тишины
        stop_background_silence()