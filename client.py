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
WAITING_FOR_PLAYER = False  # JOIN
IS_PLAYER = False
IS_VIEWER = False
IS_TURN = None
WAITING_FOR_OPPONENT = False  # WAIT FOR OPPONENT TO MOVE
RUNNING = True

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def listen_to_message_from_server(client_socket):
    global WAITING_FOR_PLAYER, RUNNING
    while True:
        try:
            response = client_socket.recv(8192).decode('ascii')
            if not response:
                raise ConnectionResetError
            process_server_message(response)
        except (ConnectionResetError, socket.timeout):
            sys.stderr.write("Disconnected from the server.\n")
            break
        except Exception as e:
            #sys.stdout.write(f"response {response}")
            sys.stderr.write(f"An error occurred in listen_to_message_from_server: {type(e).__name__}: {e}\n")
            break


def process_server_message(response):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_VIEWER, MODE, IS_TURN
    sys.stdout.write("\r" + " " * 80 + "\r")
    if response.startswith("LOGIN"):
        sys.stdout.write(handle_return_login(response, USERNAME) + "\n")
    elif response.startswith("REGISTER"):
        sys.stdout.write(handle_return_register(response, USERNAME) + "\n")
    elif response.startswith("BEGIN"):
        sys.stdout.write(handle_return_begin(response) + "\n")
        player1, player2 = response.split(":")[1], response.split(":")[2]
        if player1 == USERNAME:
            IS_TURN = False
        elif player2 == USERNAME:
            IS_TURN = True
        WAITING_FOR_PLAYER = False  # Game begins, stop waiting
    elif response.startswith("ROOMLIST"):
        sys.stdout.write("\nresponse from server: " + response)
        sys.stdout.write("Hey: {handle_returned_room_list(response, MODE)}")
        sys.stdout.write(handle_returned_room_list(response, MODE) + "\n")
    elif response.startswith("CREATE"):
        if "ACKSTATUS:0" in response:
            sys.stdout.write(f"Successfully created room {ROOM_NAME}\n")
            sys.stdout.write("Waiting for other player...\n")
            WAITING_FOR_PLAYER = True  # Waiting for second player
            IS_PLAYER = True
        else:
            sys.stdout.write("Failed to create room.\n")
    elif response.startswith("JOIN"):
        status = response.split(":")[2]
        if status == "0":
            if MODE == "PLAYER":
                IS_PLAYER = True
            elif MODE == "VIEWER":
                IS_VIEWER = True
        sys.stdout.write(handle_returned_join(response, ROOM_NAME, MODE) + "\n")
    elif response.startswith("INPROGRESS"):
        sys.stdout.write(handle_return_in_progress(response) + "\n")
    elif response.startswith("BADAUTH"):
        sys.stdout.write("Error: You must log in to perform this action\n")
    elif response.startswith("BOARDSTATUS"):
        sys.stdout.write(handle_return_board_status(response) + "\n")
        if IS_TURN is not None:
            IS_TURN = not IS_TURN
        if IS_PLAYER and IS_TURN:
            sys.stdout.write("It is your turn.\n")
        elif IS_PLAYER and not IS_TURN:
            sys.stdout.write("It is the opponent's turn.\n")
    elif response.startswith("GAMEEND"):
        sys.stdout.write(handle_return_game_end(response, IS_PLAYER, USERNAME) + "\n")
    else:
        sys.stdout.write(response)

def handle_outside_input(client_socket):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_TURN, RUNNING
    while True:
        if WAITING_FOR_PLAYER:
            continue
        if IS_PLAYER and not IS_TURN:
            continue
        try:
            message = input()
        except EOFError:
            sys.stdout.write("\nEnd of input detected. Shutting down...\n")
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
            sys.stdout.write("\n")
        elif message == "FORFEIT":
            handle_forfeit(client_socket)

def handle_forfeit(client_socket):
    client_socket.send("FORFEIT".encode('ascii'))

def execute_place_client(client_socket):
    col = input("Column: ")
    row = input("Row: ")
    while True:
        if not col.isnumeric() or not row.isnumeric() or not (0 <= int(col) <= 2 and 0 <= int(row) <= 2):
            sys.stdout.write(" (Column/Row) values must be an integer between 0 and 2\n")
            print(f"row: {row}, col: {col}")
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

def handle_join(client_socket):
    global ROOM_NAME, MODE
    ROOM_NAME = input("Enter room name to join: ").strip()
    MODE = input("Do you want to join as Player or Viewer? ").strip().upper()
    client_socket.send(f"JOIN:{ROOM_NAME}:{MODE}".encode('ascii'))

def close_socket(client_socket):
    if client_socket:
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()
        sys.stdout.write("Client socket closed.\n")

def main(args: list[str]) -> None:
    global RUNNING
    if len(args) != 2:
        sys.stderr.write("Usage: python client.py <server_address> <port>\n")
        sys.exit(1)

    SERVER_ADDRESS = args[0]
    PORT = int(args[1])

    client_socket = connect_to_server(SERVER_ADDRESS, PORT)

    listener_thread = threading.Thread(target=listen_to_message_from_server, args=(client_socket,))
    listener_thread.start()

    handle_outside_input(client_socket)
    listener_thread.join()
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()

if __name__ == "__main__":
    main(sys.argv[1:])
