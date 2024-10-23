import sys


def handle_return_in_progress(message):
    message = message.strip().split(":")
    player1, player2 = message[1], message[2]
    return f"Match between {player1} and {player2} is in progress, it is currently {player1}'s turn."

def handle_return_board_status(message):
    message = message.strip().split(":")
    board = message[1].replace('1', 'X').replace('2', 'O').replace('0', ' ')
    row_separator = "----------"
    column_separator = "|"

    formatted_board = row_separator + "\n"
    for i in range(0, len(board), 3):
        if i == 9:
            break
        row = f" {board[i]} {column_separator} {board[i+1]} {column_separator} {board[i+2]} "
        formatted_board += row + "\n" + row_separator + "\n"

    return formatted_board

def handle_return_game_end(message, is_player, username):
    message = message.strip().split(":")
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

