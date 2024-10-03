def handle_return_in_progress(message):
    message = message.split(":")
    player1, player2 = message[1], message[2]
    return f"Match between {player1} and {player2} is in progress, it is currently {player1}'s turn."

def handle_return_board_status(message):
    message = message.split(":")
    board = message[1]
    return f"{board}"