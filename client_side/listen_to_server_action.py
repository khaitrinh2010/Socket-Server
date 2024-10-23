def handle_return_begin(message):
    message = message.strip().split(":")
    if message[0] == "BEGIN":
        player1, player2 = message[1], message[2]
        return f"Match between {player1} and {player2} will commence, it is currently {player1}'s turn."
    return None