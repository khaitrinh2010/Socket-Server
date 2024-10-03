from authen.authentication import handle_login, handle_register

def handle_authentication_message(message, db_path, sock, all_users):
    message = message.split(":")
    prompt = message[0]
    if len(message) != 3:
        if prompt == "LOGIN":
            return "LOGIN:ACKSTATUS:3"
        elif prompt == "REGISTER":
            return "REGISTER:ACKSTATUS:2"
    else:
        if prompt == "LOGIN":
            return handle_login(message, db_path, sock, all_users)
        elif prompt == "REGISTER":
            return handle_register(message, db_path, sock, all_users)

