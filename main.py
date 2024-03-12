import os, pathlib, subprocess
import win32com.client as win32

def launch_program(program):
        subprocess.check_call([f"{program}"])

def list_programs():
    start_menu_list = os.listdir("C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs")
    program_list = []
    for item in start_menu_list:
        if not item.endswith(".lnk"):
            start_menu_list.remove(item)
            program_list.append(item)
    for folder in start_menu_list:
        for item in os.listdir(f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\{folder}"):
            if item.endswith(".lnk"):
                program_list.append(f"{folder}\\{item}")
    return 

def run_shortcut(shortcut):
    shell = win32.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut)
    launch_program(shortcut.Targetpath)

def cli():
    program_list = list_programs()
    for i in range(0, len(program_list)):
        print(f"{i + 1}. {program_list[i]}")
    chosen_program = input("Enter program index: ")
    run_shortcut(f"C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\{program_list[int(chosen_program) - 1]}")

cli()