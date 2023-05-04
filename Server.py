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
ref_vols = []
tester_conx = False
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = '192.168.1.133's
vol_mutex = threading.Lock()

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
        for i in ref_vols:
            if str(ch) == i:
                return True
        return False
# ---------------------------------------------------------------------------------------

    def creer_vols(self, ref):
        ref_vols.append(ref)
        ch = ref
        self.conn.send(
            bytes('**** GIVE THE REFERENCE OF THE VOL ****', format))


# -----------------------------------------------------------------------------------------


    def gerer_vols(self, ref):
        choice = 1
        while choice == 1:
            self.conn.send(
                bytes("1/DEMANDE DE RESERVATION \n 2/ANNULATION DE RESERVATION \n 3/RECIEVE BILL", format))
            choix = int(self.receive())
            vols = open('vols.txt', 'r+')
            historique = open('histo.txt', 'a+')
            lines = vols.readlines()
            vols.close()
            vols = open('vols.txt', 'w')
            while (choix not in range(1, 4)):
                self.conn.send(bytes("WRONG CHOICE ! \n", format))
                self.conn.send(
                    bytes("1/DEMANDE DE RESERVATION \n 2/ANNULATION DE RESERVATION \n 3/RECIEVE BILL", format))
                choix = int(self.receive())

            if (choix == 1):
                for line in lines:
                    Liste_ch = line.split(" ")
                    if (Liste_ch[0] == ref):
                        vol_mutex.acquire()
                        self.conn.send(
                            bytes("ENTER THE number of PLACE to RESERVATE", format))
                        mont = int(self.receive())
                        if (int(Liste_ch[2]) < mont):
                            self.conn.send(
                                bytes("YOU HAVE REACHED THE LIMIT !!!", format))
                            his = Liste_ch[0]+' '
                            his = Liste_ch[0]+' '
                            his = his+str(self.details)[18:23]+' '
                            fin = his+'DEMANDE' +\
                                ' '+str(mont)+' '+'FAILED'
                            historique.write(fin+'\n')
                            vols.write(line)

                        elif (int(Liste_ch[2]) >= mont):
                            self.conn.send(
                                bytes("RESERVATION SUCCESEDED", format))
                            tarif = (mont*int(Liste_ch[3]))
                            fac = str(self.details)[18:23]+' '+str(tarif)
                            vols = open("vols.txt", "a+")
                            facture = open("factures.txt", "a+")
                            facture.write(fac + "\n")
                            facture.close()
                            his = Liste_ch[0]+' '
                            his = his+str(self.details)[18:23]+' '
                            fin = his+'DEMANDE' +\
                                ' '+str(mont)+' '+'succeseded'
                            historique.write(fin+'\n')

                            # Mark the line as modified
                            line_modified = True
                            # Write the modified line to the file
                            vols.write(Liste_ch[0]+' '+Liste_ch[1] +
                                       ' '+str(int(Liste_ch[2])-mont)+' '+Liste_ch[3]+'\n')
                    else:
                        # If the line hasn't been modified, write it back to the file
                        vols.write(line)
    # Close the file after all modifications have been made
                vols.close()

            if (choix == 2):

                for line in lines:
                    Liste_ch = line.split(" ")
                    if (Liste_ch[0] == ref):
                        vol_mutex.acquire()
                        self.conn.send(
                            bytes("ENTER THE number of PLACE to CANCEL", format))
                        mont = int(self.receive())
                        if (int(Liste_ch[2]) < mont):
                            self.conn.send(
                                bytes("YOU CAN'T CANCEL MORE THAN YOU RESERVED !!!", format))
                            his = Liste_ch[0]+' '
                            his = Liste_ch[0]+' '
                            his = his+str(self.details)[18:23]+' '
                            fin = his+'ANNULATION' +\
                                ' '+str(mont)+' '+'FAILED'
                            historique.write(fin+'\n')
                            vols.write(line)
                        else:
                            self.conn.send(
                                bytes("CANCELATION SUCCESEDED", format))
                            tarif = (mont*int(Liste_ch[3]))*0.1
                            fac = str(self.details)[18:23]+' -'+str(tarif)
                            vols = open("vols.txt", "a+")
                            facture = open("factures.txt", "a+")
                            facture.write(fac + "\n")
                            facture.close()
                            his = Liste_ch[0]+' '
                            his = his+str(self.details)[18:23]+' '
                            fin = his+'ANNULATION' +\
                                ' '+str(mont)+' '+'succeseded'
                            historique.write(fin+'\n')

                            # Mark the line as modified
                            line_modified = True
                            # Write the modified line to the file
                            vols.write(Liste_ch[0]+' '+Liste_ch[1] +
                                       ' '+str(int(Liste_ch[2])+mont)+' '+Liste_ch[3]+'\n')
                    else:
                        # If the line hasn't been modified, write it back to the file
                        vols.write(line)
        # Close the file after all modifications have been made
                vols.close()

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
                        if (Liste_ch[0] == str(self.details)[18:23]):
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
            bytes("GIVE THE REFERENCE OF THE VOL", format))
        ch = self.receive()
        print(ref_vols)

        if (exist(ch) == False):
            self.creer_vols(ch)
            self.gerer_vols(ch)
        else:
            self.gerer_vols(ch)
# --------------------------------------------------------------------------------------------------

    def rerun(self):
        while True:
            self.conn.send(
                bytes("GIVE THE REFERENCE OF THE VOL (type 'menu' to return to main menu)", format))
            ch = self.receive()
            print(ref_vols)

            if ch.lower() == 'menu':
                self.conn.send(bytes("Returning to main menu...", format))
                break

            while ch == '':
                self.conn.send(
                    bytes("Please enter a valid reference", format))
                ch = self.receive()

            if exist(ch):
                self.gerer_vols(ch)
            else:
                self.creer_vols(ch)
                self.gerer_vols(ch)
# ---------------------------------------------------------------------------------------------------


def exist(ch):
    for i in ref_vols:
        if str(ch) == i:
            return True
    return False
# ----------------------------------------------------------


def voir_vols():
    view = Toplevel(scene)
    view.title("CHECK  VOLS")
    ch = Label(view, text="**** HELLO ****")
    ch.pack()
    tableview = Treeview(view, columns=(1, 2, 3, 4), heigh=14, show="headings")
    tableview.heading(1, text="Référence Vol")
    tableview.heading(2, text="Destination")
    tableview.heading(3, text="Nombre Places")
    tableview.heading(4, text="Prix Place")
    vols = open('vols.txt', 'r')
    lines = vols.readlines()
    vols.close()
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
        ch = Label(viewfac, text="No bill for this agence")
        ch.pack()
    else:
        tableview = Treeview(viewfac, columns=(
            1, 2), heigh=14, show="headings")
        tableview.heading(1, text="Account Reference ")
        tableview.heading(2, text="Pay ammount")
        vols = open('factures.txt', 'r')
        lines = vols.readlines()
        vols.close()
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


def consulter_historique():
    view = Toplevel(scene)
    view.title("CHECK HISTORY")
    ch = Label(view, text="**** HELLO ****")
    ch.pack()
    tableview = Treeview(view, columns=(1, 2, 3, 4, 5),
                         height=20, show="headings")
    tableview.heading(1, text="Référence Vol")
    tableview.heading(2, text="Agence")
    tableview.heading(3, text="Transaction")
    tableview.heading(4, text="Value ")
    tableview.heading(5, text="fail/succes")
    with open('histo.txt', 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            parcour1 = lines[i].split(" ")
            if i < len(lines)-1:
                parcour2 = lines[i+1].split(" ")
                parcour = parcour1 + parcour2[1:4]
            else:
                parcour = parcour1 + [''] * 3  # add empty values for last row
            tableview.insert('', END, values=parcour)

    tableview.pack()


# ---------------------------------------------------------------------------------------------------


def quitter():
    scene.destroy()
# -----------------------------------------------------------------------------------------------


def exist_facture(ch):
    ref_facture = []
    vols = open("factures.txt", "r")
    lines = vols.readlines()
    vols.close()
    for line in lines:
        ref = line.split(" ")
        ref_facture.append(ref[0])
    if (ch in ref_facture):
        return True
    else:
        return False
# ---------------------------------------------------------------------------------------------------


def charger_ref_existant():
    vols = open("vols.txt", "r")
    lines = vols.readlines()
    vols.close()
    for line in lines:
        ref = line.split(" ")
        ref_vols.append(ref[0])


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
mainmenu.add_command(label="CHECK  VOLS", command=voir_vols)
mainmenu.add_command(label="CHECK BILLS ", command=consulter_facture)
mainmenu.add_command(label="CHECK HISTORY", command=consulter_historique)


scene.config(menu=mainmenu)
scene.mainloop()
