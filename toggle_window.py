import platform

if not platform.system() == "Windows":
    
    import os
    from pathlib import Path

    def change_value(filename):
        with open(filename, 'r+') as file:
            data = file.read()
            data = data.replace('0', '1')
            file.seek(0)
            file.write(data)
            file.truncate()

    abs_path = os.path.abspath(__file__)
    directory = os.path.dirname(abs_path)
    change_value(Path(directory, "toggle_window_socket"))
else:
    print("This file is only for Linux and other systems. You can safely ignore it (because you use Windows).")