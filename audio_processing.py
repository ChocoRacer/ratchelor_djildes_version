#!/usr/bin/python3
import socket
import select
import speech_recognition as sr
import pyaudio as pa

HOST = ''
PORT = 7777

server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM, proto=0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))


r = sr.Recognizer()
r.pause_threshold = 1.5

server.listen(1)

liste_clients = []

nick = {}

while True:
    reception, addr = server.accept()

    try:
        data = reception.recv(1500).decode("utf-8")

        if data == "REQ INPUT":

            with sr.Microphone() as source:
                print("Say something!")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=4)

            response = r.recognize_google(audio)
            print(response + "\n\n\n")

            reception.send(response.encode("utf-8"))




    except:
        erreur_cmd = "Erreur : Pas de contenu ou de commande\n"
        reception.send(erreur_cmd.encode("utf-8"))
