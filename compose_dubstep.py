import numpy as np
import wave
import struct
import time
import random

def get_sine(freq, duration, sample_rate=44100, amp=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return amp * np.sin(2 * np.pi * freq * t)

def get_saw(freq, duration, sample_rate=44100, amp=0.5):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return amp * (2 * (t * freq - np.floor(0.5 + t * freq)))

def get_noise(duration, sample_rate=44100, amp=0.5):
    return amp * (np.random.rand(int(sample_rate * duration)) * 2 - 1)

def get_kick(duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Frequency sweep from 150 to 30 Hz
    freq_sweep = 150 * np.exp(-30 * t) + 30
    phase = 2 * np.pi * np.cumsum(freq_sweep) / sample_rate
    env = np.exp(-10 * t)
    return np.sin(phase) * env

def get_snare(duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    noise = get_noise(duration, sample_rate, amp=0.4)
    env = np.exp(-15 * t)
    return noise * env

def get_wobble(freq, duration, lfo_freq, sample_rate=44100, amp=0.6):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Carrier saw wave
    wave = get_saw(freq, duration, sample_rate, amp)
    # LFO for volume/filter simulation
    lfo = (np.sin(2 * np.pi * lfo_freq * t) + 1) / 2
    return wave * lfo

def create_dubstep():
    sr = 44100
    bpm = 140
    beat_dur = 60 / bpm
    bar_dur = beat_dur * 4
    
    total_sec = 180 # 3 minutes
    full_audio = np.array([], dtype=np.float32)
    
    print("Generating 3-minute Dubstep track...")
    
    sections = [
        {"type": "intro", "dur": 16, "wobble": False, "drums": False},
        {"type": "verse", "dur": 32, "wobble": False, "drums": True},
        {"type": "buildup", "dur": 16, "wobble": False, "drums": "fast"},
        {"type": "drop", "dur": 32, "wobble": True, "drums": True},
        {"type": "bridge", "dur": 16, "wobble": False, "drums": False},
        {"type": "buildup", "dur": 16, "wobble": False, "drums": "fast"},
        {"type": "drop", "dur": 36, "wobble": True, "drums": True},
        {"type": "outro", "dur": 16, "wobble": False, "drums": False},
    ]

    for sec in sections:
        sec_samples = int(sec["dur"] * sr)
        buffer = np.zeros(sec_samples, dtype=np.float32)
        
        # Add Drums
        if sec["drums"]:
            step = beat_dur if sec["drums"] == True else beat_dur / 4
            for t_off in np.arange(0, sec["dur"], step):
                idx = int(t_off * sr)
                # Kick on 1 and 3
                if int(round(t_off / beat_dur)) % 4 == 0:
                    k = get_kick(0.3, sr)
                    end = min(idx + len(k), len(buffer))
                    buffer[idx:end] += k[:end-idx] * 0.8
                # Snare on 2 and 4
                if int(round(t_off / beat_dur)) % 4 == 2:
                    s = get_snare(0.2, sr)
                    end = min(idx + len(s), len(buffer))
                    buffer[idx:end] += s[:end-idx] * 0.6
        
        # Add Bass/Melody
        if sec["wobble"]:
            for t_off in np.arange(0, sec["dur"], bar_dur):
                idx = int(t_off * sr)
                # Alternate LFO speed
                lfo = 4 if (t_off % (bar_dur*2) == 0) else 8
                w = get_wobble(55, bar_dur, lfo, sr, amp=0.5) # A1 note
                if idx+len(w) < len(buffer):
                    buffer[idx:idx+len(w)] += w
        else:
            # Simple lead melody for other sections
            melody = [440, 392, 349, 329] # A4, G4, F4, E4
            for i, t_off in enumerate(np.arange(0, sec["dur"], beat_dur)):
                idx = int(t_off * sr)
                note = melody[i % len(melody)]
                s = get_sine(note, beat_dur*0.8, sr, amp=0.2)
                if idx+len(s) < len(buffer):
                    buffer[idx:idx+len(s)] += s * np.exp(-2 * np.linspace(0, 1, len(s)))

        full_audio = np.concatenate((full_audio, buffer))

    # Master Limiter / Normalization
    full_audio = np.clip(full_audio, -1, 1)
    full_audio = (full_audio * 32767).astype(np.int16)
    
    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/aria-dubstep-{timestamp}.wav"
    
    print(f"Saving to {filename}...")
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(full_audio.tobytes())
            
    print(f"MEDIA:{filename}")
    return filename

if __name__ == "__main__":
    create_dubstep()
