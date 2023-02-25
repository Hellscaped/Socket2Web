from flask import Flask,request
from flask_sock import Sock
import socket
import threading
import simple_websocket
app = Flask(__name__)
sock = Sock(app)

@app.route('/')
def index():
    return 'Use /protocol/host/port to connect to a TCP or UDP over WebSockets.'

@sock.route('/tcp/<ip>/<int:port>')
def tcp(ws,ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = True
    s.connect((ip, port))
    print('Connected to {}:{} from {}:{}.'.format(ip, port, request.headers.get('X-Forwarded-For', request.remote_addr), request.headers.get('X-Forwarded-Port', request.environ['REMOTE_PORT'])))
    def send(s,ws):
        print("Sending circuit opened.")
        while True:
            try:
                data = s.recv(1024)
                if not data:
                    break
                ws.send(data.decode())
            except simple_websocket.ws.ConnectionClosed:
                connected = False
                break
    def recv(s,ws):
        print("Receiving circuit opened.")
        while True:
            try:
                data = ws.receive()
                if not data:
                    break
                s.send(data.encode())
            except simple_websocket.ws.ConnectionClosed:
                connected = False
                break
    threading.Thread(target=send, args=(s,ws)).start()
    threading.Thread(target=recv, args=(s,ws)).start()

    while connected:
        pass

    print('Disconnected from {}:{} from {}:{}.'.format(ip, port, request.headers.get('X-Forwarded-For', request.remote_addr), request.headers.get('X-Forwarded-Port', request.environ['REMOTE_PORT'])))
    s.close()

@sock.route('/udp/<ip>/<int:port>')
def udp(ws,ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connected = True
    print('Connected to {}:{} from {}:{}.'.format(ip, port, request.headers.get('X-Forwarded-For', request.remote_addr), request.headers.get('X-Forwarded-Port', request.environ['REMOTE_PORT'])))
    def send(s,ws):
        print("Sending circuit opened.")
        while True:
            try:
                data, addr = s.recvfrom(1024)
                if not data:
                    break
                ws.send(data.decode())
            except simple_websocket.ws.ConnectionClosed:
                connected = False
                break
    def recv(s,ws):
        print("Receiving circuit opened.")
        while True:
            try:
                data = ws.receive()
                if not data:
                    break
                s.sendto(data.encode(), (ip, port))
            except simple_websocket.ws.ConnectionClosed:
                connected = False
                break
    threading.Thread(target=send, args=(s,ws)).start()
    threading.Thread(target=recv, args=(s,ws)).start()

    while connected:
        pass

    print('Disconnected from {}:{} from {}:{}.'.format(ip, port, request.headers.get('X-Forwarded-For', request.remote_addr), request.headers.get('X-Forwarded-Port', request.environ['REMOTE_PORT'])))
    s.close()

if __name__ == '__main__':
    app.run(port=6900)