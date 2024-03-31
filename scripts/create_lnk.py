import winshell
from os_tools import current_user

def create_lnk(target, arguments, link, icon):
    try:
        winshell.CreateShortcut(
            Path=link,
            Target=target,
            Arguments=f'"{arguments}"',
            Icon=(icon, 0),
            Description="Shortcut to my script"
        )
        print(f"Successfully Created shortcut: C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\kaboom.lnk")
    except Exception as e:
        print("Failed to create shortcut:", e)

kaboom_path = f"C:\\Program Files\\kaboom"
script_path = "C:\\Program Files\\kaboom\\main.py"
icon_path = f"{kaboom_path}/images/logo-light.ico"
create_lnk(
    "C:\\Users\\ethan\\AppData\\Local\\Programs\\Python\\Python312\\pythonw.exe",
    script_path,
    f"C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\kaboom.lnk",
    icon_path
)