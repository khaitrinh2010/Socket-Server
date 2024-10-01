import sys
import socket


def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def handle_outside_input(client_socket):
    while True:
        message = input("Enter message: ")
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

def handle_login(client_socket):
    username = input("Enter username: ")
    password = input("Enter password: ")
    client_socket.send(f"LOGIN:{username}:{password}".encode('ascii'))
    response = client_socket.recv(8192).decode('ascii')
    print(response)

def handle_register(client_socket):
    username = input("Enter username: ")
    password = input("Enter password: ")
    client_socket.send(f"REGISTER:{username}:{password}".encode('ascii'))
    response = client_socket.recv(8192).decode('ascii')
    print(response)

def handle_room_list(client_socket):
    mode = input("Do you want to list rooms as Player or Viewer? ").strip().upper()
    client_socket.send(f"ROOMLIST:{mode}".encode('ascii'))
    response = client_socket.recv(8192).decode('ascii')
    print(response)

def handle_create(client_socket):
    room_name = input("Enter room name: ")
    client_socket.send(f"CREATE:{room_name}".encode('ascii'))
    response = client_socket.recv(8192).decode('ascii')
    print(response)

def handle_join(client_socket):
    room_name = input("Enter room name to join: ").strip().upper()
    mode = input("Do you want to join as Player or Viewer? ").strip().upper()
    client_socket.send(f"JOIN:{room_name}:{mode}".encode('ascii'))
    response = client_socket.recv(8192).decode('ascii')
    print(response)

def listen_to_message_from_server(client_socket):
    while True:
        response = client_socket.recv(8192).decode('ascii')
        pass

def main(args: list[str]) -> None:
    # Begin here!
    if len(args) != 3:
        print("Expecting 2 arguments: server address and port")
        return
    server_address = args[1]
    port = int(args[2])
    client_socket = connect_to_server(server_address, port)
    handle_outside_input(client_socket)

if __name__ == "__main__":
    main(sys.argv[1:])
