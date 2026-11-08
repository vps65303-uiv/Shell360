sudo bash -c 'cat << "EOF" > /etc/systemd/system/myscript.service
[Unit]
Description=My Background Python Script Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/bin/bash -c "while true; do python3 /usr/local/bin/myscript.py; sleep 5; done"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable myscript.service
sudo systemctl start myscript.service
