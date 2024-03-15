import os, pathlib, subprocess, config, toml, re, webbrowser, math
import win32com.client as win32
from pathlib import Path

with open("config.toml", "r") as f:
    config = toml.loads(f.read())

def current_user() -> str:
    return os.getlogin()

def launch_program(program):
    subprocess.Popen(program)

def launch_program_cwd(program, cwd):
    subprocess.Popen(program, cwd=cwd)

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

def list_steam_games(search_text):
    steam_path = config["Settings"]["steam_path"]
    steam_apps_path = f"{steam_path}\\steamapps\\common"
    steam_games = os.listdir(steam_apps_path)
    narrowed_list = []
    for game in steam_games:
        if remove_specials(search_text) in remove_specials(game):
            narrowed_list.append(game)
    return narrowed_list

def list_bs_instances(search_text):
    bsman_path = config["Settings"]["bsman_path"].replace("<CURRENT_USER>", current_user())
    bsman_instances = os.listdir(bsman_path)
    narrowed_list = []
    for instance in bsman_instances:
        if remove_specials(search_text) in remove_specials(instance):
            narrowed_list.append(instance)
    return narrowed_list

def get_steam_appid(game_name):
    steam_directory = config["Settings"]["steam_path"] + "\\steamapps"
    for file in os.listdir(steam_directory):
        if file.endswith('.acf'):
            with open(os.path.join(steam_directory, file), 'r', encoding="utf-8") as f:
                content = f.read()
                if game_name.lower() in content.lower():
                    appid = re.search(r'"appid"\s+"(\d+)"', content)
                    if appid:
                        return appid.group(1)
    return None

def is_calculation(s):
    try:
        eval(s, {"__builtins__": None, **math.__dict__})
        return True
    except Exception as e:
        return False

def remove_specials(string):
    unwanted_chars = [" ", ".", "-", "_", "(", ")", "&", "'", ",", "!", "?", ":", ";", "=", "+", "[", "]", "{", "}", "|", "\\", "/", "<", ">", "~", "`", "@", "#", "$", "%", "^", "*"]
    for char in unwanted_chars:
        string = string.replace(char, "")
    return string.lower()

def narrow_down(search_text):
    program_list = list_programs()
    narrowed_list = []
    if search_text.startswith("steam:"):
        narrowed_list = list_steam_games(search_text.split("steam:")[1])
    elif search_text.startswith("bsman:"):
        narrowed_list = list_bs_instances(search_text.split("bsman:")[1])
    elif is_calculation(search_text):
        try:
            result = eval(search_text, {"__builtins__": None, **math.__dict__})
            narrowed_list = [str(result)]
        except Exception as e:
            narrowed_list = ["Calculator Error: " + str(e).title()]
    else:
        for program in program_list:
            if not config["Settings"]["verbatim_search"]:
                search_text_ = remove_specials(search_text)
                program_ = remove_specials(program)
            else:
                search_text_ = search_text
                program_ = program
            if search_text_ in program_:
                narrowed_list.append(program)
        if len(narrowed_list) == 0:
            narrowed_list = [config["Settings"]["no_results_text"]]
    return narrowed_list

def run_shortcut(shortcut: str):
    shell = win32.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut)
    subprocess.Popen([shortcut.Targetpath] + shortcut.Arguments.split(), cwd=shortcut.WorkingDirectory)


def determine_program(string):
    narrowed_list = narrow_down(string)
    if len(narrowed_list) > 0:
        if string.startswith("steam:"):
            appid = get_steam_appid(narrowed_list[0])
            webbrowser.open(f"steam://rungameid/{appid}")
        elif string.startswith("bsman:"):
            launch_program_cwd(f"{config['Settings']['bsman_path'].replace('<CURRENT_USER>', current_user())}\\{narrowed_list[0]}\\Beat Saber.exe", f"{config['Settings']['bsman_path'].replace('<CURRENT_USER>', current_user())}\\{narrowed_list[0]}")
        else:
            file_name = narrowed_list[0]
            shortcut_path = Path('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
            if not shortcut_path.exists():
                shortcut_path = Path(f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
            run_shortcut(str(shortcut_path))

def load_themes():
    themes = []
    for file in os.listdir("themes"):
        if file.endswith(".qss"):
                themes.append(file)
    return themes

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
