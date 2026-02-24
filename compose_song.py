import numpy as np
import wave
import struct
import time

def generate_piano_note(freq, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Basic sine wave with harmonics for a more complex "piano-like" tone
    tone = np.sin(2 * np.pi * freq * t) * 0.5
    tone += np.sin(2 * np.pi * (freq * 2) * t) * 0.25
    tone += np.sin(2 * np.pi * (freq * 3) * t) * 0.125
    
    # Exponential decay to sound like a plucked/hit string
    decay = np.exp(-3 * t / duration)
    return tone * decay

def create_melody():
    sample_rate = 44100
    # Frequencies for a simple C Major melody
    notes = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25
    }
    
    # Simple melody pattern (Twinkle Twinkle style)
    melody_sequence = ['C4', 'C4', 'G4', 'G4', 'A4', 'A4', 'G4', 'F4', 'F4', 'E4', 'E4', 'D4', 'D4', 'C4']
    note_duration = 0.5 # seconds
    
    full_audio = np.array([])
    
    print("Synthesizing notes...")
    for note in melody_sequence:
        note_audio = generate_piano_note(notes[note], note_duration, sample_rate)
        full_audio = np.concatenate((full_audio, note_audio))
    
    # Normalize to 16-bit PCM range
    full_audio = (full_audio * 32767).astype(np.int16)
    
    timestamp = int(time.time())
    filename = f"/home/claw/.openclaw/workspace/aria-lullaby-{timestamp}.wav"
    
    print(f"Saving to {filename}...")
    with wave.open(filename, 'w') as f:
        f.setnchannels(1) # Mono
        f.setsampwidth(2) # 2 bytes per sample
        f.setframerate(sample_rate)
        for sample in full_audio:
            f.writeframes(struct.pack('h', sample))
            
    print(f"MEDIA:{filename}")
    return filename

if __name__ == "__main__":
    create_melody()
