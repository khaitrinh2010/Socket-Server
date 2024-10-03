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
    handle_board_status(all_rooms)


def handle_in_progress(all_rooms):
    for room_name in all_rooms:
        room = all_rooms[room_name]
        if len(room.get_players()) == 2:
            for viewers in room.get_viewers():
                current_player = room.get_current_turn()
                next_player = room.get_next_turn()
                viewers.get_socket().send(f"INPROGRESS:{current_player}:{next_player}".encode('ascii'))

def handle_board_status(all_rooms):
    for room_name in all_rooms:
        room = all_rooms.get(room_name)
        game = room.get_game()
        board = game.create_board()
        board = game.get_board(board)
        for p in room.get_viewers() + room.get_players():
            message = f"BOARDSTATUS:{board}".encode("ascii")
            try:
                p.get_socket().send(message)
            except Exception as e:
                print("Something went wrong")