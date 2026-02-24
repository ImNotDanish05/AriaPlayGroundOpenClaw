import numpy as np
import wave
import struct
import time
import random

def get_sine(freq, duration, sample_rate=44100, amp=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return amp * np.sin(2 * np.pi * freq * t)

def get_piano_note(freq, duration, sample_rate=44100, amp=0.4):
    if freq == 0: return np.zeros(int(sample_rate * duration))
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Sad piano: rich harmonics but soft high-end
    tone = np.sin(2 * np.pi * freq * t) * 0.6
    tone += np.sin(2 * np.pi * (freq * 2) * t) * 0.3
    tone += np.sin(2 * np.pi * (freq * 3) * t) * 0.1
    # Smooth attack and long release
    env = np.exp(-4 * t / duration)
    attack = np.minimum(1, t / 0.05) # 50ms attack
    return tone * env * attack * amp

def get_rain_ambient(duration, sample_rate=44100, amp=0.08):
    noise = np.random.rand(int(sample_rate * duration)) * 2 - 1
    # Simple low-pass filter simulation (muffled rain)
    filtered_noise = np.zeros_like(noise)
    alpha = 0.1
    for i in range(1, len(noise)):
        filtered_noise[i] = alpha * noise[i] + (1 - alpha) * filtered_noise[i-1]
    return filtered_noise * amp

def create_sad_piano():
    sr = 44100
    bpm = 65
    beat_dur = 60 / bpm
    total_sec = 120 # 2 minutes
    
    full_audio = np.zeros(int(total_sec * sr), dtype=np.float32)
    
    # Frequencies
    notes = {
        'F2': 87.31, 'G2': 98.00, 'A2': 110.00, 'C3': 130.81, 'E3': 164.81, 'G3': 196.00,
        'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66,
        'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00,
        'B4': 493.88, 'C5': 523.25, '0': 0
    }
    
    print("Generating sad piano with ambient rain...")
    
    # 1. Add Rain Ambient (Background layer)
    full_audio += get_rain_ambient(total_sec, sr)
    
    # 2. Composition (Slow A minor / D minor vibe)
    # 4 Voices: Bass, Chord L, Chord R, Melody
    chord_prog = [
        ['A2', 'C4', 'E4'], # Am
        ['F2', 'A3', 'C4'], # F
        ['C3', 'E4', 'G4'], # C
        ['G2', 'B3', 'D4'], # G
    ]
    
    melody = ['A4', '0', 'G4', 'E4', 'F4', 'E4', 'D4', 'C4']
    
    for bar in range(int(total_sec / (beat_dur * 4))):
        start_time = bar * (beat_dur * 4)
        chord = chord_prog[bar % len(chord_prog)]
        
        # Draw Chords/Bass (Voices 1, 2, 3)
        for i, note_name in enumerate(chord):
            n_freq = notes[note_name]
            note_audio = get_piano_note(n_freq, beat_dur * 4, sr, amp=0.15)
            idx = int(start_time * sr)
            end = min(idx + len(note_audio), len(full_audio))
            full_audio[idx:end] += note_audio[:end-idx]
            
        # Draw Melody (Voice 4)
        for step in range(4):
            m_note = melody[(bar * 4 + step) % len(melody)]
            if m_note != '0':
                m_freq = notes[m_note]
                m_audio = get_piano_note(m_freq, beat_dur, sr, amp=0.25)
                m_idx = int((start_time + step * beat_dur) * sr)
                m_end = min(m_idx + len(m_audio), len(full_audio))
                full_audio[m_idx:m_end] += m_audio[:m_end-m_idx]

    # Normalize
    full_audio = np.clip(full_audio, -1, 1)
    full_audio = (full_audio * 32767).astype(np.int16)
    
    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/aria-sad-piano-{timestamp}.wav"
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(full_audio.tobytes())
            
    print(f"MEDIA:{filename}")
    return filename

if __name__ == "__main__":
    create_sad_piano()
