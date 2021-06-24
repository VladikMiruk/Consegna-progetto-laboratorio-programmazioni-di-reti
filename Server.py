# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 18:00:56 2021

@author: miruk
"""

from requests import get
from time import sleep
import tkinter as tk
import socket
import threading
import random

window = tk.Tk()
window.title("Server")

topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Start", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server())
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

middleFrame = tk.Frame(window)
lblAddress = tk.Label(middleFrame, text="Address:X.X.X.X")
lblAddress.pack(side=tk.LEFT)
lblPublicip = tk.Label(middleFrame, text="Public IP:X.X.X.X")
lblPublicip.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text="Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="Players").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=10, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

server = None
hostname = socket.gethostname()
Localip = socket.gethostbyname(hostname)
Publicip = get('https://api.ipify.org').text
#Si rimane in ascolto su tutti gli indirizzi in modo da poter permettere la conessione sia in locale che attraverso il web
HOST_ADDR = "0.0.0.0"
HOST_PORT = 8080
from_client = " "
num_players=" "
ready = 0
ended_games = 0
max_players = 5
clients = []
clients_names = []
player_data = []
player_score = []
player_is_dead = []



def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
   
    print ("Server started")

    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5) 
    threading._start_new_thread(accept_clients, (server, " "))

    lblAddress["text"] = "Local IP: " + Localip
    lblPublicip["text"] = "Public IP: " + Publicip
    lblPort["text"] = "Port: " + str(HOST_PORT)
    
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    
    
    
def accept_clients(the_server, y):
    while True:
        if len(clients) < max_players:
            client, addr = the_server.accept()
            clients.append(client)
            
            threading._start_new_thread(send_receive_client_message, (client, addr))
            
def send_receive_client_message(client_connection, client_ip_addr):
    global server, from_client, clients, player_data, player0, player1, ready, player_score, ended_games
    count = 0
    reverse_count = 0

    # invia un messaggio di benvenuto al client
    from_client = client_connection.recv(4096)
    if len(clients) < 2:
        client_connection.send("welcome1".encode())
    else:
        client_connection.send("welcome2".encode())

    clients_names.append(from_client.decode())
    update_from_clients_display(clients_names)  # aggiornare la visualizzazione dei nomi dei client

    if len(clients) > 1:
        sleep(1)

        # invia il nome dell'avversario
        while count < len(clients):
            reverse_count = len(clients)-1
            #All'ultimo giocatore connesso invia l'intera lista dei giocatori gia connessi
            if count == len(clients)-1:
              while reverse_count >= 0:
                  if count != reverse_count:
                      clients[count].send(("opponent_name$" + clients_names[reverse_count]).encode())
                      reverse_count -= 1
                  else:
                          reverse_count -= 1
            #Ai giocatori gia connessi invia solo il nome dell'ultimo giocatore connesso
            else:
                clients[count].send(("opponent_name$" + clients_names[reverse_count]).encode())
            count += 1
    
        
        # rimane in attesa

    while True:
        data = client_connection.recv(4096)
        if not data: break
    
        if data.startswith("Ready".encode()):
           ready += 1
           #Quando tutti i giocatori sono pronti imposta tutti i punteggi su 0 e lo stato della morte su false e poi invia il messaggio per iniziare la partita
           if (len(clients)>1) and (ready == len(clients)):
               count = 0
               for x in clients:
                player_is_dead.append(False)
                player_score.append(0)
                clients[count].send("Start".encode())
                #Decide in maniera random il ruolo del giocatore e lo invia ai client
                rand_role = random.randint(0, 2)
                clients[count].send(str(rand_role).encode())
                count += 1
        
            #Ricevo la scelta del giocatore e aggiorna i punteggi
        elif data.startswith("good".encode()):
            idx = get_client_index(clients, client_connection)
            player_score [idx] += 1
            print("good from:" +str(client_connection))
        elif data.startswith("bad".encode()):
            idx = get_client_index(clients, client_connection)
            player_score [idx] -= 1
            print("bad from:" +str(client_connection))
        elif data.startswith("trap".encode()):
            idx = get_client_index(clients, client_connection)
            player_is_dead [idx] = True
            print("trap from:" +str(client_connection))
           
            #Quando tutti i giocatori hanno finito la partita calcola il vincitore e mannda il risultato ai client
        elif data.startswith("End".encode()):
            ended_games += 1
            if ended_games == len(clients):
                winner = decide_winner()
                count = 0
                for x in clients:
                   clients[count].send(("The winner is:" +winner).encode())
                   count += 1
               
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()

    update_from_clients_display(clients_names) 

def decide_winner():
    global player_score, player_is_dead, clients, clients_names
    winner = ""
    count = 0
    deads = 0
    best_score = 0
    players = len(clients)
    while count < len(clients):
        if (player_is_dead == False) and (player_score[best_score]<player_score[count]):
            best_score = count
        elif player_is_dead[count] == True:
            deads += 1
            #Nel caso tutti i giocatori siano morti
            if deads == len(clients):
                winner ="All players dead"
                return winner
        count += 1
        
    winner = clients_names[best_score]
    
    #Si verica se dei giocatori abbiano lo stesso punteggio
    for x in range (0, players):
        if (player_score[x] == player_score[best_score]) and (best_score != x):
            winner =winner + " and " + clients_names[x]
            
    return winner
    

def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


def update_from_clients_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c +"\n")
    tkDisplay.config(state=tk.DISABLED)

window.mainloop()