from cgitb import text
import socket
from threading import Thread
import time
from tkinter import *

buf = 1024
PORT = 5050
format = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.133"
ADDR = (SERVER, PORT)

# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect(ADDR)
# ---------------------------------------------------------


def receive():
    while True:
        msg = client_socket.recv(buf).decode(format)
        msg_list.insert(END, msg)
        if msg == DISCONNECT_MESSAGE:
            msg_list.insert(END, "THE SERVER HAS CRASHED!!!")
            exitscene()
        if msg == "SEE YA":
            time.sleep(5)
            exitscene()

# --------------------------------------------------------------


def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    client_socket.send(bytes(msg, format))
# -----------------------------------------------------------------


def exitscene(event=None):
    client_socket.send(bytes(DISCONNECT_MESSAGE, format))
    scene.destroy()


# --------------------------------------------------------------------
scene = Tk()
scene.title("CLIENT TRANSACTION")
messages_frame = Frame(scene)
my_msg = StringVar()
scrollbar = Scrollbar(messages_frame)
msg_list = Listbox(messages_frame, height=30, width=100,
                   yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack()
messages_frame.pack()
entry_field = Entry(scene, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = Button(scene, text="Reply")
send_button.bind("<ButtonRelease-1>", send)
send_button.pack()
exit_button = Button(scene, text="Quit")
exit_button.bind("<ButtonRelease-1>", exitscene)
exit_button.pack()
# -------------------------------------------------------------------------------------

try:
    # le type du socket : SOCK_STREAM pour le protocole TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(ADDR)
    test = True
except:
    print("the server is offline")
    test = False
if test:
    receive_thread = Thread(target=receive)
    receive_thread.start()
    scene.mainloop()
