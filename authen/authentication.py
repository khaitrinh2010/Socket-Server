import json
import sys

import bcrypt

def find_by_username(username, path):
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

def save_user(username, password, path):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):  # Handle missing or invalid file
        data = []
    data.append({'username': username, 'password': hashed_password})
    with open(path, 'w') as f:
        json.dump(data, f)

def handle_login(message, path, clients, sock):
    username = message[0]
    password = message[1]
    user = find_by_username(username, path)
    if not user:
        return "LOGIN:ACKSTATUS:1"
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        clients[sock]["authenticated"] = True
        return "LOGIN:ACKSTATUS:0"
    else:
        return "LOGIN:ACKSTATUS:2"

def handle_register(username, password, path):
    if find_by_username(username, path):
        return "REGISTER:ACKSTATUS:1"
    save_user(username, password, path)
    return "REGISTER:ACKSTATUS:0"