import os, pathlib, subprocess
import win32com.client as win32
from pathlib import Path

def current_user() -> str:
    return os.getlogin()

def launch_program(program):
    subprocess.Popen(program)

def list_programs() -> list:
    directories = [
        'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs',
        f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs'
    ]
    lnk_files = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".lnk"):
                    relative_path = Path(root).relative_to(directory)
                    lnk_files.append(str(Path(relative_path) / file))
    return lnk_files

def narrow_down(search_text):
    program_list = list_programs()
    narrowed_list = []
    for program in program_list:
        if search_text.lower() in program.lower():
            narrowed_list.append(program)
    return narrowed_list

def run_shortcut(shortcut: str):
    shell = win32.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut)
    launch_program(shortcut.Targetpath)

def determine_program(string):
    narrowed_list = narrow_down(string)
    file_name = narrowed_list[0]
    run_shortcut(f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\{narrowed_list[0]}")

def cli():
    program_list = list_programs()
    for i in range(0, len(program_list)):
        if program_list[i] == "Immersive Control Panel.lnk":
            program_display_name = "Control Panel"
        else:
            program_display_name = program_list[i].split(".lnk")[0]
            program_display_name = program_display_name.split("\\")[-1]
        print(f"{i + 1}. {program_display_name}")
    chosen_program = input("Enter program index: ")
    run_shortcut(f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\{program_list[int(chosen_program) - 1]}")
