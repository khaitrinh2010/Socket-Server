import sys
import socket
import select

from src.authen.user_management import handle_authentication_message


def handle_client_message(message, path) -> str:
    components = message.split(":")
    if components[0] == "LOGIN" or components[0] == "REGISTER":
        return handle_authentication_message(message, path)

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
                client_socket.setblocking(False) # client won't block the server while waiting for it to send data
                socket_list.append(client_socket)
                clients[client_socket] = client_socket
            else: #CLIENT SOCKET
                #client socket is in server side, used for communication with the client
                try:
                    message = sock.recv(8192).decode('ascii')
                    if not message:
                        raise ConnectionResetError
                    response = handle_client_message(message, path)
                    sock.send(response.encode('ascii'))
                except Exception as e:
                    socket_list.remove(sock)
                    del clients[sock]
        for sock in exceptional_server:
            socket_list.remove(sock)
            del clients[sock]

def main(args: list[str]) -> None:
    # Begin here!
    init_server('127.0.0.1', 65432, "DATABASE.json")


if __name__ == "__main__":
    main(sys.argv[1:])
