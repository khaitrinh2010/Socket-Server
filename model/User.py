class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_authenticated = False
        self.socket = None
        self.room = None
    def set_authenticated(self, is_authenticated):
        self.is_authenticated = is_authenticated
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password
    def get_socket(self):
        return self.socket
    def set_socket(self, socket):
        self.socket = socket
    def set_room(self, room):
        self.room = room
    def get_room(self):
        return self.room