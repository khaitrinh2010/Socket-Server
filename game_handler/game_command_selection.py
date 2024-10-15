from game_handler.game_management import handle_place, handle_game_end_and_forfeit
def handle_game_command(message, username, all_users, room_name, all_rooms):
    message = message.split(":")
    code = message[0]
    if code == "PLACE":
        handle_place(message, username, all_users, room_name, all_rooms)
    elif code == "FORFEIT":
        handle_game_end_and_forfeit(message, username, all_users, room_name, all_rooms)
