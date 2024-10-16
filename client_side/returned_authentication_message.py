import sys
def check_bad_auth(response):
    code = response.split(":")[0]
    if code == "BADAUTH":
        return "Error: You must be logged in to perform this action"
    return None

def handle_return_login(response: str, username):
    bad_auth_msg = check_bad_auth(response)
    if bad_auth_msg:
        return bad_auth_msg
    if bad_auth_msg:
        return bad_auth_msg
    status = response.split(":")[2]
    if status == "0":
        return f"Welcome {username}"
    elif status == "1":
        return f"User {username} not found"
    elif status == "2":
        return f"Wrong password for user {username}"
    else:
        return "Unknown error during login process"

def handle_return_register(response: str, username):
    bad_auth_msg = check_bad_auth(response)
    if bad_auth_msg:
        return bad_auth_msg
    status = response.split(":")[2]
    if status == "0":
        return f"Successfully created user account {username}"
    elif status == "1":
        return f"Error: User {username} already exists"