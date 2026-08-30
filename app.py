#!/usr/bin/env python3
from flask import Flask, send_from_directory
from pathlib import Path
import json
import re

app = Flask(__name__)

BASE_DIR = Path.home() / "ava-audiobook-engine"
RECORDING_DIR = BASE_DIR / "recording" / "output"
TTS_DIR = BASE_DIR / "audiobook_farsi_tts" / "rebuild_chunks"
MUSIC_DIR = BASE_DIR / "music"
RECORDING_DIR.mkdir(parents=True, exist_ok=True)
TTS_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

def get_chapters():
    chapters = []
    if RECORDING_DIR.exists():
        for file in sorted(RECORDING_DIR.glob("chapter_*.mp3")):
            match = re.search(r'chapter_(\d+)', file.name)
            if match:
                chapters.append({
                    'id': int(match.group(1)),
                    'title': f'فصل {match.group(1)}',
                    'file': f'recording/{file.name}',
                    'type': 'recorded'
                })
    if TTS_DIR.exists():
        for file in sorted(TTS_DIR.glob("chunk_*.mp3"))[:20]:
            match = re.search(r'chunk_(\d+)', file.name)
            if match:
                chapters.append({
                    'id': int(match.group(1)),
                    'title': f'بخش {match.group(1)}',
                    'file': f'tts/{file.name}',
                    'type': 'tts'
                })
    return chapters

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>کتاب صوتی مسخ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Tahoma, Arial; background: #1a1a2e; color: #eee; padding: 20px; padding-bottom: 100px; }
        h1 { text-align: center; color: #e94560; margin: 30px 0; }
        .chapter { background: rgba(255,255,255,0.05); padding: 15px; margin: 10px 0; border-radius: 10px; }
        .chapter.playing { background: rgba(233,69,96,0.2); border: 1px solid #e94560; }
        audio { width: 100%; margin-top: 10px; }
        .controls { position: fixed; bottom: 0; left: 0; right: 0; background: #16213e; padding: 15px; border-top: 1px solid #e94560; display: flex; gap: 10px; align-items: center; justify-content: center; flex-wrap: wrap; }
        .btn { background: #e94560; color: white; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 0.9rem; }
        .btn.off { background: #555; }
        .slider { width: 100px; }
        label { font-size: 0.8rem; color: #aaa; }
    </style>
</head>
<body>
    <h1>📚 کتاب صوتی مسخ</h1>
    <div id="chapters"></div>
    
    <div class="controls">
        <button class="btn" id="musicBtn" onclick="toggleMusic()">🎵 موسیقی: روشن</button>
        <label>بلندی موسیقی</label>
        <input type="range" class="slider" id="musicVol" min="0" max="100" value="30" oninput="setMusicVol(this.value)">
        <label>سرعت پخش</label>
        <input type="range" class="slider" id="speed" min="50" max="200" value="100" oninput="setSpeed(this.value)">
        <span id="speedVal">1x</span>
    </div>
    
    <audio id="bgMusic" loop></audio>
    
    <script>
        const bgMusic = document.getElementById('bgMusic');
        bgMusic.src = '/audio/music/background.mp3';
        bgMusic.volume = 0.3;
        let musicOn = true;
        let mainAudio = null;
        
        function toggleMusic() {
            musicOn = !musicOn;
            const btn = document.getElementById('musicBtn');
            if (musicOn) {
                btn.textContent = '🎵 موسیقی: روشن';
                btn.classList.remove('off');
                if (mainAudio && !mainAudio.paused) bgMusic.play();
            } else {
                btn.textContent = '🎵 موسیقی: خاموش';
                btn.classList.add('off');
                bgMusic.pause();
            }
        }
        
        function setMusicVol(v) { bgMusic.volume = v / 100; }
        function setSpeed(v) {
            document.getElementById('speedVal').textContent = (v/100) + 'x';
            if (mainAudio) mainAudio.playbackRate = v / 100;
        }
        
        fetch('/api/chapters')
            .then(r => r.json())
            .then(chapters => {
                const container = document.getElementById('chapters');
                if (chapters.length === 0) {
                    container.innerHTML = '<p style="text-align:center;color:#888">هنوز فصلی ضبط نشده</p>';
                    return;
                }
                chapters.forEach((ch, idx) => {
                    const div = document.createElement('div');
                    div.className = 'chapter';
                    div.id = 'ch-' + ch.id;
                    div.innerHTML = `
                        <strong>${ch.title}</strong>
                        <span style="font-size:0.8rem;color:#888;margin-right:10px">${ch.type === 'recorded' ? '🎙️' : '🤖'}</span>
                        <audio controls style="display:block;margin-top:10px" data-idx="${idx}">
                            <source src="/audio/${ch.file}" type="audio/mpeg">
                        </audio>
                    `;
                    container.appendChild(div);
                });
                
                // مدیریت پخش
                const audios = document.querySelectorAll('audio[data-idx]');
                audios.forEach((audio, idx) => {
                    audio.addEventListener('play', () => {
                        mainAudio = audio;
                        audio.playbackRate = document.getElementById('speed').value / 100;
                        // توقف بقیه
                        audios.forEach(a => { if (a !== audio) a.pause(); });
                        // پخش موسیقی پس‌زمینه
                        if (musicOn) bgMusic.play();
                        // علامت‌گذاری
                        document.querySelectorAll('.chapter').forEach(c => c.classList.remove('playing'));
                        audio.closest('.chapter').classList.add('playing');
                    });
                    audio.addEventListener('pause', () => {
                        bgMusic.pause();
                    });
                    // پخش خودکار فصل بعدی
                    audio.addEventListener('ended', () => {
                        const next = audios[idx + 1];
                        if (next) {
                            next.play();
                        } else {
                            bgMusic.pause();
                        }
                    });
                });
            });
    </script>
</body>
</html>'''

@app.route('/api/chapters')
def api_chapters():
    return json.dumps(get_chapters())

@app.route('/audio/<path:filename>')
def audio(filename):
    if filename.startswith('recording/'):
        return send_from_directory(RECORDING_DIR, filename.replace('recording/', ''))
    elif filename.startswith('music/'):
        return send_from_directory(MUSIC_DIR, filename.replace('music/', ''))
    else:
        return send_from_directory(TTS_DIR, filename.replace('tts/', ''))

if __name__ == '__main__':
    print("✅ اپ آماده است!")
    print("📱 توی مرورگر باز کن: http://127.0.0.1:8080")
    app.run(host='0.0.0.0', port=8080)
