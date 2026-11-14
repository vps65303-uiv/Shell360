#!/bin/bash
set -e

echo "=========================================="
echo " تثبيت XFCE + XRDP + Audio + Tailscale"
echo "=========================================="

if [ "$(id -u)" -ne 0 ]; then
    echo "شغّل السكربت بصلاحيات root"
    exit 1
fi

# 1. تحديث النظام وتثبيت curl
apt update
DEBIAN_FRONTEND=noninteractive apt install -y curl

# 2. تثبيت سطح المكتب XFCE
DEBIAN_FRONTEND=noninteractive apt install -y \
    xfce4 \
    xfce4-goodies \
    dbus-x11 \
    xorg \
    xserver-xorg-core \
    xfonts-base

# 3. تثبيت XRDP
DEBIAN_FRONTEND=noninteractive apt install -y \
    xrdp \
    xorgxrdp \
    ssl-cert

# 4. تثبيت نظام الصوت
DEBIAN_FRONTEND=noninteractive apt install -y \
    pulseaudio \
    pulseaudio-utils \
    pavucontrol \
    alsa-utils

# 5. إعداد جلسة XFCE
cat > /etc/skel/.xsession <<'EOF'
#!/bin/sh
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
exec dbus-launch --exit-with-session startxfce4
EOF
chmod +x /etc/skel/.xsession

for home_dir in /home/* /root; do
    if [ -d "$home_dir" ]; then
        cat > "$home_dir/.xsession" <<'EOF'
#!/bin/sh
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
exec dbus-launch --exit-with-session startxfce4
EOF
        chmod +x "$home_dir/.xsession"
    fi
done

# 6. صلاحيات وتشغيل XRDP مباشرة
adduser xrdp ssl-cert || true
systemctl enable xrdp
systemctl enable xrdp-sesman
systemctl restart xrdp
systemctl restart xrdp-sesman

# 7. تثبيت وتشغيل Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
systemctl enable --now tailscaled || tailscaled --tun=userspace-networking &

echo "=========================================="
echo " تم تثبيت كل شيء بنجاح!"
echo "=========================================="
echo "لتفعيل شبكة Tailscale والحصول على الـ IP الخاص بك، نفذ الأمر التالي:"
echo "tailscale up"
