#!/bin/bash
set -e

echo "=== 1. فحص وإنشاء ملف Swap بحجم 4GB ==="
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "تمت إضافه 4GB Swap بنجاح."
else
    echo "ملف Swap موجود مسبقاً."
fi

echo "=== 2. تحديث الحزم وتثبيت المتطلبات الأساسية و LXDE و TigerVNC و Docker ==="
sudo apt update
sudo apt install -y curl wget apt-transport-https ca-certificates gnupg lsb-release

# تثبيت LXDE إذا لم يكن مثبتًا
if ! dpkg -l | grep -q lxde-core; then
    echo "جارٍ تثبيت واجهة LXDE الخفيفة..."
    sudo apt install -y lxde-core
fi

# تثبيت TigerVNC إذا لم يكن مثبتًا
if ! command -v vncserver &> /dev/null; then
    echo "جارٍ تثبيت خادم VNC..."
    sudo apt install -y tigervnc-standalone-server
fi

# تثبيت Docker إذا لم يكن مثبتًا
if ! command -v docker &> /dev/null; then
    echo "جارٍ تثبيت Docker..."
    sudo apt install -y docker.io
    sudo systemctl enable --now docker
else
    sudo systemctl enable --now docker
fi

# تثبيت Google Chrome لمعمارية ARM64 إذا لم يكن مثبتًا
if ! command -v google-chrome &> /dev/null; then
    echo "جارٍ تحميل وتثبيت Google Chrome لـ ARM64..."
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_arm64.deb -O /tmp/chrome.deb || true
    if [ -f /tmp/chrome.deb ]; then
        sudo dpkg -i /tmp/chrome.deb || sudo apt-get install -f -y
        rm -f /tmp/chrome.deb
    fi
fi

echo "=== 3. إعداد كلمة مرور الـ VNC وبيئة العمل ==="
mkdir -p ~/.vnc
if [ ! -f ~/.vnc/passwd ]; then
    echo "يرجى إدخال كلمة مرور جديدة للـ VNC (سوف تحتاجها للدخول من هاتفك):"
    vncpasswd
fi

cat << 'EOF' > ~/.vnc/xstartup
#!/bin/sh
xrdb $HOME/.Xresources
startlxde &
EOF
chmod +x ~/.vnc/xstartup

echo "=== 4. إنشاء خدمة تشغيل VNC تلقائياً عند الإقلاع ==="
USER_NAME=$(whoami)
sudo bash -c "cat << EOF > /etc/systemd/system/vncserver.service
[Unit]
Description=Automated VNC Server Startup
After=network.target

[Service]
Type=forking
User=$USER_NAME
ExecStart=/usr/bin/vncserver :1 -geometry 1280x720 -depth 24
ExecStop=/usr/bin/vncserver -kill :1

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable vncserver.service

echo "=== 5. إنشاء خدمة طباعة Tailscale IP عند الإقلاع ==="
sudo bash -c "cat << 'EOF' > /usr/local/bin/show-ip.sh
#!/bin/bash
sleep 10
TS_IP=\$(tailscale ip -4 2>/dev/null || echo 'Tailscale Not Connected')
echo '==========================================='
echo '   Orange Pi 5 Ready for Connection!'
echo \"   Tailscale IP: \$TS_IP\"
echo \"   VNC Address : \$TS_IP:5901\"
echo '==========================================='
EOF"
sudo chmod +x /usr/local/bin/show-ip.sh

sudo bash -c "cat << 'EOF' > /etc/systemd/system/vnc-notify.service
[Unit]
Description=Show Tailscale and VNC IP on Startup
After=network.target tailscaled.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/show-ip.sh
StandardOutput=journal

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable vnc-notify.service

echo "=== 6. تشغيل الـ VNC الآن ==="
# إيقاف أي جلسة قديمة إن وجدت ثم تشغيل الجديدة
vncserver -kill :1 2>/dev/null || true
vncserver :1 -geometry 1280x720 -depth 24

echo "================================================="
echo " تم فحص، تثبيت، وإعداد كل شيء بنجاح يا محمد!"
echo " يمكنك الآن الاتصال عبر تطبيق الـ VNC باستخدام:"
echo " [Tailscale_IP]:5901"
echo "================================================="
