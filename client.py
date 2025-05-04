import threading
import socket
import argparse
import os
import sys
import tkinter


class Send(threading.Thread):
    def __init__(self, sock, host, port):
        super().__init__()
        self.sock = sock
        self.host = host
        self.port = port
        self.root = tkinter.Tk()
        self.root.title("Chat Client")
        self.root.geometry("400x300")
        self.text_area = tkinter.Text(self.root)
        self.text_area.pack(expand=True, fill=tkinter.BOTH)
        self.entry = tkinter.Entry(self.root)
        self.entry.pack(fill=tkinter.X)
        self.entry.bind("<Return>", self.send_message)

    def run(self):
        while True:
            message = self.sock.recv(1024).decode('utf-8')
            if not message:
                break
            self.text_area.insert(tkinter.END, f"Server: {message}\n")
            self.text_area.see(tkinter.END)
        self.sock.close()
        os.exit(0)

class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        while True:
            message = self.sock.recv(1024).decode('ascii')
            if message:
                if self.messages:
                    self.messages.insert(tkinter.END, message)
                    print("\r{}\n{}:".format(message, self.name), end="")
                    self.messages.see(tkinter.END)
                else:
                    print(message)
            else:
                break
        self.sock.close()
        os.exit(0)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

    def start(self):
        self.name = input("Your name: ")
        print(f"Welcome to the chatroom, {self.name}!")

        # Create and start the send and receive threads
        send_thread = Send(self.sock, self.host, self.port)
        receive_thread = Receive(self.sock, self.name)
        send_thread.start()
        receive_thread.start()

        # Start the GUI main loop
        send_thread.root.mainloop()

    def send_message(self, event):
        message = self.entry.get()
        if message:
            self.sock.sendall(message.encode('utf-8'))
            self.entry.delete(0, tkinter.END)
            self.text_area.insert(tkinter.END, f"You: {message}\n")
            self.text_area.see(tkinter.END)
        else:
            print("Message cannot be empty")
        self.sock.close()
        os.exit(0)

    def main(host, port):
        client = Client(host, port)
        client.start()