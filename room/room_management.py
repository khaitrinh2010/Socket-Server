import re

from model.Room import Room
from game_handler.game_management import handle_begin

def join_room(message, all_rooms, all_users, username, socket_to_user):
    if len(message) != 3:
        return "JOIN:ACKSTATUS:3"
    mode = message[2]
    room_name = message[1]
    if mode not in ["PLAYER", "VIEWER"]:
        return "JOIN:ACKSTATUS:3"
    if not room_name in all_rooms:
        return "JOIN:ACKSTATUS:1"
    if mode == "PLAYER" and len(all_rooms[room_name].get_players()) >= 2:
        return "JOIN:ACKSTATUS:2"
    user_to_be_added = all_users[username]
    all_rooms[room_name].add_player(user_to_be_added)
    if len(all_rooms[room_name].get_players()) == 2:
        handle_begin(all_rooms, socket_to_user)
    return "JOIN:ACKSTATUS:0"

def create_room(message, all_rooms):
    room_name = message[1]
    if len(all_rooms.keys()) >= 256:
        return "CREATE:ACKSTATUS:3"
    if room_name in all_rooms.keys():
        return "CREATE:ACKSTATUS:2"
    if not is_valid_room(room_name):
        return "CREATE:ACKSTATUS:1"
    if len(message) != 2:
        return "a CREATE:ACKSTATUS:4"
    room_to_add = Room(room_name, [], [], None)
    all_rooms[room_name] = room_to_add
    return "CREATE:ACKSTATUS:0"


def room_list(all_rooms, message):
    mode = message[1]
    if mode not in ["PLAYER", "VIEWER"]:
        return "ROOMLIST:ACKSTATUS:1"
    mode = mode.upper()
    rooms_available = []
    for room_name, room in all_rooms.items():
        if mode == "PLAYER":
            if len(room.get_players()) < 2:
                rooms_available.append(room_name)
        elif mode == "VIEWER":
            rooms_available.append(room_name)
    rooms = ",".join(rooms_available)
    return f"ROOMLIST:ACKSTATUS:0:{rooms}"

def is_valid_room(room_name):
    return bool(re.match(r'^[a-zA-Z0-9_-]{1,20}$', room_name))