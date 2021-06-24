# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 17:59:42 2021

@author: miruk
"""

import tkinter as tk
from tkinter import messagebox
import socket
from time import sleep
import threading
import random

window_main = tk.Tk()
window_main.title("Game Client")
your_name = ""
opponent_name = ""
opponent_counter = 0
rand_enemy = 0
rand_role = 0
game_timer = 60
your_role = ""
role = ["Mage", "Warrior", "Assasin"]
enemy = ["Rat", "Goblin", "Dragon", "Soldier", "Carnivorous plant"]
mage_attacks = ["Fire", "Ice", "Earth"]
warrior_attacks = ["Sword", "Great sword", "Axe"]
assasin_attacks = ["Poison", "Dagger", "Bow"]

# client di rete
client = None
HOST_ADDR = ''
HOST_PORT = 8080


top_welcome_frame= tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text = "Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
lbl_addr = tk.Label(top_welcome_frame, text = "Server IP:")
lbl_addr.pack(side=tk.LEFT)
ent_addr = tk.Entry(top_welcome_frame)
ent_addr.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda : connect())
btn_connect.pack(side=tk.LEFT)
top_welcome_frame.pack(side=tk.TOP)

top_message_frame = tk.Frame(window_main)
lbl_line = tk.Label(top_message_frame, text="________________________________________________________").pack()
lbl_welcome = tk.Label(top_message_frame, text="Waitng for connection...")
lbl_welcome.pack()
lbl_line_server = tk.Label(top_message_frame, text="______________________________________________________")
lbl_line_server.pack()
top_message_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)
top_left_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_your_name = tk.Label(top_left_frame, text="Your name: " + your_name, font = "Helvetica 13 bold")
lbl_opponent_name = tk.Label(top_left_frame, text="Opponent: " + opponent_name)
lbl_opponent1_name = tk.Label(top_left_frame, text="Opponent: ")
lbl_opponent2_name = tk.Label(top_left_frame, text="Opponent: ")
lbl_opponent3_name = tk.Label(top_left_frame, text="Opponent: ")
lbl_your_name.grid(row=0, column=0, padx=5, pady=8)
lbl_opponent_name.grid(row=1, column=0, padx=5, pady=8)
lbl_opponent1_name.grid(row=2, column=0, padx=5, pady=8)
lbl_opponent2_name.grid(row=3, column=0, padx=5, pady=8)
lbl_opponent3_name.grid(row=4, column=0, padx=5, pady=8)
top_left_frame.pack(side=tk.LEFT, padx=(10, 10))
top_frame.pack()

top_right_frame = tk.Frame(top_frame, highlightbackground="green", highlightcolor="green", highlightthickness=1)
lbl_game_round = tk.Label(top_right_frame, text="Game Timer \n waiting for players to start", foreground="blue", font = "Helvetica 14 bold")
lbl_timer = tk.Label(top_right_frame, text=" ", font = "Helvetica 24 bold", foreground="blue")
lbl_game_round.grid(row=0, column=0, padx=5, pady=5)
lbl_timer.grid(row=1, column=0, padx=5, pady=5)
top_right_frame.pack(side=tk.RIGHT, padx=(10, 10))



middle_frame = tk.Frame(window_main)

lbl_line = tk.Label(middle_frame, text="***********************************************************").pack()
btn_ready = tk.Button(middle_frame, text="**** READY ****", font = "Helvetica 13 bold", foreground="blue", command=lambda : ready(), state =tk.DISABLED)
btn_ready.pack()
middle_frame.pack()
 

final_frame = tk.Frame(middle_frame)
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
lbl_final_result = tk.Label(final_frame, text="", font = "Helvetica 15 bold", foreground="red")
lbl_final_result.pack()
lbl_role = tk.Label(final_frame, text="Your role is:", font = "Helvetica 13 bold")
lbl_role.pack()
lbl_line = tk.Label(final_frame, text="***********************************************************").pack()
final_frame.pack(side=tk.TOP)


button_frame = tk.Frame(window_main)
lbl_enemy = tk.Label(button_frame, text="Your Enemy is: ", font = "Helvetica 13 bold")
lbl_attack = tk.Label(button_frame, text="Choose Your Attack")
btn_rock = tk.Button(button_frame, text="",font = "Helvetica 15 bold", command=lambda : choice(btn_rock), state=tk.DISABLED)
btn_paper = tk.Button(button_frame, text="", font = "Helvetica 15 bold", command=lambda : choice(btn_paper), state=tk.DISABLED)
btn_scissors = tk.Button(button_frame, text="", font = "Helvetica 15 bold", command=lambda : choice(btn_scissors), state=tk.DISABLED)
lbl_enemy.grid(row=0, column=0)
lbl_attack.grid(row=1, column=0)
btn_rock.grid(row=2, column=0)
btn_paper.grid(row=3, column=0)
btn_scissors.grid(row=4, column=0)
button_frame.pack(side=tk.BOTTOM)
           

def connect():
    global your_name, HOST_ADDR
    if len(ent_name.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        your_name = ent_name.get()
        HOST_ADDR = ent_addr.get()
        lbl_your_name["text"] = "Your name: " + your_name
        connect_to_server(your_name, HOST_ADDR)
        
def connect_to_server(name,addr):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((addr, HOST_PORT))
        client.send(name.encode()) # Invia il nome al server dopo la connessione

        # disable widgets
        btn_connect.config(state=tk.DISABLED)
        ent_name.config(state=tk.DISABLED)
        lbl_name.config(state=tk.DISABLED)
        ent_addr.config(state=tk.DISABLED)


        # avvia un thread per continuare a ricevere messaggi dal server
        # non bloccare il thread principale :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")
  
def receive_message_from_server(sck, m):
    global your_name, opponent_name, game_round, opponent_counter, rand_role
    global your_choice, opponent_choice, your_score, opponent_score
    

    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        if from_server.startswith("welcome".encode()):
            if from_server == "welcome1".encode():
                lbl_welcome["text"] = "Server says: Welcome " + your_name + "! Waiting for players"
            elif from_server == "welcome2".encode():
                lbl_welcome["text"] = "Server says: Welcome " + your_name + "! Wating for player to be ready"
    
        #Aggiorna il nome dei giocatori aversari
        elif from_server.startswith("opponent_name$".encode()):
            if opponent_counter == 0:
                opponent_name = from_server.replace("opponent_name$".encode(), "".encode())
                lbl_opponent_name["text"] = "Opponent: " + opponent_name.decode()
                btn_ready.config(state = tk.NORMAL)
                opponent_counter += 1
            elif opponent_counter == 1:
                opponent_name = from_server.replace("opponent_name$".encode(), "".encode())
                lbl_opponent1_name["text"] = "Opponent: " + opponent_name.decode()
                opponent_counter += 1
            elif opponent_counter == 2:
                opponent_name = from_server.replace("opponent_name$".encode(), "".encode())
                lbl_opponent2_name["text"] = "Opponent: " + opponent_name.decode()
                opponent_counter += 1
            elif opponent_counter == 3:
                opponent_name = from_server.replace("opponent_name$".encode(), "".encode())
                lbl_opponent3_name["text"] = "Opponent: " + opponent_name.decode()
                opponent_counter += 1
         
        #Riceve il ruolo da aassegnare al giocatore
        elif isinstance(from_server, int):
             rand_role = int(from_server.decode())
            
        #Quando riceve il segnale dal server fa partire il gioco
        elif from_server.startswith("Start".encode()):
            threading._start_new_thread(game_session, (game_timer,""))
        
        #Riceve e visualizza il nome del vincitore
        elif from_server.startswith("The winner is:".encode()):
            lbl_final_result["text"] = from_server.decode()
    sck.close()
        
def ready():
    #Manda un messaggio al server indicando che il giocatore è pronto
    client.send(("Ready").encode())
    btn_ready.config(state = tk.DISABLED)
    lbl_welcome.pack_forget()
    
def game_session(my_timer, nothing):
    global your_role, rand_enemy, rand_role
    #Assegna il ruolo al giocatore in base all'intero generato in maniera random dal server
    your_role = role[rand_role]
    
    button_asign_names(your_role)
    lbl_role ["text"] = "Your role is:" + your_role
    lbl_enemy ["text"] = "Your Enemy is:" + enemy[rand_enemy]
    enable_disable_buttons("enable")
    lbl_game_round["text"] = "The Game Has Begun"
    
    #Avvia il timer della partita
    while my_timer > 0:
        my_timer = my_timer - 1
        print("game timer is: " + str(my_timer))
        lbl_timer["text"] = my_timer
        sleep(1)

    #Quando il tempo finisce disabilita i pulsanti e manda un segnaleal server che la partita è finita
    enable_disable_buttons("disable")
    client.send(("End").encode())
    
def choice (button):
    global your_role, enemy, rand_enemy
    your_choice = button.cget("text")
    result = game_logic(your_role, enemy[rand_enemy], your_choice)
    client.send((result).encode())
    
    #Nel caso della scelta trappola manda un segnale al server che la partita è finita e disabilita i pulsanti
    if result == "trap":
        enable_disable_buttons("disable")
        lbl_timer.pack_forget()
        lbl_role ["text"] = "You are dead"
        lbl_role ["font"] = "Helvetica 15 bold"
        lbl_role ["foreground"] = "red"
        client.send(("End").encode())
        
    #Genero un nuovo mostro random per il giocatore
    rand_enemy = random.randint(0, 4)
    lbl_enemy ["text"] = "Your Enemy is:" + enemy[rand_enemy]
    
    
def button_asign_names(role):
    if role == "Mage":
        btn_rock ["text"] = mage_attacks[0]
        btn_paper  ["text"] = mage_attacks[1]
        btn_scissors  ["text"] = mage_attacks[2]
    elif role == "Warrior":
        btn_rock ["text"] =warrior_attacks[0]
        btn_paper  ["text"] = warrior_attacks[1]
        btn_scissors  ["text"] = warrior_attacks[2]
    elif role == "Assasin":
        btn_rock ["text"] = assasin_attacks[0]
        btn_paper  ["text"] = assasin_attacks[1]
        btn_scissors  ["text"] = assasin_attacks[2]
        
    
def enable_disable_buttons(todo):
    if todo == "disable":
        btn_rock.config(state=tk.DISABLED)
        btn_paper.config(state=tk.DISABLED)
        btn_scissors.config(state=tk.DISABLED)
    else:
        btn_rock.config(state=tk.NORMAL)
        btn_paper.config(state=tk.NORMAL)
        btn_scissors.config(state=tk.NORMAL)
        
def game_logic(role, enemy, attack):
    result = " "
    mage = "Mage"
    warrior = "Warrior"
    assasin = "Assasin"
    rat = "Rat"
    goblin = "Goblin"
    dragon = "Dragon"
    soldier = "Soldier"
    plant = "Carnivorous plant"
    fire = "Fire"
    ice = "Ice"
    earth = "Earth"
    sword = "Sword"
    axe = "Axe"
    great_sword = "Great sword"
    poison = "Poison"
    dagger = "Dagger"
    bow = "Bow"
    
    if role == mage:
       if enemy == rat:
           if attack == fire:
            result = "good"
           elif attack == earth:
            result = "bad"
           elif attack == ice:
            result = "trap"
       elif enemy == goblin:
           if attack == fire:
            result = "trap"
           elif attack == earth:
            result = "good"
           elif attack == ice:
            result = "bad"
       elif enemy == dragon:
           if attack == fire:
            result = "trap"
           elif attack == earth:
            result = "bad"
           elif attack == ice:
            result = "good"
       elif enemy == soldier:
           if attack == fire:
            result = "bad"
           elif attack == earth:
            result = "trap"
           elif attack == ice:
            result = "good"
       elif enemy == plant:
           if attack == fire:
            result = "good"
           elif attack == earth:
            result = "trap"
           elif attack == ice:
            result = "bad"
    elif role == warrior:
        if enemy == rat:
           if attack == sword:
            result = "good"
           elif attack == great_sword:
            result = "trap"
           elif attack == axe:
            result = "bad"
        elif enemy == goblin:
           if attack == sword:
            result = "bad"
           elif attack == great_sword:
            result = "trap"
           elif attack == axe:
            result = "good"
        elif enemy == dragon:
           if attack == sword:
            result = "bad"
           elif attack == great_sword:
            result = "good"
           elif attack == axe:
            result = "trap"
        elif enemy == soldier:
           if attack == sword:
            result = "good"
           elif attack == great_sword:
            result = "bad"
           elif attack == axe:
            result = "trap"
        elif enemy == plant:
           if attack == sword:
            result = "trap"
           elif attack == great_sword:
            result = "bad"
           elif attack == axe:
            result = "good"
    elif role == assasin:
        if enemy == rat:
           if attack == poison:
            result = "trap"
           elif attack == dagger:
            result = "bad"
           elif attack == bow:
            result = "good"
        elif enemy == goblin:
           if attack == poison:
            result = "bad"
           elif attack == dagger:
            result = "trap"
           elif attack == bow:
            result = "good"
        elif enemy == dragon:
           if attack == poison:
            result = "bad"
           elif attack == dagger:
            result = "trap"
           elif attack == bow:
            result = "good"
        elif enemy == soldier:
           if attack == poison:
            result = "bad"
           elif attack == dagger:
            result = "good"
           elif attack == bow:
            result = "trap"
        elif enemy == plant:
           if attack == poison:
            result = "good"
           elif attack == dagger:
            result = "trap"
           elif attack == bow:
            result = "bad"
    return result

window_main.mainloop()