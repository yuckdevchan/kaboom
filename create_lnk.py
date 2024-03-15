import pylnk3
from utils import current_user

def create_lnk(path_to_python, path_to_script, path_to_lnk):
    lnk = pylnk3.Lnk()
    lnk.target = path_to_python
    lnk.arguments = path_to_script
    lnk.save(path_to_lnk)

if __name__ == "__main__":
    create_lnk("python.exe", f"C:\\Users\\{current_user()}\\Documents\\kaboom-1\\main.py", "kaboom.lnk")