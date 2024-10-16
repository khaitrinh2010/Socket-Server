class Room:
    def __init__(self, name, viewers, players, game):
        self.name = name
        self.viewers = viewers
        self.players = players
        self.current_turn = None
        self.game = game # EACH ROOM WILL HAVE A UNIQUE GAME INSTANCE
        self.is_started = False
        self.cache = []
        self.is_cache = False
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
    def set_current_turn(self,player):
        self.current_turn = player
    def switch_turn(self):
        self.current_turn = self.players[1] if self.current_turn == self.players[0] else self.players[0]
    def get_game(self):
        return self.game
    def set_game(self, game):
        self.game = game
    def is_play_first(self, player):
        return self.players[0].get_username() == player.get_username()
    def is_started(self):
        return self.is_started
    def set_started(self, is_started):
        self.is_started = is_started
    def get_cache(self):
        return self.cache
    def set_cache(self, cache):
        self.cache = cache
    def set_cache_status(self, status):
        self.is_cache = status
    def get_cache_status(self):
        return self.is_cache
