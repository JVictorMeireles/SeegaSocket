import threading
import socket
import argparse
import os

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = []

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Servidor de chat ativo em {self.host}:{self.port}")

        while True:
            conn, addr = server_socket.accept()
            print(f"{addr} conectado.")

            # #Cria um novo thread
            # server_sock = ServerSocket(conn, addr, self)
            # #Inicia o thread
            # server_sock.start()
            # #Adiciona o thread à lista de threads
            # self.clients.append(server_sock)

            self.clients.append(conn)
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        while True:
            try:
                msg = conn.recv(1024).decode()
                if not msg: break
                print(f"{addr}: {msg}")
                self.broadcast(msg, conn)
            except:
                break
        conn.close()
        self.clients.remove(conn)

    def broadcast(self, msg, sender_conn):
        for client in self.clients:
            if client != sender_conn:
                client.send(msg.encode())

    # def remove_client(self, conn):
    #     if conn in self.clients:
    #         self.clients.remove(conn)
    #         conn.close()
    #         print(f"Cliente {conn} desconectado.")
    #     else:
    #         print(f"Cliente {conn} não encontrado na lista de clientes.")

    def close(self):
        for client in self.clients:
            client.close()
        print("Servidor fechado.")

# class ServerSocket(threading.Thread):
#     def __init__(self, conn, addr, server):
#         super().__init__()
#         self.conn = conn
#         self.addr = addr
#         self.server = server

#     def run(self):
#         while True:
#             try:
#                 msg = self.conn.recv(1024).decode()
#                 if not msg: break
#                 print(f"{self.addr}: {msg}")
#                 self.server.broadcast(msg, self.conn)
#             except:
#                 break
#         self.conn.close()
#         self.server.remove_client(self.conn)

#     def envia(self, msg):
#         try:
#             self.conn.send(msg.encode())
#         except:
#             print(f"Erro ao enviar mensagem para {self.addr}")
#             self.server.remove_client(self.conn)

def exit(servidor):
    servidor.close()
    os._exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de Chat")
    parser.add_argument("--host", type=str, default="localhost", help="Endereço do servidor")
    parser.add_argument("--port", type=int, default=5555, help="Porta do servidor")
    args = parser.parse_args()

    server = Server(args.host, args.port)
    server.start()

    exit = threading.Thread(target=exit, args=(server,))
    exit.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        sair(server)