o_first = False
x_first = False
have_x = False
CACHED = False
def handle_begin(all_rooms, socket_to_user):
    for room_name in all_rooms:
        room = all_rooms[room_name]
        players = room.get_players()
        if len(players) == 2:
            player1, player2 = players
            begin_message = f"BEGIN:{player1.get_username()}:{player2.get_username()}\n".encode('ascii')
            room.set_started(True)
            sent_participants = set()
            for participant in players + room.get_viewers():
                if participant not in sent_participants:
                    user_socket = participant.get_socket()
                    if user_socket:
                        try:
                            user_socket.send(begin_message)
                            if room.get_cache():
                                user_socket.send(f"BOARDSTATUS:{get_board_status(room)}\n".encode('ascii'))
                            sent_participants.add(participant)
                        except Exception as e:
                            print(f"Failed to send BEGIN message to {participant.get_username()}: {e}")
            #handle_board_status(room)
        if room.get_cache():
            room.get_cache().pop(0)

def get_board_status(room):
    game = room.get_game()
    board = game.get_board()
    res = ""
    for row in board:
        for cell in row:
            if cell == " ":
                res += "0"
            elif cell == "X":
                res += "1"
            else:
                res += "2"
    return res
def handle_in_progress(room):
    for viewers in room.get_viewers():
        current_player = room.get_current_turn().get_username()
        next_player = room.get_next_turn().get_username()
        viewers.get_socket().send(f"INPROGRESS:{current_player}:{next_player}\n".encode('ascii'))

def handle_board_status(room):
    game = room.get_game()
    board = game.get_board()
    res = ""
    for row in board:
        for cell in row:
            if cell == " ":
                res += "0"
            elif cell == "X":
                res += "1"
            else:
                res += "2"
    for p in room.get_viewers() + room.get_players():
        message = f"BOARDSTATUS:{res}\n".encode("ascii")
        try:
            p.get_socket().send(message)
        except Exception as e:
            print("Something went wrong")


def handle_place(message, username, all_users, room_name, all_rooms):
    global CACHED
    room = all_rooms[room_name]
    game = room.get_game()

    x, y = int(message[1]), int(message[2])

    if len(room.get_players()) < 2:
        room.set_cache(["X", x, y, room.get_players()[0]])
        room.set_current_turn(None)
        return

    if all_users[username] == room.get_current_turn():
        if not room.get_cache() or room.get_cache()[0][3] != room.get_current_turn():
            if room.is_play_first(all_users[username]):
                game.place("X", x, y)
            else:
                game.place("O", x, y)
            if len(room.get_players()) == 2:
                room.switch_turn()
        else:
            cache = room.get_cache()[0]
            if cache[3] == room.get_current_turn():
                game.place(cache[0], cache[1], cache[2])
                room.get_cache().pop(0)
                room.switch_turn()

    else:
        if room.is_play_first(all_users[username]):
            room.set_cache(["X", x, y, room.get_players()[0]])
        else:
            room.set_cache(["O", x, y, room.get_players()[1]]) #
        return

    if not handle_game_end_and_forfeit(message, username, all_users, room_name, all_rooms):
        handle_board_status(all_rooms[room_name])
        if room.get_cache() and room.get_cache()[0][3] == room.get_current_turn():
            next_msg = f"PLACE:{room.get_cache()[0][1]}:{room.get_cache()[0][2]}".split(":")
            handle_place(next_msg, room.get_current_turn().get_username(), all_users, room_name, all_rooms)

def handle_game_end_and_forfeit(message, username, all_users, room_name, all_rooms):

    room = all_rooms[room_name]
    game = room.get_game()
    board = game.get_board()
    res = ""
    for row in board:
        for cell in row:
            if cell == " ":
                res += "0"
            elif cell == "X":
                res += "1"
            else:
                res += "2"
    player1, player2 = room.get_players()
    winner = None
    FORFEIT = False
    STATUS = "0"
    DRAW = False

    if not socket_connected(player1.get_socket()):
        FORFEIT = True
        winner = player2
        STATUS = "2"
    elif not socket_connected(player2.get_socket()):
        FORFEIT = True
        winner = player1
        STATUS = "2"
    else:
        if game.player_wins("X"):
            winner = player1
        elif game.player_wins("O"):
            winner = player2
        elif game.players_draw():
            DRAW = True
        elif message[0] == "FORFEIT":
            winner = player2 if all_users[username] == player1 else player1
            FORFEIT = True
            STATUS  = "2"
        else:
            return False
    if winner or FORFEIT:
        for p in room.get_viewers() + room.get_players():
            message = f"GAMEEND:{res}:{STATUS}:{winner.get_username()}\n".encode("ascii")
            try:
                p.get_socket().send(message)
            except Exception as e:
                print("Something went wrong")
    elif DRAW:
        for p in room.get_viewers() + room.get_players():
            message = f"GAMEEND:{res}:1\n".encode("ascii")
            try:
                p.get_socket().send(message)
            except Exception as e:
                print("Something went wrong")
    for p in room.get_viewers() + room.get_players():
        p.set_room(None)
    del all_rooms[room_name]
    return True


def socket_connected(sock):
    try:
        sock.send(b'')
        return True
    except Exception:
        return False