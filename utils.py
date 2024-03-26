import os, pathlib, subprocess, config, toml, re, webbrowser, math, platform
if platform.system() == "Windows":
    import win32com.client as win32
    import winreg
elif platform.system() == "Linux":
    import configparser
from pathlib import Path

with open("config.toml", "r") as f:
    config = toml.loads(f.read())

def get_windows_theme():
    if platform.system() == "Windows":
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')
        value, regtype = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return 'light' if value == 1 else 'dark'
    else:
        return "dark"

def current_user() -> str:
    return os.getlogin()

windows_directories = [
    'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs',
    f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs'
]

linux_directories = [
    '/usr/share/applications', 
    f'/home/{current_user()}/.local/share/applications'
]

def launch_program(program):
    subprocess.Popen(program)

def launch_program_cwd(program, cwd):
    subprocess.Popen(program, cwd=cwd)

def list_programs() -> list:
    if platform.system() == "Windows":
        lnk_files = []
        for directory in windows_directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".lnk"):
                        relative_path = Path(root).relative_to(directory)
                        lnk_files.append(str(Path(relative_path) / file))
        program_list = lnk_files
    elif platform.system() == "Linux":
        desktop_files = []
        for directory in linux_directories:
            for file_ in os.listdir(directory):
                if file_.endswith(".desktop"):
                    desktop_files.append(str(file_))
        program_list = desktop_files
    elif platform.system() == "Darwin":
        program_list = ["macOS is not supported."]
    return program_list

def list_steam_games(search_text):
    steam_path = config["Settings"]["steam_path"].replace("<CURRENT_USER>", current_user())
    steam_apps_path = Path(steam_path, "steamapps", "common")
    print(str(steam_apps_path))
    if os.path.exists(steam_apps_path):
        steam_games = os.listdir(steam_apps_path)
        narrowed_list = []
        for game in steam_games:
            if remove_specials(search_text) in remove_specials(game):
                narrowed_list.append(game)
    else:
        narrowed_list = ["No Steam Games Found."]
    return narrowed_list

def list_bs_instances(search_text):
    bsman_path = config["Settings"]["bsman_path"].replace("<CURRENT_USER>", current_user())
    narrowed_list = []
    if os.path.exists(bsman_path):
        if len(os.listdir()) > 0:
            bsman_instances = os.listdir(bsman_path)
            for instance in bsman_instances:
                if remove_specials(search_text) in remove_specials(instance):
                    narrowed_list.append(instance)
    else:
        if platform.system() == "Windows":
            narrowed_list = ["No Beat Saber Versions Found."]
        else:
            narrowed_list = [f"Launching Beat Saber Instances is not supported on {platform.system()}."]
    return narrowed_list

def get_steam_appid(game_name):
    if not game_name == "No Steam Games Found.":
        steam_directory = Path(config["Settings"]["steam_path"].replace("<CURRENT_USER>", current_user()), "steamapps")
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
        # eval(s, {"__builtins__": None, **math.__dict__})
        if ("*" in s or "/" in s or "-" in s or "+" in s or "sqrt" in s) or (s == "e") or (s == "pi") or ("sin(" in s):
            return True
    except Exception as e:
        return False
    
def search_web(search_text):
    with open(Path("data", "tlds.txt"), "r") as f:
        tlds = f.readlines()
        for tld in tlds:
            tld = "." + tld.replace("\n", "").lower()
            if search_text.replace("\n", "").endswith(tld):
                url = True
                break
            else:
                url = False
        if url == True:
            webbrowser.open(search_text)
            print("sorry if it opened in microsoft edge :(")
        else:
            webbrowser.open(f'{config["Search_Engines"][config["Settings"]["default_search_engine"]]}{search_text}')
    return ["Searched the web."]

def remove_specials(string):
    unwanted_chars = [" ", ".", "-", "_", "(", ")", "&", "'", ",", "!", "?", ":", ";", "=", "+", "[", "]", "{", "}", "|", "\\", "/", "<", ">", "~", "`", "@", "#", "$", "%", "^", "*"]
    for char in unwanted_chars:
        string = string.replace(char, "")
    return string.lower()

def narrow_down(search_text):
    program_list = list_programs()
    narrowed_list = []
    if search_text.startswith("steam:") and config["Settings"]["search_steam"]:
        narrowed_list = list_steam_games(search_text.split("steam:")[1])
    elif search_text.startswith("bsman:") and config["Settings"]["search_bsman"]:
        narrowed_list = list_bs_instances(search_text.split("bsman:")[1])
    elif is_calculation(search_text) and config["Settings"]["search_calculator"]:
        try:
            result = eval(search_text, {"__builtins__": None, **math.__dict__})
            narrowed_list = [str(result)]
        except Exception as e:
            narrowed_list = ["Error: " + str(e).title()]
    elif search_text.startswith("web:") and config["Settings"]["search_web"]:
        narrowed_list = ["Press Enter to Search the Web."]
    elif search_text.startswith("rizzler"):
        narrowed_list = ["""
gyatt
i was in ohio before i met you
i rizz too much and that's an issue
but I grimace shake
gyatt
tell your friends it was nice to rizz them
but i hope i never edge again
i know it breaks your fanum
taxing in ohio and i'm still not sigma
four years no livy
now you're looking pretty on adin ross twitch again
i i-i-i-i can't rizz
no i i-i-i-i can't mew
so baby gronk me closer
in the back-skibidi toilet
that i know you can't afford
kai cenat tatted on my shoulder
pull the gyatt right off the corner
from that fanum that you taxed
from your roomate back in ohio
we ain't never not the rizzler
...
we ain't never not the rizzler"""]
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
    if platform.system() == "Windows":
        shell = win32.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut)
        print(f"Launched '{shortcut.Targetpath} {shortcut.Arguments}'")
        subprocess.Popen([shortcut.Targetpath] + shortcut.Arguments.split())
    elif platform.system() == "Linux":
        config = configparser.ConfigParser(interpolation=None)
        config.read(shortcut)
        print(config.read(shortcut))

        try:
            command = config['Desktop Entry']['Exec']
            if shortcut.endswith(".desktop"):
                startin = config['Desktop Entry'].get('Path', '')
                if startin:
                    os.chdir(startin)
                subprocess.run(f'sudo -u {current_user()} {command}', shell=True)
            elif "://" in shortcut:
                webbrowser.open(command)
        except KeyError:
            print(f"No 'Exec' key found in {shortcut}")


def determine_program(string):
    narrowed_list = narrow_down(string)
    if len(narrowed_list) > 0:
        if string.startswith("steam:") and config["Settings"]["search_steam"]:
            appid = get_steam_appid(narrowed_list[0])
            if appid is not None:
                webbrowser.open(f"steam://rungameid/{appid}")
        elif string.startswith("bsman:") and config["Settings"]["search_bsman"]:
            launch_program_cwd(f"{config['Settings']['bsman_path'].replace('<CURRENT_USER>', current_user())}\\{narrowed_list[0]}\\Beat Saber.exe", f"{config['Settings']['bsman_path'].replace('<CURRENT_USER>', current_user())}\\{narrowed_list[0]}")
        elif string.startswith("web:") and config["Settings"]["search_web"]:
            search_web(string.split("web:")[1])
        else:
            file_name = narrowed_list[0]
            if platform.system() == "Windows":
                shortcut_path = Path('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
                if not shortcut_path.exists():
                    shortcut_path = Path(f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
            elif platform.system() == "Linux":
                shortcut_path = Path('/usr/share/applications') / narrowed_list[0]
                if not shortcut_path.exists():
                    shortcut_path = Path(f'/home/{current_user()}/.local/share/applications') / narrowed_list[0]
            run_shortcut(str(shortcut_path))

def load_themes():
    themes = []
    for file in os.listdir("themes"):
        if file.endswith(".toml"):
                themes.append(file)
    return themes

def load_qt_styles():
    qt_styles = []
    for file in os.listdir("themes"):
        if file.endswith(".qss"):
                qt_styles.append(file)
    return qt_styles


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
