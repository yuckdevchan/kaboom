import platform, os
from pathlib import Path
from os_tools import current_user

windows_config_directories = [
    f"C:\\Users\\{current_user()}\\AppData\\Local\\kaboom"
]

linux_config_directories = [
    "~/.config/kaboom"
]

macos_config_directories = [
    "~/Library/Application Support/kaboom"
]

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
    return Path(config)

def get_core_config() -> Path:
    return Path("configs", "core.toml")