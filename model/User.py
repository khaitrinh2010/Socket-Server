class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_authenticated = False
    def set_authenticated(self, is_authenticated):
        self.is_authenticated = is_authenticated
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password