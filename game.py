from typing import Optional

class Game:
    NOUGHT = 'O'
    CROSS = 'X'
    EMPTY = ' '

    BOARD_SIZE = 3
    CELL_SIZE = 5

    ROW_SEPARATOR = '-'
    COLUMN_SEPARATOR = '|'
    N_ROW_SEPARATORS = CELL_SIZE + (CELL_SIZE - 1) * (BOARD_SIZE - 1)
    BOARD = ""

    ##########################################################
    #################### Private Methods #####################
    ##########################################################
    def __init__(self):
        self.BOARD = self.create_board()

    def _player_wins_vertically(self, player: str, board: list[list[str]]) -> bool:
        return any(
            all(board[y][x] == player for y in range(self.BOARD_SIZE))
            for x in range(self.BOARD_SIZE)
        )

    def _player_wins_horizontally(self, player: str, board: list[list[str]]) -> bool:
        return any(
            all(board[x][y] == player for y in range(self.BOARD_SIZE))
            for x in range(self.BOARD_SIZE)
        )

    def _player_wins_diagonally(self, player: str, board: list[list[str]]) -> bool:
        return (
            all(board[y][y] == player for y in range(self.BOARD_SIZE)) or
            all(board[self.BOARD_SIZE - 1 - y][y] == player for y in range(self.BOARD_SIZE))
        )

    def _try_read_value(self, prompt: str) -> Optional[int]:
        try:
            value = int(input(prompt))
        except ValueError:
            return None
        return value if 1 <= value < self.BOARD_SIZE + 1 else None

    def _empty_board_position(self, board: list[list[str]]) -> tuple[int, int]:
        while True:
            while (column := self._try_read_value(f"Column: ")) is None:
                print(f"Column values must be between 1 and {self.BOARD_SIZE}")

            while (row := self._try_read_value(f"Row: ")) is None:
                print(f"Row values must be between 1 and {self.BOARD_SIZE}")

            x = column - 1
            y = row - 1
            if (occupant := board[y][x]) == self.EMPTY:
                return (y, x)
            print(f"({column}, {row}) is occupied by {occupant}")

    ##########################################################
    #################### Public Methods ######################
    ##########################################################

    def create_board(self) -> list[list[str]]:
        """Create a new board"""
        return [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]

    def get_board(self, board: list[list[str]]) -> str:
        """Return the board as a formatted string instead of printing"""
        output = [self.ROW_SEPARATOR * self.N_ROW_SEPARATORS]
        for row in board:
            row_str = self.COLUMN_SEPARATOR.join(f" {value} " for value in row)
            output.append(f"{self.COLUMN_SEPARATOR}{row_str}{self.COLUMN_SEPARATOR}")
            output.append(self.ROW_SEPARATOR * self.N_ROW_SEPARATORS)
        return '\n'.join(output)

    def player_turn(self, player: str, board: list[list[str]]) -> tuple[int, int]:
        """Does a player's turn and returns the position of the turn"""
        y, x = self._empty_board_position(board)
        board[y][x] = player
        return (x + 1, y + 1)

    def player_wins(self, player: str, board: list[list[str]]) -> bool:
        """Determines whether the specified player wins given the board"""
        return (
            self._player_wins_vertically(player, board) or
            self._player_wins_horizontally(player, board) or
            self._player_wins_diagonally(player, board)
        )

    def players_draw(self, board: list[list[str]]) -> bool:
        """Determines whether the players draw on the given board"""
        return all(
            board[y][x] != self.EMPTY
            for y in range(self.BOARD_SIZE)
            for x in range(self.BOARD_SIZE)
        )
