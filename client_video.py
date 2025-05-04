import threading
import socket
import argparse
import os
import sys
import tkinter as tk


class Send(threading.Thread):
  #listens for user input from cmd
  #sock the connected sock object
  #name (str): the username provided by the user

  def __init__(self, sock, name):
    super().__init__()
    self.sock = sock
    self.name = name

  def run(self):
    #listen for user input from the cmd and send it to the server
    #typing "Quit" will close the connection and exit the program
    while True:
      print("{}: ",format(self.name), end="")
      sys.stdout.flush()
      message = sys.stdin.readline()[:-1]
      # if we type "QUIT" we leave the chatroom
      if message == "QUIT":
        self.sock.sendall('Server: {} has left the chatroom'.format(self.name).encode('ascii'))
        break
      else:
        #send the message to the server
        self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))
    print("Quitting chatroom")
    self.sock.close()
    os.exit(0)

class Receive(threading.Thread):
  #listens for messages from the server
  #sock the connected sock object
  #name (str): the username provided by the user

  def __init__(self, sock, name):
    super().__init__()
    self.sock = sock
    self.name = name
    self.messages = None

  def run(self):
    #listen for messages from the server and print them to the cmd
    while True:
      message = self.sock.recv(1024).decode('ascii')
      if message:
        if self.messages:
          self.messages.insert(tk.END, message)
          print("hi")
          print("\r{}\n{}:".format(message, self.name), end="")
          self.messages.see(tk.END)
        else:
          print("\r{}\n{}:".format(message, self.name), end="")
      else:
        print("\n Lost connection to server")
        print("Quitting chatroom")
        self.sock.close()
        os.exit(0)

class Client:
  #management of client-server connection and integration of GUI
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.name = None
    self.messages = None

  def start(self):
    print("Trying to connect to {}:{}".format(self.host, self.port))
    self.sock.connect((self.host, self.port))
    print("Successfully connected to {}:{}".format(self.host, self.port))
    print()
    self.name = input("Your name: ")
    print()
    print("Welcome to the chatroom, {}!".format(self.name))
    print()

    #create a send and recieve threads
    send = Send(self.sock, self.name)
    receive = Receive(self.sock, self.name)

    send.start()
    receive.start()

    self.sock.sendall('Server: {} has joined the chatroom'.format(self.name).encode('ascii'))
    print("Ready! Type 'QUIT' to leave the chatroom")
    print("{}: ".format(self.name), end="")

    return receive

  def send(self, textInput):
    #sends textInput data from the GUI
    message = textInput.get()
    textInput.delete(0, tk.END)
    self.messages.insert(tk.END, '{}: {}'.format(self.name, message))

    #type "QUIT" to leave the chatroom
    if message == "QUIT":
      self.sock.sendall('Server: {} has left the chatroom'.format(self.name).encode('ascii'))
      print("Quitting chatroom")
      self.sock.close()
      os.exit(0)
    #send message to the server for broadcasting
    else:
      self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

def main(host, port):
  #initializes and run the GUI application
  client = Client(host, port)
  receive = client.start()

  window = tk.Tk()
  window.title("Chatroom")

  fromMessage = tk.Frame(master=window)
  scrollbar = tk.Scrollbar(master=fromMessage)
  messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollbar.set)
  scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
  messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

  client.messages = messages
  receive.messages = messages

  fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
  fromEntry = tk.Frame(master=window)
  textInput = tk.Entry(master=fromEntry)

  textInput.pack(fill=tk.BOTH, expand=True)
  textInput.bind("<Return>", lambda x: client.send(textInput))
  textInput.insert(0, "Type your message here.")

  btnSend = tk.Button(master=fromEntry, text="Send", command=lambda: client.send(textInput))

  fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
  btnSend.grid(row=1, column=1, pady=10, sticky="ew")

  window.rowconfigure(0, minsize=500, weight=1)
  window.rowconfigure(1, minsize=50, weight=0)
  window.columnconfigure(0, minsize=500, weight=1)
  window.columnconfigure(1, minsize=200, weight=0)

  window.mainloop()

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Chatroom Server")
  parser.add_argument("host", help="Interface the server listens to")
  parser.add_argument("-p", metavar='PORT', type=int, default=1060, help="TCP port (default: 1060)")

  args = parser.parse_args()

  main(args.host, args.p)