# tests/test_audio.py

import time
from game.audio import play_sound

if __name__ == '__main__':
    print("▶ Generating 1 second tone (sine 440Hz)...")
    # Если у вас нет готового WAV, сгенерируйте тестовый тон:
    import wave, struct, math

    fname = '/tmp/tone440.wav'
    framerate = 44100
    duration  = 1.0
    amplitude = 32767
    nframes   = int(framerate * duration)
    with wave.open(fname, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        for i in range(nframes):
            sample = int(amplitude * math.sin(2*math.pi*440 * i/framerate))
            wf.writeframes(struct.pack('<h', sample))

    # проигрываем тестовый тон
    play_sound(os.path.basename(fname))

    time.sleep(0.5)

    # а теперь несколько ваших файлов
    for snd in ['kick.wav', 'snare.wav', 'hihat.wav']:
        print(f"▶ Playing {snd}")
        play_sound(snd)
        time.sleep(0.2)

    print("✅ Audio test complete")
