from flask import Flask
from flask_sock import Sock
import socket

app = Flask(__name__)
sock = Sock(app)

@app.route('/')
def index():
    return 'Use /protocol/ip/port to connect to a TCP or UDP over WebSockets.'

@sock.route('/tcp/<ip>/<int:port>')
def tcp(sock,ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    while True:
        data = s.recv(1024)
        if not data:
            break
        sock.send(data)
    s.close()
    sock.close()

@sock.route('/udp/<ip>/<int:port>')
def udp(sock,ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    while True:
        data, addr = s.recvfrom(1024)
        if not data:
            break
        sock.send(data)
    s.close()
    sock.close()

if __name__ == '__main__':
    app.run()