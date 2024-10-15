import json
import sys

import bcrypt

from model.User import User

def find_by_username(username, path):
    print(username)
    # FIRST RETURN VALUE INDICATES IF THERE IS A USER IN THE DATABASE YET
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        sys.stderr.write("File not found")
        return None
    if not data:
        return None
    for user in data:
        if user['username'] == username:
            return user
    return None

def save_user(username, password,path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):  # Handle missing or invalid file
        data = []
    data.append({'username': username, 'password': password})
    with open(path, 'w') as f:
        json.dump(data, f)

def handle_login(message, path, sock, all_users):
    username = message[1]
    password = message[2]
    user = find_by_username(username, path)
    if not user:
        sock.send("LOGIN:ACKSTATUS:1".encode('ascii'))
        return None
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        try:
            foundUser = all_users[username]
            foundUser.set_authenticated(True)
            foundUser.set_socket(sock)
        except Exception as e:
            print(e)
        sock.send("LOGIN:ACKSTATUS:0".encode('ascii'))
        return username
    else:
        sock.send("LOGIN:ACKSTATUS:2")
        return None


def handle_register(message, path, sock, all_users):
    username, password = message[1], message[2]
    if find_by_username(username, path):
        sock.send("REGISTER:ACKSTATUS:1".encode('ascii'))
        return
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    save_user(username, hashed_password, path)

    #CREATE AND SAVE A NEW USER
    new_user = User(username, hashed_password)
    all_users[username] = new_user
    sock.send("REGISTER:ACKSTATUS:0".encode('ascii'))