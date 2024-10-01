class User:
    def __init__(self, username, password, sock):
        self.username = username
        self.password = password
        self.is_authenticated = False
        self.socket = sock # EACH USER HAS A UNIQUE SOCKET CONNECTION TO THE SERVER
    def set_authenticated(self, is_authenticated):
        self.is_authenticated = is_authenticated
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password