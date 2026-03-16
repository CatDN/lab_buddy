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

def play_chime():
    def note(freq, duration, volume=0.3, detune=0.0):
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
        # slight detune on second harmonic gives a metallic shimmer
        wave = (
            np.sin(2 * np.pi * freq * t) * 0.5 +
            np.sin(2 * np.pi * freq * 2.756 * t + detune) * 0.3 +  # inharmonic partial
            np.sin(2 * np.pi * freq * 5.404 * t) * 0.1 +           # inharmonic partial
            np.sin(2 * np.pi * freq * 0.5 * t) * 0.1               # sub tone
        )
        n = len(t)
        # very fast attack, long slow exponential decay like a real chime
        attack  = min(int(SAMPLE_RATE * 0.003), n // 4)
        release = min(int(SAMPLE_RATE * duration * 0.85), n - attack)
        envelope = np.ones(n)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:attack + release] = np.exp(
            np.linspace(0, -4, release)
        )
        envelope[attack + release:] = 0
        return (wave * envelope * volume).astype(np.float32)

    # pentatonic windchime notes — randomly ordered like real wind chimes
    chime_notes = [
        (391.9, 1.1, 0.22),   # G4
        (440.0, 0.7, 0.25),   # A4
        (523.3, 0.9, 0.28),   # C5  — peak
        (659.3, 0.85, 0.18),  # E5
    ]

    selected = chime_notes

    # overlap notes slightly like a real windchime
    overlap = int(SAMPLE_RATE * 0.35)
    total_length = sum(int(SAMPLE_RATE * dur) for _, dur, _ in selected)
    full_wave = np.zeros(total_length + SAMPLE_RATE, dtype=np.float32)

    pos = 0
    for freq, duration, volume in selected:
        n = note(freq, duration, volume, detune=0.05)
        end = pos + len(n)
        if end > len(full_wave):
            full_wave = np.pad(full_wave, (0, end - len(full_wave)))
        full_wave[pos:end] += n
        pos += len(n) - overlap

    # normalise to avoid clipping
    max_val = np.max(np.abs(full_wave))
    if max_val > 0:
        full_wave = full_wave / max_val * 0.6

    sd.play(full_wave, SAMPLE_RATE)
    sd.wait()

if __name__ == "__main__":
    # play_alarm()
    play_chime()