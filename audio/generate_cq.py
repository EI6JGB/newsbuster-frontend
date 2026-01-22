"""Generate CQ CQ CQ morse code audio at 20 WPM"""
import numpy as np
from scipy.io import wavfile
import subprocess
import os

# Morse code mapping
MORSE = {
    'C': '-.-.',
    'Q': '--.-',
    ' ': ' '
}

# 20 WPM timing: 1 unit (dit) = 1200 / WPM = 60ms
WPM = 20
DIT_MS = 1200 / WPM  # 60ms
DAH_MS = DIT_MS * 3   # 180ms
SYMBOL_GAP_MS = DIT_MS  # 60ms (between dits/dahs)
LETTER_GAP_MS = DIT_MS * 3  # 180ms (between letters)
WORD_GAP_MS = DIT_MS * 7  # 420ms (between words)

# Audio settings
SAMPLE_RATE = 44100
FREQUENCY = 700  # Hz
VOLUME = 0.6

def generate_tone(duration_ms):
    """Generate a sine wave tone"""
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, samples, False)
    tone = np.sin(2 * np.pi * FREQUENCY * t) * VOLUME

    # Apply envelope to avoid clicks
    attack = int(SAMPLE_RATE * 0.005)  # 5ms attack
    release = int(SAMPLE_RATE * 0.005)  # 5ms release

    if len(tone) > attack + release:
        tone[:attack] *= np.linspace(0, 1, attack)
        tone[-release:] *= np.linspace(1, 0, release)

    return tone

def generate_silence(duration_ms):
    """Generate silence"""
    samples = int(SAMPLE_RATE * duration_ms / 1000)
    return np.zeros(samples)

def text_to_morse_audio(text):
    """Convert text to morse code audio"""
    audio = []

    for i, char in enumerate(text.upper()):
        if char == ' ':
            # Word gap (minus letter gap already added)
            audio.append(generate_silence(WORD_GAP_MS - LETTER_GAP_MS))
            continue

        morse = MORSE.get(char, '')
        for j, symbol in enumerate(morse):
            if symbol == '.':
                audio.append(generate_tone(DIT_MS))
            elif symbol == '-':
                audio.append(generate_tone(DAH_MS))

            # Symbol gap (between dits/dahs within a letter)
            if j < len(morse) - 1:
                audio.append(generate_silence(SYMBOL_GAP_MS))

        # Letter gap (between letters, not after last)
        if i < len(text) - 1 and text[i + 1] != ' ':
            audio.append(generate_silence(LETTER_GAP_MS))

    return np.concatenate(audio)

# Generate CQ CQ CQ
print("Generating CQ CQ CQ at 20 WPM...")
audio = text_to_morse_audio("CQ CQ CQ")

# Normalize to 16-bit range
audio_16bit = np.int16(audio * 32767)

# Save as WAV first
wav_path = "cq_morse.wav"
wavfile.write(wav_path, SAMPLE_RATE, audio_16bit)
print(f"Saved {wav_path}")

# Convert to MP3 using ffmpeg if available
mp3_path = "cq_morse.mp3"
try:
    subprocess.run([
        'ffmpeg', '-y', '-i', wav_path,
        '-codec:a', 'libmp3lame', '-qscale:a', '2',
        mp3_path
    ], check=True, capture_output=True)
    print(f"Saved {mp3_path}")
    os.remove(wav_path)
except (subprocess.CalledProcessError, FileNotFoundError):
    print("ffmpeg not found - keeping WAV file")
    print("You can convert manually or use the WAV file")

print("Done!")
