import socket
import subprocess
import os

def run_server():
    # إنشاء سوكيت TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # الاستماع محلياً على البورت 8443
    server.bind(('0.0.0.0', 8443))
    server.listen(1)
    print("[*] Jetson Server is waiting for connection on port 8443...")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Connection accepted from {addr}")
        
        while True:
            # استقبال الأمر من هاتفك
            command = client_socket.recv(1024).decode('utf-8')
            if not command or command.lower() == 'exit':
                break
            
            # تنفيذ الأمر على نظام الـ Jetson
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            except Exception as e:
                output = str(e).encode('utf-8')
            
            # إرسال النتيجة العائدة إلى هاتفك
            client_socket.sendall(output)
        
        client_socket.close()

if __name__ == '__main__':
    run_server()
