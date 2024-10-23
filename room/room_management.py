import re

from model.Room import Room
from game_handler.game_management import handle_begin, handle_in_progress, handle_board_status
from game import Game

def join_room(message, all_rooms, all_users, username, socket_to_user, sock):
    if len(message) != 3:
        sock.send("JOIN:ACKSTATUS:3".encode('ascii'))
        return
    mode = message[2]
    room_name = message[1]
    if mode not in ["PLAYER", "VIEWER"]:
        sock.send("JOIN:ACKSTATUS:3".encode('ascii'))
        return
    if not room_name in all_rooms:
        sock.send("JOIN:ACKSTATUS:1".encode('ascii'))
        return
    if mode == "PLAYER" and len(all_rooms[room_name].get_players()) >= 2:
        sock.send("JOIN:ACKSTATUS:2".encode('ascii'))
        return
    user_to_be_added = all_users[username]
    if mode == "PLAYER":
        all_rooms[room_name].add_player(user_to_be_added)
    elif mode == "VIEWER":
        all_rooms[room_name].add_viewer(user_to_be_added)
    all_users[username].set_room(all_rooms[room_name])
    room  = all_rooms[room_name]
    if len(room.get_players()) == 2 and room.get_current_turn() is None:
        room.set_current_turn(user_to_be_added)
        if room.get_cache():
            cache = room.get_cache()[0]
            game = room.get_game()
            game.place(cache[0], cache[1], cache[2])

    sock.send("JOIN:ACKSTATUS:0\n".encode('ascii'))
    if room.is_started_yet():
        handle_in_progress(room)
        return

    if len(all_rooms[room_name].get_players()) == 2:
        handle_begin(all_rooms, socket_to_user)



def create_room(message, all_rooms, sock, username, all_users):
    if len(message) != 2:
        sock.send("CREATE:ACKSTATUS:4".encode('ascii'))
        return
    room_name = message[1]
    if len(all_rooms.keys()) >= 256:
        sock.send("CREATE:ACKSTATUS:3".encode('ascii'))
        return
    if room_name in all_rooms.keys():
        sock.send("CREATE:ACKSTATUS:2".encode('ascii'))
        return
    if not is_valid_room(room_name): #
        sock.send("CREATE:ACKSTATUS:1".encode('ascii'))
        return


    room_to_add = Room(room_name, [], [], Game())
    room_to_add.add_player(all_users[username])
    room_to_add.set_current_turn(all_users[username])
    all_users[username].set_room(room_to_add)
    all_rooms[room_name] = room_to_add
    sock.send("CREATE:ACKSTATUS:0".encode('ascii'))


def room_list(all_rooms, message, sock):
    if(len(message) != 2):
        sock.send("ROOMLIST:ACKSTATUS:1".encode('ascii'))
        return
    mode = message[1]
    if mode not in ["PLAYER", "VIEWER"]:
        sock.send("ROOMLIST:ACKSTATUS:1".encode('ascii'))
        return
    mode = mode.upper()
    rooms_available = []
    for room_name, room in all_rooms.items():
        if mode == "PLAYER":
            if len(room.get_players()) < 2:
                rooms_available.append(room_name)
        elif mode == "VIEWER":
            rooms_available.append(room_name)
    if len(rooms_available) > 0:
        rooms = ",".join(rooms_available)
        sock.send(f"ROOMLIST:ACKSTATUS:0:{rooms}".encode('ascii'))
    else:
        sock.send("ROOMLIST:ACKSTATUS:0:".encode('ascii'))


def is_valid_room(room_name):
    return bool(re.match(r'^[a-zA-Z0-9 _-]{1,20}$', room_name))
