import os, pathlib, subprocess
import win32com.client as win32
from pathlib import Path

def current_user() -> str:
    return os.getlogin()

def launch_program(program):
        print(program)
        subprocess.Popen(program)

def list_programs(directories: list) -> list:
    lnk_files = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".lnk"):
                    relative_path = Path(root).relative_to(directory)
                    lnk_files.append(str(Path(relative_path) / file))
    return lnk_files

def run_shortcut(shortcut: str):
    shell = win32.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut)
    launch_program(shortcut.Targetpath)

def cli():
    program_list = list_programs(directories)
    for i in range(0, len(program_list)):
        if program_list[i] == "Immersive Control Panel.lnk":
            program_display_name = "Control Panel"
        else:
            program_display_name = program_list[i].split(".lnk")[0]
            program_display_name = program_display_name.split("\\")[-1]
        print(f"{i + 1}. {program_display_name}")
    chosen_program = input("Enter program index: ")
    run_shortcut(f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\{program_list[int(chosen_program) - 1]}")

directories = [
    'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs',
    f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs'
]

cli()
