def handle_begin(all_rooms, socket_to_user):
    for room_name in all_rooms:
        room = all_rooms[room_name]
        players = room.get_players()
        if len(players) == 2:
            player1, player2 = players
            begin_message = f"BEGIN:{player1.get_username()}:{player2.get_username()}".encode('ascii')
            sent_participants = set()
            for participant in players + room.get_viewers():
                if participant not in sent_participants:
                    user_socket = participant.get_socket()
                    if user_socket:
                        try:
                            user_socket.send(begin_message)
                            sent_participants.add(participant)
                        except Exception as e:
                            print(f"Failed to send BEGIN message to {participant.get_username()}: {e}")
            handle_board_status(room)


def handle_in_progress(room):
    for viewers in room.get_viewers():
        current_player = room.get_current_turn().get_username()
        next_player = room.get_next_turn().get_username()
        viewers.get_socket().send(f"INPROGRESS:{current_player}:{next_player}".encode('ascii'))

def handle_board_status(room):
    game = room.get_game()
    board = game.get_board()
    for p in room.get_viewers() + room.get_players():
        message = f"BOARDSTATUS:{board}".encode("ascii")
        try:
            p.get_socket().send(message)
        except Exception as e:
            print("Something went wrong")
    handle_in_progress(room)

def handle_place(message, username, all_users, room_name, all_rooms):
    x, y = int(message[1]), int(message[2])
    room = all_rooms[room_name]
    game = room.get_game()
    if room.is_play_first(all_users[username]):
        game.place("X", x, y)
        room.switch_turn()
    else:
        game.place("O", x, y)
        room.switch_turn()
    handle_board_status(all_rooms[room_name])
    handle_game_end_and_forfeit(message, username, all_users, room_name, all_rooms)

def handle_game_end_and_forfeit(message, username, all_users, room_name, all_rooms):

    room = all_rooms[room_name]
    game = room.get_game()
    board = game.get_board()
    player1, player2 = room.get_players()
    winner = None
    FORFEIT = False
    STATUS = "0"
    DRAW = False

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
        return

    if winner or FORFEIT:
        for p in room.get_viewers() + room.get_players():
            message = f"GAMEEND:{board}:{STATUS}:{winner.get_username()}".encode("ascii")
            try:
                p.get_socket().send(message)
            except Exception as e:
                print("Something went wrong")
    elif DRAW:
        for p in room.get_viewers() + room.get_players():
            message = f"GAMEEND:{board}:1".encode("ascii")
            try:
                p.get_socket().send(message)
            except Exception as e:
                print("Something went wrong")
    del all_rooms[room_name]
