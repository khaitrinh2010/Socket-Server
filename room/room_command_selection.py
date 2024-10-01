from room_management import join_room, create_room, room_list
def handle_room_message(message, all_rooms, clients, client_socket):
    message = message.split(":")
    code = message[0]
    if code == "JOIN":
        return join_room(message, all_rooms, clients, client_socket)
    elif code == "CREATE":
        return create_room(message, all_rooms)
    elif code == "ROOMLIST":
        return room_list(all_rooms, message)
