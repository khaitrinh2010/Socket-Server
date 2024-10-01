import re

def join_room(message, all_rooms, client_address_list, client_socket):
    if len(message) != 3:
        return "JOIN:ACKSTATUS:3"
    mode = message[0]
    room_name = message[1]
    if mode not in ["PLAYER", "VIEWER"]:
        return "JOIN:ACKSTATUS:3"
    if not room_name in all_rooms:
        return "JOIN:ACKSTATUS:1"
    if mode == "PLAYER" and len(all_rooms[room_name]["players"]) >= 2:
        return "JOIN:ACKSTATUS:2"
    all_rooms[room_name][mode].append(client_address_list[client_socket])
    return "JOIN:ACKSTATUS:0"

def create_room(message, all_rooms):
    room_name = message[1]
    if len(all_rooms.keys()) >= 256:
        return "a CREATE:ACKSTATUS:3"
    if room_name in all_rooms.keys():
        return "CREATE:ACKSTATUS:2"
    if not is_valid_room(room_name):
        return "CREATE: ACKSTATUS:1"
    if len(message) != 2:
        return "a CREATE:ACKSTATUS:4"
    all_rooms[room_name] = {"players": [], "viewers": []}
    return "CREATE:ACKSTATUS:0"


def room_list(all_rooms, message):
    mode = message[0]
    if mode not in ["PLAYER", "VIEWER"]:
        return "ROOMLIST:ACKSTATUS:1"
    mode = mode.upper()
    rooms_available = []
    for key, value in all_rooms.items():
        if mode == "PLAYER":
            if value["players"] < 2:
                rooms_available.append(key)
        elif mode == "VIEWER":
            rooms_available.append(key)
    rooms = ",".join(rooms_available)
    return "ROOMLIST:ACKSTATUS:0:ROOMLIST:ACKSTATUS:0:" + rooms

def is_valid_room(room_name):
    return re.match(r'^[a-zA-Z0-9_-]{1, 20}$', room_name)