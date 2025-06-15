# tests/test_audio.py

import os
import sys
import time
import wave
import struct
import math
import subprocess
import random

# Добавляем корень проекта в sys.path для корректного импорта game
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

from game.audio import play_sound


def generate_tone(path, frequency=440, duration=1.0, framerate=44100, amplitude=32767):
    """
    Generate a sine wave tone and save to the given path as a WAV file.
    """
    nframes = int(framerate * duration)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for i in range(nframes):
            sample = int(amplitude * math.sin(2 * math.pi * frequency * i / framerate))
            wf.writeframes(struct.pack('<h', sample))


def get_duration(path):
    """
    Получить длительность WAV-файла в секундах; для MP3 возвращает 1.0 сек.
    """
    if path.lower().endswith('.wav'):
        try:
            with wave.open(path, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                return frames / float(rate)
        except wave.Error:
            return 1.0
    return 1.0


if __name__ == '__main__':
    # --- Выбор случайного фонового трека ---
    fon_dir = os.path.join(BASE_DIR, 'fon')
    bg_files = [f for f in os.listdir(fon_dir) if f.lower().endswith(('.wav', '.mp3'))]
    if bg_files:
        bg_choice = random.choice(bg_files)
        music_path = os.path.join(fon_dir, bg_choice)
        try:
            bg_proc = subprocess.Popen(
                ['mpg123', '-q', '--loop', '0', music_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            print(f"🎵 Фоновая музыка запущена: {bg_choice}")
        except FileNotFoundError:
            print("⚠️ mpg123 не найден, пропускаем фоновую музыку")
    else:
        print(f"⚠️ В папке fon нет аудиофайлов: {fon_dir}")

    try:
        # --- Тест: генерируем тон и проигрываем ---
        print("▶ Generating 1-second sine tone at 440Hz...")
        tone_path = os.path.join('/tmp', 'tone440.wav')
        generate_tone(tone_path)
        print(f"✓ Tone generated at {tone_path}")

        print("▶ Playing generated tone...")
        play_sound(tone_path)
        time.sleep(get_duration(tone_path) + 1)

        # --- Тестируем существующие звуковые файлы ---
        sounds_dir = os.path.join(BASE_DIR, 'sounds')
        print(f"▶ Testing existing sound files in {sounds_dir}")

        if not os.path.isdir(sounds_dir):
            print(f"⚠️ Sounds directory not found: {sounds_dir}")
        else:
            for snd in os.listdir(sounds_dir):
                if snd.lower().endswith(('.wav', '.mp3')):
                    path = os.path.join(sounds_dir, snd)
                    print(f"▶ Playing {snd}...")
                    try:
                        play_sound(path)
                        duration = get_duration(path)
                        time.sleep(duration + 1)
                    except Exception as e:
                        print(f"❌ Error playing {snd}: {e}")
    finally:
        # --- Остановка фоновой музыки ---
        try:
            bg_proc.terminate()
            print("🛑 Фоновая музыка остановлена")
        except NameError:
            pass

    print("✅ Audio test complete")
