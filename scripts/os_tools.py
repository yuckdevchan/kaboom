import os

def current_user() -> str:
    return os.getlogin()