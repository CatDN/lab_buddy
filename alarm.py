# 14/03/2026

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100

def play_alarm(duration = 10):
    t= np.linspace(0, duration, int(SAMPLE_RATE*duration))

    # alternating between two frequencies for a siren effect
    wave = np.sin(2 * np.pi * 880 * t) * (np.sin(2 * np.pi * 2 * t) > 0) + \
           np.sin(2 * np.pi * 660 * t) * (np.sin(2 * np.pi * 2 * t) <= 0)
    wave = (wave * 0.5).astype(np.float32)
    sd.play(wave, SAMPLE_RATE)
    sd.wait()



if __name__ == "__main__":
    # play_alarm()
    play_chime()