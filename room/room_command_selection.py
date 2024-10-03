from room.room_management import join_room, create_room, room_list
def handle_room_message(message, all_rooms, all_users, username, socket_to_user, sock):
    message = message.split(":")
    code = message[0]
    if code == "JOIN":
        return join_room(message, all_rooms, all_users, username, socket_to_user, sock)
    elif code == "CREATE":
        return create_room(message, all_rooms, sock, username, all_users)
    elif code == "ROOMLIST":
        return room_list(all_rooms, message, sock)
