from datetime import time
from optparse import Values
import os
import random
from secrets import choice
import socket
import threading
from tkinter import *
from tkinter.ttk import Treeview

buf = 1024
format = "utf8"
PORT = 5050
ref_compte = []
tester_conx = False
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '192.168.1.13'
bank_mutex = threading.Lock()

ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(ADDR)
# ---------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------


class gerer_clients(threading.Thread):
    testconn = True

    def __init__(self, conn, details):
        threading.Thread.__init__(self)
        self.conn = conn
        self.details = details

    def exist(self, ch):
        for i in ref_compte:
            if str(ch) == i:
                return True
        return False
# ---------------------------------------------------------------------------------------

    def creer_compte(self, ref):
        ref_compte.append(ref)
        ch = ref
        self.conn.send(bytes('**** ENTER YOUR INFORMATION ****', format))
        self.conn.send(bytes("GIVE YOUR ACCOUNT'S ID", format))
        val = self.receive()
        ch = ch+' '+val+' '
        self.conn.send(
            bytes("ACOUNT STATE \n 1/ Negative 2/ Positive", format))
        msg = self.receive()
        if (int(msg) == 1):
            ch = ch+'NEGATIVE'+' '
            ch = ch+str(random.randint(int(val), int(val)+300))
        if (int(msg) == 2):
            ch = ch+'POSITIVE'+' '
            ch = ch+str(random.randint(0, int(val)))
        self.conn.send(bytes(ch, format))
        compte = open('vols.txt', 'a+')
        compte.write(ch+"\n")
        compte.close()
# -----------------------------------------------------------------------------------------

    def gerer_compte(self, ref):
        choice = 1
        while choice == 1:
            self.conn.send(
                bytes("1/PULL REQUEST \n 2/ADD \n 3/RECIEVE BILL", format))
            choix = int(self.receive())
            compte = open('vols.txt', 'r')
            historique = open('histo.txt', 'a+')
            lines = compte.readlines()
            compte.close()
            compte = open('vols.txt', 'w')
            while (choix not in range(1, 4)):
                self.conn.send(bytes("WRONG CHOICE ! \n", format))
                self.conn.send(
                    bytes("1/PULL REQUEST \n 2/ADD \n 3/RECIEVE BILL", format))
                choix = int(self.receive())

            if (choix == 1):
                for line in lines:
                    Liste_ch = line.split(" ")
                    if (Liste_ch[0] == ref):
                        bank_mutex.acquire()
                        self.conn.send(bytes("ENTER THE AMMOUNT", format))
                        mont = int(self.receive())
                        if (Liste_ch[2].upper() == "NEGATIVE"):
                            if ((int(Liste_ch[1])+mont) > int(Liste_ch[3])):
                                self.conn.send(
                                    bytes("YOU HAVE REACHED THE LIMIT !!!", format))
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' '+Liste_ch[2]
                                his = his+' ' + \
                                    Liste_ch[3]+' '+'pull request' + \
                                    ' '+str(mont)+' '+'failed'
                                historique.write(his+'\n')
                                compte.write(line)
                            if (mont+int(Liste_ch[1])) < int(Liste_ch[3]):
                                self.conn.send(
                                    bytes("TRANSACTION SUCCESEDED", format))
                                Liste_ch[1] = str(int(Liste_ch[1])-mont)
                                tarif = (mont*2)/100
                                fac = Liste_ch[0]+' '+str(tarif)
                                facture = open("factures.txt", "a+")
                                facture.write(fac + "\n")
                                facture.close()
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' ' + \
                                    Liste_ch[2]+' '+Liste_ch[3]
                                fin = his+' '+'Pull request' + \
                                    ' '+str(mont)+' '+'succeseded'
                                historique.write(fin+'\n')
                                compte.write(his)

                        if (Liste_ch[2].upper() == "POSITIVE"):
                            if (mont > (int(Liste_ch[1])+(int(Liste_ch[1])))):
                                self.conn.send(
                                    bytes("You have reached the LIMIT !!! ", format))
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' '+Liste_ch[2]
                                his = his+' ' + \
                                    Liste_ch[3]+' '+'pull request' + \
                                    ' '+str(mont)+' '+'fail'
                                historique.write(his+'\n')
                                compte.write(line)
                            if (mont < int(Liste_ch[1])):
                                self.conn.send(
                                    bytes("TRANSACTION SUCCESEDED", format))
                                Liste_ch[1] = str(int(Liste_ch[1])-mont)
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' ' + \
                                    Liste_ch[2]+' '+Liste_ch[3]
                                fin = his+' '+'retrait' + \
                                    ' '+str(mont)+' '+'succes'
                                historique.write(fin+'\n')
                                compte.write(his)
                            if (mont in range(int(Liste_ch[1]), int(Liste_ch[3])+int(Liste_ch[1]))):
                                self.conn.send(
                                    bytes("TRANSACTION SUCCESEDED", format))
                                Liste_ch[1] = str(mont-int(Liste_ch[1]))
                                tarif = (mont*2)/100
                                fac = Liste_ch[0]+' '+str(tarif)
                                facture = open("factures.txt", "a+")
                                facture.write(fac + "\n")
                                facture.close()
                                Liste_ch[2] = "NEGATIVE"
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' ' + \
                                    Liste_ch[2]+' '+Liste_ch[3]
                                fin = his+' '+'retrait' + \
                                    ' '+str(mont)+' '+'succes'
                                historique.write(fin+'\n')
                                compte.write(his)
                        bank_mutex.release()

                    else:
                        compte.write(line)
            if (choix == 2):
                bank_mutex.acquire()
                for line in lines:
                    Liste_ch = line.split(" ")
                    if (Liste_ch[0] == ref):
                        self.conn.send(bytes("ENTER THE AMMOUNT", format))
                        mont = int(self.receive())
                        if (Liste_ch[2].upper() == "NEGATIVE"):
                            if (int(Liste_ch[1]) > mont):
                                self.conn.send(
                                    bytes("TRANSACTION  SUCCESEDED", format))
                                Liste_ch[1] = str(int(Liste_ch[1])-mont)
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' ' + \
                                    Liste_ch[2]+' '+Liste_ch[3]
                                fin = his+' '+'ajout'+' ' + \
                                    str(mont)+' '+'succes'
                                historique.write(fin+'\n')
                                compte.write(his)
                            else:
                                self.conn.send(
                                    bytes("TRANSACTION  SUCCESEDED", format))
                                Liste_ch[1] = str(mont-int(Liste_ch[1]))
                                Liste_ch[2] = "POSITIVE"
                                his = Liste_ch[0]+' '
                                his = his+Liste_ch[1]+' ' + \
                                    Liste_ch[2]+' '+Liste_ch[3]
                                fin = his+' '+'add'+' '+str(mont)+' '+'succes'
                                historique.write(fin+'\n')
                                compte.write(his)

                        else:
                            self.conn.send(
                                bytes("TRANSACTION SUCCESEDED", format))
                            Liste_ch[1] = str(int(Liste_ch[1])+mont)
                            his = Liste_ch[0]+' '
                            his = his+Liste_ch[1]+' ' + \
                                Liste_ch[2]+' '+Liste_ch[3]
                            fin = his+' '+'ajout'+' '+str(mont)+' '+'succes'
                            historique.write(fin+'\n')
                            compte.write(his)

                    else:
                        compte.write(line)
                bank_mutex.release()

            if (choix == 3):
                if (exist_facture(ref) == False):
                    self.conn.send(bytes("YOU HAVE NO BILL TO PAY", format))
                else:
                    fac = open("factures.txt", "r")
                    lines = fac.readlines()
                    fac.close()
                    somme = 0.0
                    for line in lines:
                        Liste_ch = line.split(' ')
                        if (Liste_ch[0] == ref):
                            somme += float(Liste_ch[1][0] +
                                           Liste_ch[1][1]+Liste_ch[1][2])
                    self.conn.send(bytes("**** YOUR BILLS **** ", format))
                    self.conn.send(
                        bytes(str(somme)+" dt , THANK YOU FOR YOUR PAYMENT ", format))

            self.conn.send(
                bytes("YOU WANT TO RETURN TO MAIN MENU ! \n 1/YES \t 2/NO", format))
            choice = int(self.receive())
            if (choice == 2):
                self.conn.send(bytes("SEE YA", format))
                self.receive()


# -------------------------------------------------------------------------------------------


    def receive(self):
        ch = self.conn.recv(buf).decode(format)
        if ch == DISCONNECT_MESSAGE:
            ch1 = Label(scene, text=f"DISCONNECT {self.details} disconnect.")
            ch1.pack()
            scene.update()
        else:
            return ch

    def run(self):
        ch = Label(scene, text=f"NEW CONNECTION {self.details} connected.")
        ch.pack()
        scene.update()

        self.conn.send(
            bytes("HELLO, please enter your account's reference", format))
        ch = self.receive()
        print(ref_compte)

        if (exist(ch) == False):
            self.creer_compte(ch)
            self.gerer_compte(ch)
        else:
            self.gerer_compte(ch)
# --------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------


def exist(ch):
    for i in ref_compte:
        if str(ch) == i:
            return True
    return False
# ----------------------------------------------------------


def voir_compte():
    view = Toplevel(scene)
    view.title("CHECK ACCOUNTS")
    ch = Label(view, text="**** HELLO ****")
    ch.pack()
    tableview = Treeview(view, columns=(1, 2, 3, 4), heigh=14, show="headings")
    tableview.heading(1, text="ACCOUNT Reference")
    tableview.heading(2, text="ACCOUNT VALUE")
    tableview.heading(3, text="ACCOUNT STATE")
    tableview.heading(4, text="ACCOUNT limit")
    compte = open('vols.txt', 'r')
    lines = compte.readlines()
    compte.close()
    for line in lines:
        Liste_ch = line.split(' ')
        tableview.insert('', END, values=Liste_ch)

    tableview.pack()
# --------------------------------------------------------------------


def chercher_facture(event=None):
    ref = my_msg.get()
    somme = 0.0
    valeur = []
    if (exist_facture(ref) == False):
        ch = Label(viewfac, text="No bill for this account")
        ch.pack()
    else:
        tableview = Treeview(viewfac, columns=(
            1, 2), heigh=14, show="headings")
        tableview.heading(1, text="Account Reference ")
        tableview.heading(2, text="Pay ammount")
        compte = open('factures.txt', 'r')
        lines = compte.readlines()
        compte.close()
        for line in lines:
            parcour = line.split(' ')
            if (parcour[0] == ref):
                somme += float(parcour[1][0]+parcour[1][1]+parcour[1][2])
        valeur = [ref, str(somme)]
        print(valeur)
        tableview.insert('', END, values=valeur)
        tableview.pack()


# -----------------------------------------------------------------
def consulter_facture():
    global viewfac
    global my_msg
    viewfac = Toplevel(scene)
    viewfac.geometry("400x300")
    viewfac.title(" CHECK BILLS")
    ch = Label(viewfac, text="**** HELLO **** ")
    ch.pack()
    my_msg = StringVar()
    entry_field = Entry(viewfac, textvariable=my_msg)
    entry_field.pack()
    entry_field.bind("<Return>", chercher_facture)
    send_button = Button(viewfac, text="Search")
    send_button.bind("<ButtonRelease-1>", chercher_facture)
    send_button.pack()
# -------------------------------------------------------------------------------------------------


def consulter_histrorique():
    view = Toplevel(scene)
    view.title("CHECK HISTORY")
    ch = Label(view, text="**** HELLO ****")
    ch.pack()
    tableview = Treeview(view, columns=(
        1, 2, 3, 4, 5, 6, 7), heigh=20, show="headings")
    tableview.heading(1, text="Account References")
    tableview.heading(2, text="Value after transaction")
    tableview.heading(3, text="State after transaction")
    tableview.heading(4, text="Account Plafond du compte")
    tableview.heading(5, text="operation")
    tableview.heading(6, text="Amount Value ")
    tableview.heading(7, text="fail/succes")
    compte = open('histo.txt', 'r')
    lines = compte.readlines()
    compte.close()
    for i in range(0, len(lines)-1, 2):
        parcour1 = lines[i].split(" ")
        parcour2 = lines[i+1].split(" ")
        parcour = parcour1+parcour2[1:4]
        tableview.insert('', END, values=parcour)

    tableview.pack()

# ---------------------------------------------------------------------------------------------------


def quitter():
    scene.destroy()
# -----------------------------------------------------------------------------------------------


def exist_facture(ch):
    ref_facture = []
    compte = open("factures.txt", "r")
    lines = compte.readlines()
    compte.close()
    for line in lines:
        ref = line.split(" ")
        ref_facture.append(ref[0])
    if (ch in ref_facture):
        return True
    else:
        return False
# ---------------------------------------------------------------------------------------------------


def charger_ref_existant():
    compte = open("vols.txt", "r")
    lines = compte.readlines()
    compte.close()
    for line in lines:
        ref = line.split(" ")
        ref_compte.append(ref[0])


# ---------------------------------------------------------------------------------------------------
def start():
    global conn
    global addr
    ch = Label(scene, text="Server is starting...")
    ch1 = Label(scene, text=f" Server is listening on {SERVER}")
    charger_ref_existant()
    ch.pack()
    ch1.pack()
    scene.update()
    while True:
        server_socket.listen()
        conn, addr = server_socket.accept()
        gerer_clients(conn, addr).start()


global scene
scene = Tk()
scene.geometry("500x300")
scene.title("RESERVATION DES VOLS ")
mainmenu = Menu(scene)
firstmenu = Menu(mainmenu)
mainmenu.add_cascade(label="OPTIONS", menu=firstmenu)
firstmenu.add_command(
    label="Started ", command=threading.Thread(target=start).start())
firstmenu.add_separator()
firstmenu.add_command(label="Quit", command=scene.destroy)
mainmenu.add_command(label="CHECK ACCOUNTS", command=voir_compte)
mainmenu.add_command(label="CHECK BILLS ", command=consulter_facture)
mainmenu.add_command(label="CHECK HISTORY", command=consulter_histrorique)


scene.config(menu=mainmenu)
scene.mainloop()
