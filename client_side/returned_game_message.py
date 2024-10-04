def handle_return_in_progress(message):
    message = message.split(":")
    player1, player2 = message[1], message[2]
    return f"Match between {player1} and {player2} is in progress, it is currently {player1}'s turn."

def handle_return_board_status(message):
    message = message.split(":")
    board = message[1]
    return f"{board}"

def handle_return_game_end(message, is_player, username):
    message = message.split(":")
    board = message[1]
    status = message[2]
    winner = message[3]
    if status == "0":
        if is_player:
            if winner == username:
                return f"Congratulations, you won!"
            else:
                return f"Sorry you lost. Good luck next time!"
        else:
            return  f"{winner} has won this game!"
    elif status == "1":
        return f"Game ended in a draw."
    elif status == "2":
        return f"{winner} won due to the opposing player forfeiting."

