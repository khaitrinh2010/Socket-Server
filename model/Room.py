class Room:
    def __init__(self, name, viewers, players, game):
        self.name = name
        self.viewers = []
        self.players = []
        self.current_turn = None
        self.game = game # EACH ROOM WILL HAVE A UNIQUE GAME INSTANCE
    def add_viewer(self, viewer):
        self.viewers.append(viewer)
    def add_player(self, player):
        self.players.append(player)
    def set_name(self, name):
        self.name = name
    def get_players(self):
        return self.players
    def get_name(self):
        return self.name
    def get_viewers(self):
        return self.viewers
    def get_current_turn(self):
        return self.current_turn
    def get_next_turn(self):
        return self.players[1] if self.current_turn == self.players[0] else self.players[0]
    def set_current_turn(self):
        self.current_turn = self.players[0]
    def switch_turn(self):
        self.current_turn = self.players[1] if self.current_turn == self.players[0] else self.players[0]