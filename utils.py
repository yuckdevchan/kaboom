import os, pathlib, subprocess, toml, re, webbrowser, math, platform
if platform.system() == "Windows":
    import win32com.client as win32
    import winreg
    from plyer import notification
elif platform.system() == "Linux":
    import configparser
from pathlib import Path
from scripts.config_tools import get_config, get_core_config, get_program_directory
from scripts.os_tools import current_user
from everything_api import search
from setproctitle import setproctitle
from PIL import Image

setproctitle("kaboom")

with open(get_config(), "r") as f:
    config = toml.loads(f.read())

with open(get_core_config(), "r") as f:
    core_config = toml.loads(f.read())

def get_windows_theme():
    if platform.system() == "Windows":
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')
        value, regtype = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return 'light' if value == 1 else 'dark'
    else:
        return "dark"

windows_directories = [
    'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs',
    f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs'
]

linux_directories = [
    '/usr/share/applications', 
    f'/home/{current_user()}/.local/share/applications'
]

macos_directories = [
    '/Applications'
]

def launch_program(program):
    subprocess.Popen(program)

def launch_program_cwd(program, cwd):
    print("OK")
    subprocess.Popen(program, cwd=cwd)

def list_msstore_apps() -> list:
    msstore_apps = []
    if platform.system() == "Windows":
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Classes\\ActivatableClasses\\Package')
        for i in range(winreg.QueryInfoKey(key)[0]):
            subkey_name = winreg.EnumKey(key, i)
            if subkey_name.startswith("microsoft.windowsstore"):
                continue
            msstore_apps.append(subkey_name + ".kaboom.Microsoft Store App")
    return msstore_apps

def list_programs() -> list:
    max_results = config["Settings"]["max_results"]
    if platform.system() == "Windows":
        lnk_files = []
        lnk_file_names = []
        for directory in windows_directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".lnk") and not file == "kaboom.lnk" and file.rsplit("\\")[-1] not in lnk_file_names:
                        relative_path = Path(root).relative_to(directory)
                        lnk_files.append(str(Path(relative_path) / file))
                        lnk_file_names.append(file)
        program_list = lnk_files
    elif platform.system() == "Linux":
        desktop_files = []
        for directory in linux_directories:
            for file_ in os.listdir(directory):
                if file_.endswith(".desktop"):
                    desktop_files.append(str(file_))
        program_list = desktop_files
    elif platform.system() == "Darwin":
        program_list = []
        for directory in macos_directories:
            for file in os.listdir(directory):
                if file.endswith(".app"):
                    program_list.append(file)
                program_list.append(file)
    program_list = [program + ".kaboom.Program" for program in program_list]
    kaboom_programs = [
        f"Open {core_config['Settings']['program_title']} Settings.kaboom.Kaboom Settings",
        f"Reset {core_config['Settings']['program_title']} Settings.kaboom.Kaboom Settings",
        f"Exit {core_config['Settings']['program_title']}.kaboom.Kaboom Settings",
        f"Open {core_config['Settings']['program_title']} Notes.kaboom.Kaboom Settings",
    ]
    program_list += kaboom_programs
    program_list = sorted(program_list)
    apps_list = list_msstore_apps()
    return program_list + apps_list

def list_steam_games(search_text):
    steam_path = config["Settings"]["steam_path"].replace("<CURRENT_USER>", current_user())
    steam_apps_path = Path(steam_path, "steamapps", "common")
    if os.path.exists(steam_apps_path):
        steam_games = os.listdir(steam_apps_path)
        narrowed_list = []
        for game in steam_games:
            if remove_specials(search_text) in remove_specials(game):
                narrowed_list.append(game + ".kaboom.Steam Game")
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
            narrowed_list = ["No Beat Saber Versions Found..kaboom.None"]
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
        if (("*" in s or "/" in s or "-" in s or "+" in s or "sqrt" in s) or (s == "e") or (s == "pi") or ("sin(" in s)) and (not is_youtube_url(s)):
            return True
    except Exception:
        return False
    return False

weight_units = {
    ("kg", "kilogram", "kilograms"): 1,
    ("g", "gram", "grams", "grammes"): 1000,
    ("mg", "milligram", "milligrams"): 1_000_000,
    ("mcg", "microgram", "micrograms"): 1_000_000,
    ("ng", "nanogram", "nanograms"): 1_000_000_000,
    ("pg", "picogram", "picograms"): 1_000_000_000_000,
    ("fg", "femtogram", "femtograms"): 1_000_000_000_000_000,
    ("ag", "attogram", "attograms"): 1_000_000_000_000_000_000,
    ("zg", "zeptogram", "zeptograms"): 1_000_000_000_000_000_000_000,
    ("yg", "yoctogram", "yoctograms"): 1_000_000_000_000_000_000_000_000,
    ("lb", "lbs", "pound", "pounds"): 2.20462,
    ("oz", "ounce", "ounces"): 35.274,
    ("st", "stone", "stones"): 0.157473,
    ("t", "tonne", "tonnes"): 0.001,
    ("cwt", "hundredweight", "hundredweights"): 0.0196841,
}

length_units = {
    ("m", "meter", "metre", "meters", "metres"): 1,
    ("cm", "centimeter", "centimetre", "centimeters", "centimetres"): 100,
    ("km", "kilometer", "kilometre", "kilometers", "kilometres"): 0.001,
    ("mm", "millimeter", "millimetre", "millimeters", "millimetres"): 1000,
    ("um", "micrometer", "micrometre", "micrometers", "micrometres"): 1_000_000,
    ("nm", "nanometer", "nanometre", "nanometers", "nanometres"): 1_000_000_000,
    ("pm", "picometer", "picometre", "picometers", "picometres"): 1_000_000_000_000,
    ("fm", "femtometer", "femtometre", "femtometers", "femtometres"): 1_000_000_000,
    ("am", "attometer", "attometre", "attometers", "attometres"): 1_000_000_000_000,
    ("zm", "zeptometer", "zeptometre", "zeptometers", "zeptometres"): 1_000_000,
    ("ym", "yoctometer", "yoctometre", "yoctometers", "yoctometres"): 1_000_000_000,
    ("mi", "mile", "miles"): 0.000621371,
    ("yd", "yard", "yards"): 1.09361,
    ("ft", "foot", "feet"): 3.28084,
    ("in", "inch", "inches"): 39.3701,
    ("nmi", "nautical mile", "nautical miles"): 0.000539957,
    ("au", "astronomical unit", "astronomical units"): 6.68459e-12,
    ("ly", "light-year", "light-years", "lightyear", "lightyears"): 1.057e-16,
    ("pc", "parsec", "parsecs"): 3.24078e-17,
    ("ft", "foot", "feet"): 3.28084,
    ("ft", "foot", "feet"): 3.28084,
    ("in", "inch", "inches"): 39.3701,
    ("yd", "yard", "yards"): 1.09361,
    ("mi", "mile", "miles"): 0.000621371,
}

volume_units = {
    ("l", "liter", "litre", "liters", "litres"): 1,
    ("ml", "milliliter", "millilitre", "milliliters", "millilitres"): 1000,
    ("cm^3", "cc", "cubic centimeter", "cubic centimetre", "cubic centimeters", "cubic centimetres"): 1000,
    ("m^3", "cubic meter", "cubic metre", "cubic meters", "cubic metres"): 0.001,
    ("ft^3", "cubic foot", "cubic feet"): 0.0353147,
    ("in^3", "cubic inch", "cubic inches"): 61.0237,
    ("gal", "gallon", "gallons"): 0.264172,
    ("qt", "quart", "quarts"): 1.05669,
    ("pt", "pint", "pints"): 2.11338,
    ("cup", "cups"): 4.22675,
    ("fl oz", "fluid ounce", "fluid ounces"): 33.814,
}

time_units = {
    ("s", "second", "seconds"): 1,
    ("ms", "millisecond", "milliseconds"): 1000,
    ("min", "minute", "minutes"): 0.0166667,
    ("h", "hour", "hours"): 0.000277778,
    ("d", "day", "days"): 0.0000115741,
    ("wk", "week", "weeks"): 0.00000165344,
    ("mo", "month", "months"): 0.000000380517,
    ("y", "year", "years"): 0.0000000316881,
}

byte_units = {
    ("bit", "bits"): 1,
    ("byte", "bytes"): 0.125,
    ("kb", "kilobyte", "kilobytes"): 0.00012207,
    ("mb", "megabyte", "megabytes"): 1.1921e-7,
    ("gb", "gigabyte", "gigabytes"): 1.16415e-10,
    ("tb", "terabyte", "terabytes"): 1.13687e-13,
    ("pb", "petabyte", "petabytes"): 1.11022e-16,
    ("eb", "exabyte", "exabytes"): 1.0842e-19,
    ("zb", "zettabyte", "zettabytes"): 1.05879e-22,
    ("yb", "yottabyte", "yottabytes"): 1.03398e-25,
}

units = [weight_units, length_units, volume_units, time_units, byte_units]

def conversion(text):
    text = text.lower()
    if "to" in text.split(" ") or "in" in text.split(" "):
        if "to" in text.split(" "):
            text = text.split("to")
        elif "in" in text.split(" "):
            text = text.split("in")
        unit = text[1].strip()
        try:
            value, from_unit = text[0].strip().split()
        except ValueError:
            print(f"Task Failed Sucessfully (Caught Error): \nValueError: not enough values to unpack (expected 2, got 1)\n\nBug Report URL: {core_config['Settings']['bug_report_url']}")
            return None
        from_unit_in_key = False
        unit_in_key = False
        for unit_dict in units:
            unit_dict_keys = unit_dict.keys()
            for key in unit_dict_keys:
                if from_unit in key:
                    from_unit_in_key = True
                if unit in key:
                    unit_in_key = True
        if from_unit_in_key and unit_in_key:
            from_unit_value = None
            to_unit_value = None
            for unit_dict in units:
                for key, conversion_factor in unit_dict.items():
                    if from_unit in key:
                        from_unit_value = conversion_factor
                    if unit in key:
                        to_unit_value = conversion_factor
            if from_unit_value and to_unit_value:
                # Convert the value to the base unit (e.g., meters, kilograms)
                value_in_base_unit = float(value) / from_unit_value

                # Convert the value in the base unit to the target unit
                value_in_target_unit = value_in_base_unit * to_unit_value
                if value_in_target_unit.is_integer():
                    value_in_target_unit = int(value_in_target_unit)
                result = [value_in_target_unit, unit]
                return result

    return None

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

def is_youtube_url(text):
    text = text.replace("https://", "").replace("http://", "").replace("www.", "")
    if text.startswith("youtube.com/watch?v=") or text.startswith("youtu.be/") or text.startswith("youtube.com/playlist?list=") or text.startswith("youtube.com/shorts"):
        return True
    else:
        return False

def download_youtube(text, format):
    url = text
    download_format = None
    if format == "Download Video: Original Quality":
        download_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio"
    elif format == "Download Video: 1080p":
        download_format = "bestvideo[height<=1080]+bestaudio[ext=m4a]/bestvideo+bestaudio"
    if format is not None:
        subprocess.Popen(f'yt-dlp -f "{download_format}" {url}', shell=True)
        return ["Downloading Video..."]
    else:
        if format == "Download Video: 720p":
            download_format = "bestvideo[height<=720]+bestaudio"
        elif format == "Download Audio: Original Quality":
            download_format = "bestaudio"
        subprocess.Popen(f'yt-dlp -x --audio-format mp3 -f "{download_format}" {url}', shell=True)
        return ["Downloading Audio..."]

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
            # add commas to large numbers
            if len(narrowed_list[0]) > 3:
                narrowed_list[0] = "{:,}".format(result)
        except Exception as e:
            narrowed_list = ["Error: " + str(e).title()]
    elif search_text.startswith("web:") and config["Settings"]["search_web"]:
        narrowed_list = ["Press Enter to Search the Web."]
    elif is_youtube_url(search_text):
        narrowed_list = ["Download Video: Original Quality", "Download Video: 1080p", "Download Video: 720p", "Download Audio: Original Quality"]
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
    max_results = config["Settings"]["max_results"]
    narrowed_list = narrowed_list[:max_results]
    if config["Settings"]["search_filesystem"] and len(search_text) > 3:
        files_list = search(search_text)
        files_list = [file + ".kaboom.Image File" if is_image(file) else file + "kaboom.File" for file in files_list]
        narrowed_list += files_list
    if len(narrowed_list) == 0:
        narrowed_list = [core_config["Settings"]["no_results_text"]]
    return narrowed_list

def is_image(path):
    try:
        Image.open(path)
        return True
    except Exception:
        return False

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        # app_icon=str(os.path.abspath(Path("images", "logo-light.ico"))),
        timeout=60,
    )

def run_shortcut(shortcut: str):
    if platform.system() == "Windows":
        shell = win32.Dispatch("WScript.Shell")
        try:
            shortcut = shell.CreateShortCut(shortcut)
        except Exception as e:
            print(f"Task Failed Sucessfully (Caught Error): \n{e}")
            send_notification("Task Failed Sucessfully", f"Failed to launch program.\n\nBug Report URL: {core_config['Settings']['bug_report_url']}")
            return
        print(f"Launched '{shortcut.Targetpath} {shortcut.Arguments}'")
        try:
            subprocess.Popen([shortcut.Targetpath] + shortcut.Arguments.split())
        except OSError:
            subprocess.Popen(f'start "" "{shortcut.Targetpath}" {shortcut.Arguments}', shell=True)
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
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", shortcut])

def determine_program(string: str):
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
            elif platform.system() == "Darwin":
                shortcut_path = Path('/Applications') / narrowed_list[0]
            run_shortcut(str(shortcut_path))

def program_name_to_shortcut(program_name: str) -> Path:
    narrowed_list = narrow_down(program_name)
    file_name = narrowed_list[0]
    if platform.system() == "Windows":
        shortcut_path = Path('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
        if not shortcut_path.exists():
            shortcut_path = Path(f'C:\\Users\\{current_user()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs') / narrowed_list[0]
    elif platform.system() == "Linux":
        shortcut_path = Path('/usr/share/applications') / narrowed_list[0]
        if not shortcut_path.exists():
            shortcut_path = Path(f'/home/{current_user()}/.local/share/applications') / narrowed_list[0]
    elif platform.system() == "Darwin":
        shortcut_path = Path('/Applications') / narrowed_list[0]
    return Path(shortcut_path)

def load_themes():
    themes = []
    for file in os.listdir(f"{get_program_directory()}/themes"):
        if file.endswith(".toml"):
                themes.append(file)
    return themes

def load_qt_styles():
    qt_styles = []
    for file in os.listdir(f"{get_program_directory()}/themes"):
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
