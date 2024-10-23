from client_side.returned_authentication_message import check_bad_auth

def handle_returned_create(message, room_name):
    bad_auth_msg = check_bad_auth(message)
    if bad_auth_msg:
        return bad_auth_msg
    status = message.strip().split(":")[2]
    if status == "0":
        return f"Successfully created room name {room_name}\nWaiting for other players"
    elif status == "1":
        return f"Error: Room {room_name} is invalid"
    elif status == "2":
        return f"Error: Room {room_name} already exists"
    elif status == "3":
        return f"Error: Server already contains a maximum of 256 rooms"
    return ""

def handle_returned_join(message, room_name, mode):
    bad_auth_msg = check_bad_auth(message)
    if bad_auth_msg:
        return bad_auth_msg
    status = message.strip().split(":")[2]
    if status == "0":
        return f"Successfully joined room {room_name} as a {mode}"
    elif status == "1":
        return f"Error: No room named {room_name}\n"
    elif status == "2":
        return f"Error: The room {room_name}  already has 2 players"
    else:
        return ""

def handle_returned_room_list(message, mode):
    bad_auth_msg = check_bad_auth(message)
    if bad_auth_msg:
        return bad_auth_msg
    status = message.strip().split(":")[2]
    if len(message.split(":")) == 4:
        room_list = message.split(":")[3]
    if status == "0":
        return f"Room available to join as {mode}: {room_list}"
    elif status == "1":
        return "Error: Please input a valid mode"
    else:
        return ""
