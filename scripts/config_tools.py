import platform, os
from pathlib import Path
from scripts.os_tools import current_user

windows_config_directories = [
    f"C:\\Users\\{current_user()}\\AppData\\Local\\kaboom"
]

linux_config_directories = [
    "~/.config/kaboom"
]

macos_config_directories = [
    "~/Library/Application Support/kaboom"
]

windows_program_directory = f"C:\\Program Files\\kaboom"
linux_program_directory = "/usr/share/kaboom"
macos_program_directory = "/Applications/kaboom"

def get_config() -> Path:
    config = None
    if platform.system() == "Windows":
        config_dirs = windows_config_directories
    elif platform.system() == "Linux":
        config_dirs = linux_config_directories
    elif platform.system() == "Darwin":
        config_dirs = macos_config_directories
    else:
        raise Exception("Unsupported platform")
    for directory in config_dirs:
        if os.path.exists(Path(directory, "config.toml")):
            config = Path(directory, "config.toml")
            break
    if config is None:
        default_config = Path("configs", f"default-{platform.system().lower().replace('darwin', 'macos')}.toml")
        with open(default_config, "r") as f:
            os.makedirs(config_dirs[0], exist_ok=True)
            with open(Path(config_dirs[0], "config.toml"), "w") as f2:
                f2.write(f.read())
        config = get_config()
    return os.path.abspath(Path(config))

def get_program_directory() -> Path:
    if platform.system() == "Windows":
        return Path(windows_program_directory)
    elif platform.system() == "Linux":
        return Path(linux_program_directory)
    elif platform.system() == "Darwin":
        return Path(macos_program_directory)
    else:
        raise Exception("Unsupported platform")

def get_core_config() -> Path:
    if platform.system() == "Windows":
        return Path(f"{windows_program_directory}\\configs\\core.toml")
    elif platform.system() == "Linux":
        return Path(f"{linux_program_directory}/configs/core.toml")
    elif platform.system() == "Darwin":
        return Path(f"{macos_program_directory}/configs/core.toml")