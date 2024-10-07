import json
import sys
import socket

import select

from authen.user_management import handle_authentication_message
from room.room_command_selection import handle_room_message
from game_handler.game_command_selection import handle_game_command
from model.User import User

USERS = {} # MAP EACH USERNAME TO A USER OBJECT
ROOMS = {} # MAP EACH ROOM NAME TO A ROOM OBJECT t
SOCKET_TO_USER = {}


def load_users_from_file(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.stderr.write("File not found")
        return None
    if not data:
        return None
    for user in data:
        USERS[user['username']] = User(user['username'], user['password'])

def handle_client_message(message, path, sock:socket):
    components = message.split(":")
    if components[0] == "LOGIN" or components[0] == "REGISTER":
        username = handle_authentication_message(message, path, sock, USERS)
        if components[0] == "LOGIN":
            SOCKET_TO_USER[sock] = username
    else:
        if not SOCKET_TO_USER.get(sock):
            sock.send("BADAUTH".encode('ascii'))
        if components[0] in ["ROOMLIST", "JOIN", "CREATE"]:
            handle_room_message(message, ROOMS, USERS, SOCKET_TO_USER[sock], SOCKET_TO_USER, sock)
        elif components[0] in ["PLACE", "FORFEIT", "MOVE"]:
            handle_game_command(message, SOCKET_TO_USER[sock], USERS, USERS[SOCKET_TO_USER[sock]].get_room().get_name(), ROOMS)


def init_server(host, port, path):
    # CREATE A SOCKET OBJECT WITH Ipv4 ADDRESS AND TCP PROTOCOL
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #ALLOW A SOCKET TO BE REUSED
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #SERVER CAN ACCEPT INCOMING CONNECTIONS FROM THIS ADDRESS
    server.bind((host, port))

    server.listen(5)

    #CONTAIN ALL ACTIVE SOCKETS
    socket_list = [server]
    clients = {}
    while True:
        #MONITOR WHICH SOCKETS ARE READY TO READ, WRITE, OR HAVE ERRORS
        read_server, _, exceptional_server = select.select(socket_list, [], socket_list)
        #READ SERVER: IF THE FILE DESCRIPTORS HAVE DATA AVAILABLE TO READ
        for sock in read_server:
            if sock == server: #SERVER IS READY FOR LISTENING
                #ACCEPT THE NEW CONNECTION FROM THE CLIENT AND RETURN A SOCKET TO COMMUNICATE
                client_socket, client_address = server.accept()
                client_socket.setblocking(False) # client_side won't block the server while waiting for it to send data
                socket_list.append(client_socket)
                clients[client_socket] = client_address #Not yet authenticated
            else: #CLIENT SOCKET
                #client_side socket is in server side, used for communication with the client_side
                try:
                    message = sock.recv(8192).decode('ascii')
                    if not message:
                        raise ConnectionResetError
                    handle_client_message(message, path, sock)
                    #sock.send(response.encode('ascii'))
                except Exception as e:
                    socket_list.remove(sock)
                    del clients[sock]
        for sock in exceptional_server:
            socket_list.remove(sock)
            del clients[sock]

def main(args: list[str]) -> None:
    # Begin here!
    load_users_from_file("DATABASE.json")
    init_server('127.0.0.1', 65432, "DATABASE.json")



if __name__ == "__main__":
    main(sys.argv[1:])
