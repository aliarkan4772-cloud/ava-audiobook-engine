from flask import Flask, send_from_directory
from pathlib import Path
import re

app = Flask(__name__)
B = Path.home() / "ava-audiobook-engine"
CH = B / "recording/chapters"
REC = B / "recording/output"

HEAD = """<!DOCTYPE html><html lang=fa dir=rtl><head><meta charset=utf-8>
<meta name=viewport content='width=device-width,initial-scale=1'>
<title>کتاب صوتی مسخ</title>
<style>
body{background:#1a1a2e;color:#eee;font-family:Tahoma;padding:15px;padding-bottom:80px}
h1{color:#e94560;text-align:center}
summary{background:rgba(255,255,255,.08);padding:14px;border-radius:10px;margin:8px 0;font-size:1.1rem}
details[open] summary{background:#e94560}
audio{width:100%;margin:10px 0}
.t{font-size:1.3rem;line-height:2.3;text-align:justify;padding:12px}
.no{color:#888;font-size:.85rem;padding:8px}
.bar{position:fixed;bottom:0;left:0;right:0;background:#16213e;border-top:1px solid #e94560;padding:10px;display:flex;gap:8px;align-items:center;justify-content:center}
input[type=range]{width:140px}
</style></head><body>
<h1>📚 مسخ — متن + صدا</h1>
<div class=bar><label>سرعت پخش</label><input type=range id=sp min=50 max=200 value=100 oninput="ss(this.value)"><span id=sv>1x</span></div>
"""

TAIL = """<script>
function ss(v){document.getElementById('sv').textContent=(v/100)+'x';document.querySelectorAll('audio').forEach(a=>a.playbackRate=v/100)}
document.addEventListener('play',e=>{if(e.target.tagName=='AUDIO'){document.querySelectorAll('audio').forEach(x=>{if(x!=e.target)x.pause()});ss(document.getElementById('sp').value)}},true)
</script></body></html>"""

@app.route("/")
def index():
    texts = {}
    if CH.exists():
        for f in sorted(CH.glob("chapter_*.txt")):
            m = re.search(r"chapter_(\d+)", f.name)
            if m:
                lines = f.read_text(encoding="utf8").strip().split("\n")
                texts[int(m.group(1))] = "<br>".join(lines[1:])
    audio = {}
    if REC.exists():
        for f in sorted(REC.glob("chapter_*.mp3")):
            m = re.search(r"chapter_(\d+)", f.name)
            if m: audio[int(m.group(1))] = f.name
    parts = []
    for n in sorted(texts):
        if n in audio:
            player = f"<audio controls src='/audio/{audio[n]}'></audio>"
        else:
            player = "<p class=no>🎙️ هنوز ضبط نشده</p>"
        parts.append(f"<details><summary>فصل {n}</summary>{player}<div class=t>{texts[n]}</div></details>")
    body = "".join(parts) or "<p>چیزی پیدا نشد. اول بزن: record-book split</p>"
    return HEAD + body + TAIL

@app.route("/audio/<path:f>")
def au(f):
    return send_from_directory(REC, f)

if __name__ == "__main__":
    print("✅ اپ یکپارچه: http://127.0.0.1:8081")
    app.run(host="0.0.0.0", port=8081)
