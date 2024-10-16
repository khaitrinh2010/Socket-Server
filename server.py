import json
import sys
import socket

import select

from authen.user_management import handle_authentication_message
from room.room_command_selection import handle_room_message
from game_handler.game_command_selection import handle_game_command
from model.User import User
from game_handler.game_management import handle_game_end_and_forfeit

USERS = {} # MAP EACH USERNAME TO A USER OBJECT
ROOMS = {} # MAP EACH ROOM NAME TO A ROOM OBJECT ta
SOCKET_TO_USER = {}
CLIENT_MESSAGE = {}
LOGIN = False


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
    global LOGIN
    message = message.strip()
    components = message.split(":")
    if components[0] == "LOGIN" or components[0] == "REGISTER":
        username = handle_authentication_message(message, path, sock, USERS)
        if components[0] == "LOGIN":
            SOCKET_TO_USER[sock] = username
    else:
        if not SOCKET_TO_USER.get(sock):
            sock.send("BADAUTH".encode('ascii'))
            return
        if components[0] in ["PLACE", "FORFEIT"] and not USERS[SOCKET_TO_USER[sock]].get_room():
            sock.send("NOROOM".encode('ascii'))
            return
        if components[0] in ["ROOMLIST", "JOIN", "CREATE"]:
            handle_room_message(message, ROOMS, USERS, SOCKET_TO_USER[sock], SOCKET_TO_USER, sock)
        elif components[0] in ["PLACE", "FORFEIT", "MOVE"]:
            handle_game_command(message, SOCKET_TO_USER[sock], USERS, USERS[SOCKET_TO_USER[sock]].get_room().get_name(), ROOMS)


def init_server(host, port, path):
    global CLIENT_MESSAGE
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.bind((host, port))
    server.listen(5)
    server.setblocking(False)
    socket_list = [server]
    clients = {}
    try:
        while True:
            read_server, _, exceptional_server = select.select(socket_list, [], socket_list)
            for sock in read_server:
                if sock == server:
                    client_socket, client_address = server.accept()
                    client_socket.setblocking(False)
                    socket_list.append(client_socket)
                    clients[client_socket] = client_address
                else:
                    if not socket_connected(sock):
                        handle_disconnect(sock)
                        socket_list.remove(sock)
                        sock.shutdown(socket.SHUT_RDWR)
                        sock.close()
                        continue
                    else:
                        message = sock.recv(8192).decode('ascii')
                        # if not message:
                        #     handle_disconnect(sock)
                        #     socket_list.remove(sock)
                        #     sock.shutdown(socket.SHUT_RDWR)
                        #     continue
                        if(message):
                            handle_client_message(message.strip(), path, sock)
                    # except Exception as e:
                    #
                    #     socket_list.remove(sock)
                    #     del clients[sock]
                    #     sock.shutdown(socket.SHUT_RDWR)
                    #     sock.close()
            for sock in exceptional_server:
                socket_list.remove(sock)
                del clients[sock]
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
    except Exception as e: #
        print("Server shutting down.")
    finally:
        for sock in socket_list:
            sock.close()
    server.close()

def socket_connected(sock):
    try:
        sock.send(b'')
        return True
    except Exception as e:
        return False

def handle_disconnect(sock):
    try:
        print("SIUUU disconnect")
        username = SOCKET_TO_USER[sock]
        foundUser = USERS[username]
        if foundUser.get_room():
            room = foundUser.get_room()
            if room:
                handle_game_end_and_forfeit(["FORFEIT"], username, USERS, room.get_name(), ROOMS)
    except Exception as e: #
        return

def main(args: list[str]) -> None:
    # Begin here!
    if(len(args) != 1):
        print("Error: Expecting 1 argument: <server config path>.")
        return
    server_config_path = args[0]
    PORT = None
    DATABASE_PATH = None
    with open(server_config_path, 'r') as f:
        data = json.load(f)
        PORT = data['port']
        DATABASE_PATH = data['userDatabase']
    load_users_from_file(DATABASE_PATH)
    init_server('0.0.0.0', PORT, DATABASE_PATH)


if __name__ == "__main__":
    main(sys.argv[1:])

