import socket
import threading
import tkinter as tk

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Seega")
        
        self.text_area = tk.Text(root, height=15, state='disabled')
        self.text_area.pack()

        self.entry = tk.Entry(root)
        self.entry.pack()
        self.entry.bind("<Return>", self.send_message)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 5555))

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event=None):
        msg = self.entry.get()
        self.client.send(msg.encode())
        self.entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, msg + '\n')
                self.text_area.config(state='disabled')
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    ChatClient(root)
    root.mainloop()
