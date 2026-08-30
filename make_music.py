#!/usr/bin/env python3
"""ساخت موسیقی پس‌زمینه ملایم برای کتاب صوتی"""
import numpy as np
import wave
import struct

SAMPLE_RATE = 44100

def generate_tone(freq, duration, volume=0.3):
    """تولید یه نت با فرکانس مشخص"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(2 * np.pi * freq * t) * volume
    # اضافه کردن fade in/out برای نرمی
    fade = int(SAMPLE_RATE * 0.5)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)
    return tone

def generate_ambient(duration=60):
    """ساخت موسیقی ambient ملایم"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    
    # لایه ۱: پد نرم پایه
    pad = np.sin(2 * np.pi * 110 * t) * 0.1
    pad += np.sin(2 * np.pi * 165 * t) * 0.08
    pad += np.sin(2 * np.pi * 220 * t) * 0.05
    
    # لایه ۲: ملودی آرام با نت‌های پنتاتونیک
    melody = np.zeros_like(t)
    notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]  # C D E G A C
    
    np.random.seed(42)
    note_duration = 4  # هر نت ۴ ثانیه
    for i in range(0, duration, note_duration):
        freq = np.random.choice(notes)
        start = int(i * SAMPLE_RATE)
        end = min(int((i + note_duration) * SAMPLE_RATE), len(t))
        note_t = np.linspace(0, note_duration, end - start, False)
        note = np.sin(2 * np.pi * freq * note_t) * 0.15
        # fade
        fade = int(SAMPLE_RATE * 1)
        note[:fade] *= np.linspace(0, 1, fade)
        note[-fade:] *= np.linspace(1, 0, fade)
        melody[start:end] += note
    
    # ترکیب
    audio = pad + melody
    
    # نرمال‌سازی
    audio = audio / np.max(np.abs(audio)) * 0.5
    
    return audio

def save_wav(filename, audio):
    """ذخیره به فایل wav"""
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for sample in audio:
            wav.writeframes(struct.pack('<h', int(sample * 32767)))

print("🎵 ساخت موسیقی پس‌زمینه...")
ambient = generate_ambient(120)  # ۲ دقیقه
save_wav('music/background.wav', ambient)
print("✅ music/background.wav ساخته شد")

# تبدیل به mp3
import subprocess
subprocess.run(['ffmpeg', '-y', '-i', 'music/background.wav', '-b:a', '128k', 'music/background.mp3'], 
               capture_output=True)
print("✅ music/background.mp3 ساخته شد")
