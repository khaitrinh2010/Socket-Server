import sys
import socket
import threading
from client_side.returned_authentication_message import handle_return_login, handle_return_register
from client_side.listen_to_server_action import handle_return_begin
from client_side.returned_room_message import handle_returned_create, handle_returned_join, handle_returned_room_list
from client_side.returned_game_message import handle_return_in_progress, handle_return_board_status, handle_return_game_end


USERNAME = None
ROOM_LIST = None
MODE = None
ROOM_NAME = None
WAITING_FOR_PLAYER = False  #JOIN
IS_PLAYER = False
IS_VIEWER = False
IS_TURN = None
WAITING_FOR_OPPONENT = False #WAIT FOR OPPONENT TO MOVE


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket


def listen_to_message_from_server(client_socket):
    global WAITING_FOR_PLAYER
    try:
        while True:
            try:
                response = client_socket.recv(8192).decode('ascii')
                if not response:
                    raise ConnectionResetError
                process_server_message(response)
            except (ConnectionResetError, socket.timeout):
                print("Disconnected from the server.")
                break
    finally:
        if client_socket:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def process_server_message(response):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_VIEWER, MODE, IS_TURN
    print("\r" + " " * 80, end="\r")
    if response.startswith("LOGIN"):
        print(handle_return_login(response, USERNAME))
    elif response.startswith("REGISTER"):
        print(handle_return_register(response, USERNAME))
    elif response.startswith("BEGIN"):
        print(handle_return_begin(response))
        player1, player2 = response.split(":")[1], response.split(":")[2]
        if player1 == USERNAME:
            IS_TURN = False
        elif player2 == USERNAME:
            IS_TURN = True

        WAITING_FOR_PLAYER = False  # Game begins, stop waiting
    elif response.startswith("ROOMLIST"):
        print(handle_returned_room_list(response, MODE))
    elif response.startswith("CREATE"):
        if "ACKSTATUS:0" in response:
            print(f"Successfully created room {ROOM_NAME}")
            print("Waiting for other player...")
            WAITING_FOR_PLAYER = True  # Waiting for second player
            IS_PLAYER = True
        else:
            print("Failed to create room.")
    elif response.startswith("JOIN"):
        status = response.split(":")[2]
        if(status == "0"):
            if MODE == "PLAYER":
                IS_PLAYER = True
            elif MODE == "VIEWER":
                IS_VIEWER = True
        print(handle_returned_join(response, ROOM_NAME, MODE))
    elif response.startswith("INPROGRESS"):
        print(handle_return_in_progress(response))
    elif response.startswith("BADAUTH"):
        print("Error: You must log in to perform this action")
    elif response.startswith("BOARDSTATUS"):
        print(handle_return_board_status(response))
        if IS_TURN != None:
            IS_TURN = not IS_TURN
        if IS_PLAYER and IS_TURN:
            print("It is your turn.")
        elif IS_PLAYER and not IS_TURN:
            print("It is the opponent's turn.")
    elif response.startswith("GAMEEND"):
        print(handle_return_game_end(response, IS_PLAYER, USERNAME))

    else:
        print(response)


def handle_outside_input(client_socket):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_TURN
    try:
        while True:
            if WAITING_FOR_PLAYER:
                continue
            if IS_PLAYER and not IS_TURN:
                continue
            try:
                message = input()
            except EOFError:
                break
            if message == "LOGIN":
                handle_login(client_socket)
            elif message == "REGISTER":
                handle_register(client_socket)
            elif message == "ROOMLIST":
                handle_room_list(client_socket)
            elif message == "CREATE":
                handle_create(client_socket)
            elif message == "JOIN":
                handle_join(client_socket)
            elif message == "PLACE":
                execute_place_client(client_socket)
                print()
            elif message == "FORFEIT":
                handle_forfeit(client_socket)
    except (ConnectionResetError, socket.timeout):
        print("Disconnected from the server.")
    finally:
        if client_socket:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

def handle_forfeit(client_socket):
    client_socket.send("FORFEIT".encode('ascii'))

def execute_place_client(client_socket):
    col = input("Column: ")
    row = input("Row: ")
    while True:
        if not col.isnumeric() or not row.isnumeric() or not(0 <= int(col) <= 2 and 0 <= int(row) <= 2):
            print(" (Column/Row) values must be an integer between 0 and 2")
            col = input("Column: ")
            row = input("Row: ")
        else:
            break
    client_socket.send(f"PLACE:{col}:{row}".encode('ascii'))

def handle_login(client_socket):
    global USERNAME
    username = input("Enter username: ")
    password = input("Enter password: ")
    USERNAME = username
    client_socket.send(f"LOGIN:{username}:{password}".encode('ascii'))


def handle_register(client_socket):
    global USERNAME
    username = input("Enter username: ")
    password = input("Enter password: ")
    USERNAME = username
    client_socket.send(f"REGISTER:{username}:{password}".encode('ascii'))


def handle_room_list(client_socket):
    global MODE
    MODE = input("Do you want to list rooms as Player or Viewer? ").strip().upper()
    client_socket.send(f"ROOMLIST:{MODE}".encode('ascii'))


def handle_create(client_socket):
    global ROOM_NAME, WAITING_FOR_PLAYER
    ROOM_NAME = input("Enter room name: ")
    client_socket.send(f"CREATE:{ROOM_NAME}".encode('ascii'))
    WAITING_FOR_PLAYER = True  # Set to true when waiting for second player


def handle_join(client_socket):
    global ROOM_NAME, MODE
    ROOM_NAME = input("Enter room name to join: ").strip()
    MODE = input("Do you want to join as Player or Viewer? ").strip().upper()
    client_socket.send(f"JOIN:{ROOM_NAME}:{MODE}".encode('ascii'))


def main(args: list[str]) -> None:
    global client_socket
    if len(args) != 2:
        print("Usage: python client.py <server_address> <port>")
        sys.exit(1)

    SERVER_ADDRESS = args[0]
    PORT = int(args[1])

    try:
        client_socket = connect_to_server(SERVER_ADDRESS, PORT)

        listener_thread = threading.Thread(target=listen_to_message_from_server, args=(client_socket,))
        listener_thread.daemon = True
        listener_thread.start()

        handle_outside_input(client_socket)
    except Exception as e:
        print(f"An error occurred: {e}")
        if(client_socket):
            client_socket.shutdown(socket.SHUT_RDWR)
    finally:
        client_socket.shutdown(socket.SHUT_RDWR)
        print("Client socket closed.")



if __name__ == "__main__":
    main(sys.argv[1:])
