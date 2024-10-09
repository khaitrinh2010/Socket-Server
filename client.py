import sys
import socket
import threading

# Other imports...

USERNAME = None
ROOM_LIST = None
MODE = None
ROOM_NAME = None
WAITING_FOR_PLAYER = False  # JOIN
IS_PLAYER = False
IS_VIEWER = False
IS_TURN = None
WAITING_FOR_OPPONENT = False  # WAIT FOR OPPONENT TO MOVE

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)  # Set a timeout for the connection
    client_socket.connect((host, port))
    return client_socket

def listen_to_message_from_server(client_socket):
    global WAITING_FOR_PLAYER
    try:
        while True:
            response = client_socket.recv(8192).decode('ascii')
            if not response:
                raise ConnectionResetError
            process_server_message(response)
    except (ConnectionResetError, socket.timeout):
        print("Disconnected from the server.")
    finally:
        client_socket.close()  # Ensure the socket is closed

def process_server_message(response):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_VIEWER, MODE, IS_TURN
    print("\r" + " " * 80, end="\r")
    # Process the response...
    # (No changes needed here)

def handle_outside_input(client_socket):
    global WAITING_FOR_PLAYER, IS_PLAYER, IS_TURN
    try:
        while True:
            if WAITING_FOR_PLAYER:
                continue  # Don't accept input while waiting for the other player
            if IS_PLAYER and not IS_TURN:
                continue  # Don't accept input if it's not your turn
            message = input()
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
        client_socket.close()  # Ensure the socket is closed

def handle_forfeit(client_socket):
    client_socket.send("FORFEIT".encode('ascii'))

def execute_place_client(client_socket):
    col = input("Column: ")
    row = input("Row: ")
    while True:
        if not col.isnumeric() or not row.isnumeric() or not (0 <= int(col) <= 2 and 0 <= int(row) <= 2):
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
    print(args)
    SERVER_ADDRESS = args[0]
    PORT = args[1]
    client_socket = connect_to_server(SERVER_ADDRESS, int(PORT))

    listener_thread = threading.Thread(target=listen_to_message_from_server, args=(client_socket,))
    listener_thread.daemon = True
    listener_thread.start()

    handle_outside_input(client_socket)

if __name__ == "__main__":
    main(sys.argv[1:])