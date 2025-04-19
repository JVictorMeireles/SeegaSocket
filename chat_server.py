import socket
import threading

clients = []

def handle_client(conn, addr):
    print(f"{addr} conectado.")
    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg: break
            print(f"{addr}: {msg}")
            broadcast(msg, conn)
        except:
            break
    conn.close()
    clients.remove(conn)

def broadcast(msg, sender_conn):
    for client in clients:
        if client != sender_conn:
            client.send(msg.encode())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5555))
server.listen()

print("Servidor de chat ativo em localhost:5555")
while True:
    conn, addr = server.accept()
    clients.append(conn)
    threading.Thread(target=handle_client, args=(conn, addr)).start()
