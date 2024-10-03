def handle_begin(all_rooms, socket_to_user):
    for room_name in all_rooms:
        room = all_rooms[room_name]
        players = room.get_players()
        if len(players) == 2:
            room.set_current_turn()
            player1, player2 = players
            begin_message = f"BEGIN:{player1.get_username()}:{player2.get_username()}".encode('ascii')
            for participant in players + room.get_viewers():
                socket_to_user[participant.get_username()].send(begin_message)

def handle_in_progress(all_rooms):
    for room in all_rooms:
        for viewers in room.get_viewers():
            current_player = room.get_current_turn()
            next_player = room.get_next_turn()
            viewers.get_socket().send(f"INPROGRESS:{current_player}:{next_player}".encode('ascii'))