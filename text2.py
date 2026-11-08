import os
import subprocess
import time

# المفاتيح الخاصة بك
TELEGRAM_TOKEN = "8508402230:AAGK5iP1fxc7Dscu5pDmqWkAGLCCYLtKrB0"
NGROK_TOKEN = "3L3e1ZwYliU5zCTToq5Ms4LL6qG_jSKSRVmPqoRJkt1LFNVX"
YOUR_TELEGRAM_ID = 8897834377

print(">>> [1/5] جاري تحديث الحزم وتثبيت واجهة LXDE وحزم VNC...")
subprocess.run("pip install -q pyngrok pyTelegramBotAPI psutil --break-system-packages", shell=True)
subprocess.run("export DEBIAN_FRONTEND=noninteractive && apt-get update -qq && apt-get install -y -qq tigervnc-standalone-server lxde-core lxde gtk2-engines-murrine wget curl tar bzip2 libdbus-glib-1-2 libgtk-3-0 x11-xserver-utils", shell=True)

print(">>> [2/5] جاري تحميل وتثبيت متصفح Firefox الرسمي المباشر...")
firefox_cmd = """
wget -O /tmp/firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US"
tar -xvf /tmp/firefox.tar.bz2 -C /opt/
ln -sf /opt/firefox/firefox /usr/bin/firefox
"""
subprocess.run(firefox_cmd, shell=True)

print(">>> [3/5] جاري إعداد وضبط خادم VNC...")
subprocess.run("pkill -f Xtigervnc; pkill -f ngrok; pkill -f python3", shell=True)

vnc_passwd_dir = os.path.expanduser("~/.vnc")
os.makedirs(vnc_passwd_dir, exist_ok=True)

# تشغيل أمر إعداد كلمة المرور بشكل تفاعلي يدوي لضمان عدم حدوث خطأ
print("--- يرجى إدخال كلمة مرور VNC الخاصة بك أدناه ---")
subprocess.run("vncpasswd", shell=True)

xstartup_content = """#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startlxde
"""
xstartup_path = os.path.join(vnc_passwd_dir, "xstartup")
with open(xstartup_path, "w") as f:
    f.write(xstartup_content)
subprocess.run(f"chmod +x {xstartup_path}", shell=True)

# تشغيل خادم VNC على الشاشة :1
subprocess.run("vncserver :1 -geometry 1280x720 -depth 24", shell=True)

print(">>> [4/5] إعداد نفق الاتصال الآمن عبر Ngrok...")
from pyngrok import ngrok
ngrok.set_auth_token(NGROK_TOKEN)

try:
    ngrok.kill()
except:
    pass

public_url = ngrok.connect(5901, "tcp")
tunnel_url_str = public_url.public_url if hasattr(public_url, 'public_url') else str(public_url).split('"')[1]
print(f">>> رابط الاتصال النظيف: {tunnel_url_str}")

print(">>> [5/5] كتابة وتشغيل بوت التيليجرام في الخلفية...")
bot_code = f"""
import telebot
import subprocess
import psutil
import os

TOKEN = "{TELEGRAM_TOKEN}"
ADMIN_ID = {YOUR_TELEGRAM_ID}
tunnel_url = "{tunnel_url_str}"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا محمد! نظام التحكم السحابي يعمل بكفاءة.\\nالأوامر المتاحة:\\n/status - معرفة استهلاك الموارد\\n/link - إظهار رابط VNC")

@bot.message_handler(commands=['status'])
def get_status(message):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    bot.reply_to(message, f"حالة السيرفر الحالي:\\n- المعالج (CPU): {{cpu}}%\\n- الذاكرة (RAM): {{memory}}%")

@bot.message_handler(commands=['link'])
def send_link(message):
    bot.reply_to(message, f"رابط الدخول عبر VNC:\\n{{tunnel_url}}")

try:
    bot.send_message(ADMIN_ID, f"🚀 تم تشغيل السيرفر وتثبيت متصفح Firefox بنجاح!\\nالرابط:\\n{{tunnel_url}}")
except Exception as e:
    print(f"تعذر إرسال التنبيه: {{e}}")

bot.infinity_polling(timeout=10, long_polling_timeout=5)
"""

with open("bot_run.py", "w") as f:
    f.write(bot_code)

subprocess.Popen(["python3", "bot_run.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

env = os.environ.copy()
env["DISPLAY"] = ":1"
subprocess.Popen(["firefox"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("\n==================================================")
print("🚀 تمت العملية بنجاح! تم تشغيل النظام ومتصفح فايرفوكس جاهز للاستخدام.")
print(f"🔗 رابط VNC الخاص بك: {tunnel_url_str}")
print("==================================================")
