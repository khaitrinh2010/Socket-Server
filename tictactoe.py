from game import Game
#comment

def tic_tac_toe() -> None:
    # Modify this function in any way you like
    game = Game()
    board = game.create_board()
    player = game.CROSS

    game_won = game_drawn = False
    while not game_won and not game_drawn:
        print(game.get_board())
        print()
        # turn = "Noughts'" if player == game_handler.NOUGHT else "Crosses'"
        # print(turn, "turn")

        position = game.player_turn(player)
        # Implement any relevant logic here for sending the position/board
        print()

        if game.player_wins(player):
            game_won = True
        elif game.players_draw():
            game_drawn = True
        else:
            player = game.NOUGHT if player == game.CROSS else game.CROSS

    print(game.get_board())
    print()

    if game_won:
        pass
        # winner = "Noughts" if player == game_handler.NOUGHT else "Crosses"
        # print(winner, "wins!")
    elif game_drawn:
        print("Draw!")

if __name__ == "__main__":
    tic_tac_toe()