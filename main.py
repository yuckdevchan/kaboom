import sys, toml, os, platform, subprocess, signal, psutil, PySide6, time, threading
from PySide6.QtWidgets import QStyleFactory, QApplication, QSystemTrayIcon, QMenu, QFileIconProvider, QTextBrowser, QTextEdit
from PySide6.QtCore import Qt, Slot, QTimer, QUrl, QFileInfo, QThreadPool, QRunnable, QObject, Signal
from PySide6.QtGui import QIcon, QPainterPath, QColor, QFont, QTextCursor
from PySide6.QtMultimedia import QMediaPlayer
from PySide6 import QtCore, QtWidgets, QtGui
from markdown import markdown
from pathlib import Path

if platform.system() == "Windows":
    import keyboard, wmi, win32com, win32gui, win32ui
    from qtacrylic import WindowEffect

from utils import list_programs, narrow_down, determine_program, load_qt_styles, load_themes, is_calculation, get_windows_theme, program_name_to_shortcut, conversion
from scripts.config_tools import get_config, get_core_config, get_program_directory

class SettingsPopup2(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        with open(get_config(), 'r') as file:
            config_toml = toml.load(file)
        self.setWindowTitle(f"{core_config['Settings']['program_title']} Settings")
        self.resize(700, 100)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)
        self.first_tab = QtWidgets.QWidget(self)
        self.second_tab = QtWidgets.QWidget(self)
        self.third_tab = QtWidgets.QWidget(self)
        self.fourth_tab = QtWidgets.QWidget(self)
        self.fifth_tab = QtWidgets.QWidget(self)
        self.sixth_tab = QtWidgets.QWidget(self)
        self.seventh_tab = QtWidgets.QWidget(self)
        self.eighth_tab = QtWidgets.QWidget(self)

        self.tab_widget.addTab(self.first_tab, "&Appearance")
        self.tab_widget.addTab(self.second_tab, "&Compositing")
        self.tab_widget.addTab(self.eighth_tab, "&Plugins")
        self.tab_widget.addTab(self.third_tab, "&Search")
        self.tab_widget.addTab(self.seventh_tab, "S&tartup")
        self.tab_widget.addTab(self.fifth_tab, "&Music")
        self.tab_widget.addTab(self.fourth_tab, "Config &File")
        self.tab_widget.addTab(self.sixth_tab, "A&bout")

        # First tab
        self.first_tab_layout = QtWidgets.QVBoxLayout(self.first_tab)
        
        self.qt_style_label = QtWidgets.QLabel("Qt Style", self)
        self.qt_style_label.setStyleSheet("font-weight: bold;")
        self.first_tab_layout.addWidget(self.qt_style_label)

        self.qt_style_combobox = QtWidgets.QComboBox(self)
        qt_styles = load_qt_styles()
        qt_styles_without_file_extension = [qt_style.replace(".qss", "") for qt_style in qt_styles]
        self.qt_style_combobox.addItems(QStyleFactory.keys() + qt_styles_without_file_extension)
        self.qt_style_combobox.setCurrentText(config["Settings"]["qt_style"].replace(".qss", ""))
        self.qt_style_combobox.currentTextChanged.connect(self.change_qt_style)
        self.first_tab_layout.addWidget(self.qt_style_combobox)

        self.theme_label = QtWidgets.QLabel("Colour Theme", self)
        self.theme_label.setStyleSheet("font-weight: bold;")
        self.first_tab_layout.addWidget(self.theme_label)

        self.themes_combobox = QtWidgets.QComboBox(self)
        themes = load_themes()
        themes_without_file_extension = [theme.replace(".toml", "") for theme in themes]
        self.themes_combobox.addItems(themes_without_file_extension)
        self.themes_combobox.setCurrentText(config["Settings"]["theme"])
        self.themes_combobox.currentTextChanged.connect(self.change_theme2)
        self.first_tab_layout.addWidget(self.themes_combobox)

        self.theme_style_label = QtWidgets.QLabel("Theme Style", self)
        self.theme_style_label.setStyleSheet("font-weight: bold;")
        self.first_tab_layout.addWidget(self.theme_style_label)

        self.theme_style = QtWidgets.QButtonGroup(self)
        with open(Path(f"{get_program_directory()}/themes", f"{config['Settings']['theme']}.toml"), "r") as theme_file:
            theme = toml.load(theme_file)
            theme_styles = list(theme.keys())
            for i in range(len(theme_styles)):
                self.theme_style_radio = QtWidgets.QRadioButton(theme_styles[i].title(), self)
                self.theme_style.addButton(self.theme_style_radio)
                self.first_tab_layout.addWidget(self.theme_style_radio)
        self.theme_style_radio = self.theme_style.buttons()[theme_styles.index(config["Settings"]["theme_style"].lower())]
        self.theme_style_radio.setChecked(True)
        self.theme_style.buttonClicked.connect(self.change_theme_radio)

        # Second tab
        self.second_tab_layout = QtWidgets.QGridLayout(self.second_tab)

        self.opacity_label = QtWidgets.QLabel(f"Opacity: {int(config['Settings']['opacity'] * 100)}%", self)
        self.second_tab_layout.addWidget(self.opacity_label)

        self.opacity_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(config["Settings"]["opacity"] * 100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.second_tab_layout.addWidget(self.opacity_slider)

        self.window_animation_label = QtWidgets.QLabel("Window Animation", self)
        self.window_animation_label.setStyleSheet("font-weight: bold;")
        self.second_tab_layout.addWidget(self.window_animation_label)

        self.window_animation_combobox = QtWidgets.QComboBox(self)
        self.window_animation_combobox.addItems(["None", "Fade"])
        self.window_animation_combobox.setCurrentText(config["Settings"]["window_animation"])
        self.window_animation_combobox.currentTextChanged.connect(self.change_window_animation)
        self.second_tab_layout.addWidget(self.window_animation_combobox)

        self.draggable_window_switch = QtWidgets.QCheckBox("Draggable Window", self)
        self.draggable_window_switch.setChecked(config["Settings"]["draggable_window"])
        self.draggable_window_switch.stateChanged.connect(self.change_draggable_window)
        self.second_tab_layout.addWidget(self.draggable_window_switch)

        self.borderless_switch = QtWidgets.QCheckBox("Borderless Window", self)
        self.borderless_switch.setChecked(config["Settings"]["borderless"])
        self.borderless_switch.stateChanged.connect(self.change_borderless)
        self.second_tab_layout.addWidget(self.borderless_switch)

        self.rounded_corners_switch = QtWidgets.QCheckBox("Rounded Corners (Requires Restart and Borderless mode)", self)
        self.rounded_corners_switch.setChecked(config["Settings"]["rounded_corners"])
        self.rounded_corners_switch.stateChanged.connect(self.change_rounded_corners)
        self.second_tab_layout.addWidget(self.rounded_corners_switch)

        self.always_on_top_switch = QtWidgets.QCheckBox("Always on Top", self)
        self.always_on_top_switch.setChecked(config["Settings"]["always_on_top"])
        self.always_on_top_switch.stateChanged.connect(self.change_always_on_top)
        self.second_tab_layout.addWidget(self.always_on_top_switch)

        taskbar_name = "Dock" if platform.system() == "Darwin" else "Taskbar"
        self.hide_from_taskbar_switch = QtWidgets.QCheckBox(f"Hide from {taskbar_name}", self)
        self.hide_from_taskbar_switch.setChecked(config["Settings"]["hide_from_taskbar"])
        self.hide_from_taskbar_switch.stateChanged.connect(self.change_hide_from_taskbar)
        self.second_tab_layout.addWidget(self.hide_from_taskbar_switch)

        self.translucent_background_switch = QtWidgets.QCheckBox("Translucent Background (Requires Restart)", self)
        self.translucent_background_switch.setChecked(config["Settings"]["translucent_background"])
        self.translucent_background_switch.stateChanged.connect(self.change_translucent_background)
        self.second_tab_layout.addWidget(self.translucent_background_switch)

        # third tab
        self.third_tab_layout = QtWidgets.QGridLayout(self.third_tab)

        self.max_results_label = QtWidgets.QLabel("Max Results (Default: 6, Choose -1 for Unlimited)", self)
        self.max_results_label.setStyleSheet("font-weight: bold;")
        self.third_tab_layout.addWidget(self.max_results_label)

        self.max_results_number = QtWidgets.QSpinBox(self)
        self.max_results_number.setMinimum(-1)
        self.max_results_number.setMaximum(2000)
        self.max_results_number.setValue(config_toml["Settings"]["max_results"])
        self.max_results_number.valueChanged.connect(self.change_max_results)
        self.third_tab_layout.addWidget(self.max_results_number)

        self.verbatim_search_switch = QtWidgets.QCheckBox("Verbatim Search", self)
        self.verbatim_search_switch.setChecked(config["Settings"]["verbatim_search"])
        self.verbatim_search_switch.stateChanged.connect(self.change_verbatim_search)
        self.third_tab_layout.addWidget(self.verbatim_search_switch)

        self.no_results_text_label = QtWidgets.QLabel("No Results Text:", self)
        self.third_tab_layout.addWidget(self.no_results_text_label)

        self.no_results_text_input = QtWidgets.QLineEdit(self)
        self.no_results_text_input.setText(core_config["Settings"]["no_results_text"])
        self.no_results_text_input.textChanged.connect(self.change_no_results_text)
        self.third_tab_layout.addWidget(self.no_results_text_input)

        # fourth tab
        self.fourth_tab_layout = QtWidgets.QGridLayout(self.fourth_tab)

        self.reset_settings_button = QtWidgets.QPushButton("Reset All Settings", self)
        self.reset_settings_button.clicked.connect(self.reset_settings_confirmation)
        self.fourth_tab_layout.addWidget(self.reset_settings_button)

        self.edit_toml_button = QtWidgets.QPushButton("Edit TOML In Text Editor", self)
        self.edit_toml_button.clicked.connect(self.edit_toml)
        self.fourth_tab_layout.addWidget(self.edit_toml_button)

        self.main_layout.setSpacing(0)

        # fifth tab
        self.fifth_tab_layout = QtWidgets.QVBoxLayout(self.fifth_tab)
        
        self.bgm_switch = QtWidgets.QCheckBox("Background Music", self)
        self.bgm_switch.setChecked(config["Settings"]["bgm"])
        self.bgm_switch.stateChanged.connect(self.change_bgm)
        self.fifth_tab_layout.addWidget(self.bgm_switch)

        self.auto_pause_bgm = QtWidgets.QCheckBox("Pause Music When Hidden", self)
        self.auto_pause_bgm.setChecked(config["Settings"]["auto_pause_bgm"])
        self.auto_pause_bgm.stateChanged.connect(self.change_auto_pause_bgm)
        self.fifth_tab_layout.addWidget(self.auto_pause_bgm)

        self.bgm_file_label = QtWidgets.QLabel("Music File (Place songs in the 'sounds' folder):", self)
        self.fifth_tab_layout.addWidget(self.bgm_file_label)

        self.bgm_file_combobox = QtWidgets.QComboBox(self)
        self.bgm_file_combobox.addItems([file for file in os.listdir(f"{get_program_directory()}/sounds") if file.endswith(".mp3") or file.endswith(".wav")])
        self.bgm_file_combobox.setCurrentText(config["Settings"]["bgm_file"])
        self.bgm_file_combobox.currentTextChanged.connect(self.change_bgm_file)
        self.fifth_tab_layout.addWidget(self.bgm_file_combobox)

        self.bgm_volume_label = QtWidgets.QLabel(f"Volume: {int(config['Settings']['bgm_volume'] * 100)}%", self)
        self.fifth_tab_layout.addWidget(self.bgm_volume_label)

        self.bgm_volume_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.bgm_volume_slider.setMinimum(0)
        self.bgm_volume_slider.setMaximum(100)
        self.bgm_volume_slider.setValue(config["Settings"]["bgm_volume"] * 100)
        self.bgm_volume_slider.valueChanged.connect(self.change_bgm_volume)
        self.fifth_tab_layout.addWidget(self.bgm_volume_slider)

        # sixth tab
        self.sixth_tab_layout = QtWidgets.QVBoxLayout(self.sixth_tab)

        self.kaboom_logo = QtWidgets.QLabel(self)
        if dark:
            theme = "dark"
        else:
            theme = "light"
        self.kaboom_logo.setPixmap(QtGui.QPixmap(str(Path(f"{get_program_directory()}/images/logo-{theme}.svg"))))
        self.sixth_tab_layout.addWidget(self.kaboom_logo)

        self.kaboom_info_title = QtWidgets.QLabel(f"{core_config['Settings']['program_title']} Info:", self)
        self.kaboom_info_title.setStyleSheet("font-weight: bold;")
        self.sixth_tab_layout.addWidget(self.kaboom_info_title)

        self.kaboom_info = QtWidgets.QLabel(f"Config File Location: {os.path.abspath('config.toml')}\nProgram Version: {core_config['Settings']['program_version']}\nAuthor: {core_config['Settings']['author']}\nBug Report URL: {core_config['Settings']['bug_report_url']}", self)
        self.sixth_tab_layout.addWidget(self.kaboom_info)

        self.your_pc_info_title = QtWidgets.QLabel("Your PC Info:", self)
        self.your_pc_info_title.setStyleSheet("font-weight: bold;")
        self.sixth_tab_layout.addWidget(self.your_pc_info_title)

        # seventh tab
        self.seventh_tab_layout = QtWidgets.QVBoxLayout(self.seventh_tab)
        
        self.open_on_startup_switch = QtWidgets.QCheckBox("Open on Startup", self)
        self.open_on_startup_switch.setChecked(config["Settings"]["open_on_startup"])
        self.open_on_startup_switch.stateChanged.connect(self.change_open_on_startup)
        self.seventh_tab_layout.addWidget(self.open_on_startup_switch)

        self.open_in_background_switch = QtWidgets.QCheckBox("Open in background", self)
        self.open_in_background_switch.setChecked(config["Settings"]["open_in_background"])
        self.open_in_background_switch.stateChanged.connect(self.change_open_in_background)
        self.seventh_tab_layout.addWidget(self.open_in_background_switch)

        # eighth tab
        self.eighth_tab_layout = QtWidgets.QVBoxLayout(self.eighth_tab)

        self.search_providers_label = QtWidgets.QLabel("Search Providers", self)
        self.search_providers_label.setStyleSheet("font-weight: bold;")
        self.eighth_tab_layout.addWidget(self.search_providers_label)

        self.search_start_menu_switch = QtWidgets.QCheckBox("Start Menu Apps", self)
        self.search_start_menu_switch.setChecked(config_toml["Settings"]["search_start_menu"])
        self.search_start_menu_switch.stateChanged.connect(self.change_search_start_menu)
        self.eighth_tab_layout.addWidget(self.search_start_menu_switch)

        self.search_calculator_switch = QtWidgets.QCheckBox("Maths Processing", self)
        self.search_calculator_switch.setChecked(config_toml["Settings"]["search_calculator"])
        self.search_calculator_switch.stateChanged.connect(self.change_search_calculator)
        self.eighth_tab_layout.addWidget(self.search_calculator_switch)

        self.search_unit_conversion_switch = QtWidgets.QCheckBox("Unit Conversions", self)
        self.search_unit_conversion_switch.setChecked(config_toml["Settings"]["search_unit_conversion"])
        self.search_unit_conversion_switch.stateChanged.connect(self.change_search_unit_conversion)
        self.eighth_tab_layout.addWidget(self.search_unit_conversion_switch)

        self.filesystem_search_switch = QtWidgets.QCheckBox("Filesystem Search", self)
        self.filesystem_search_switch.setChecked(config_toml["Settings"]["search_filesystem"])
        self.filesystem_search_switch.stateChanged.connect(self.change_search_filesystem)
        self.eighth_tab_layout.addWidget(self.filesystem_search_switch)

        self.search_steam_switch = QtWidgets.QCheckBox("Steam Game Search", self)
        self.search_steam_switch.setChecked(config_toml["Settings"]["search_steam"])
        self.search_steam_switch.stateChanged.connect(self.change_search_steam)
        self.eighth_tab_layout.addWidget(self.search_steam_switch)

        self.search_bsman_switch = QtWidgets.QCheckBox("BSManager Instance Search", self)
        self.search_bsman_switch.setChecked(config_toml["Settings"]["search_bsman"])
        self.search_bsman_switch.stateChanged.connect(self.change_search_bsman)
        self.eighth_tab_layout.addWidget(self.search_bsman_switch)

        self.search_web_switch = QtWidgets.QCheckBox("Web Search", self)
        self.search_web_switch.setChecked(config_toml["Settings"]["search_web"])
        self.search_web_switch.stateChanged.connect(self.change_search_web)
        self.eighth_tab_layout.addWidget(self.search_web_switch)

        self.default_search_label = QtWidgets.QLabel("Default Search Engine:", self)
        self.eighth_tab_layout.addWidget(self.default_search_label)

        self.default_search_engine_combobox = QtWidgets.QComboBox(self)
        search_engines = []
        for search_engine in config["Search_Engines"].keys(): search_engines.append(search_engine.title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com").replace("Youtube", "YouTube"))
        self.default_search_engine_combobox.addItems(search_engines)
        self.default_search_engine_combobox.setCurrentText(config_toml["Settings"]["default_search_engine"].title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com").replace("Youtube", "YouTube"))
        self.default_search_engine_combobox.currentTextChanged.connect(self.change_default_search_engine)
        self.eighth_tab_layout.addWidget(self.default_search_engine_combobox)

        if platform.system() == "Windows":
            manufacturer_and_model = f"{wmi.WMI().Win32_ComputerSystem()[0].Manufacturer} - {wmi.WMI().Win32_ComputerSystem()[0].Model}"
        elif platform.system() == "Linux":
            try:
                with open("/sys/class/dmi/id/sys_vendor") as f:
                    manufacturer = f.read().strip()
                with open("/sys/class/dmi/id/product_name") as f:
                    model = f.read().strip()
                manufacturer_and_model = f"{manufacturer} - {model}"
            except FileNotFoundError:
                manufacturer_and_model = "Unknown"
        elif platform.system() == "Darwin":
            manufacturer_and_model = "Apple Inc. - Mac"
        self.your_pc_info = QtWidgets.QLabel(f"""OS: {platform.system()} {platform.release()} 
OS Build: {platform.version()} 
Architecture: {platform.machine().replace("AMD64", "x86_64")} 
CPU: {platform.processor()} 
RAM: {psutil.virtual_memory().total / 1024**3:.2f} GB
Disk Space: {psutil.disk_usage('/').total / 1024**3:.2f} GB
Manufacturer & Model: {manufacturer_and_model}
Python Version: {platform.python_version()}
PySide6 Version: {PySide6.__version__}
Qt Version: {PySide6.QtCore.__version__}
""", self)
        self.sixth_tab_layout.addWidget(self.your_pc_info)

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        if platform.system() == "Windows":
            self.windowFX = WindowEffect()
            self.windowFX.setAeroEffect(self.winId())

    def change_window_animation(self, text):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['window_animation'] = text
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_hide_from_taskbar(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['hide_from_taskbar'] = False
            elif state == 2:
                config['Settings']['hide_from_taskbar'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_bgm(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                if hasattr(self.parent(), "player"):
                    self.parent().player.pause()
                config['Settings']['bgm'] = False
            elif state == 2:
                if hasattr(self.parent(), "player"):
                    self.parent().player.play()
                config['Settings']['bgm'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_auto_pause_bgm(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['auto_pause_bgm'] = False
            elif state == 2:
                config['Settings']['auto_pause_bgm'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_bgm_volume(self, value):
        self.bgm_volume_label.setText(f"Volume: {value}%")
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['bgm_volume'] = value / 100
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            self.parent().player.audio_set_volume(value)

    def change_bgm_file(self, text):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['bgm_file'] = text
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            if hasattr(self.parent(), "player"):
                self.parent().player.stop()
                self.parent().player = vlc.MediaPlayer(str(Path("sounds", text)))
                self.parent().player.audio_set_volume(int(config["Settings"]["bgm_volume"] * 100))
                self.parent().player.play()

    def closeEvent(self, event):
        self.parent().search_bar.setFocus()
        global theme_toml
        global config_toml
        config_toml = toml.load(open(get_config(), 'r'))
        theme_toml = toml.load(open(Path(f"{get_program_directory()}/themes", f"{config_toml['Settings']['theme']}.toml"), "r"))

    def showEvent(self, event):
        with open(get_config(), 'r') as file:
            config = toml.load(file)

#     def change_theme(self, state):
#         with open(get_config(), 'r+') as file:
#             config = toml.load(file)
#             if state == 0:
#                 config['Settings']['dark_mode'] = False
#                 self.setStyleSheet(f"background-color: {config['Setting']['light_mode_bg']}; color: {config['Settings']['light_mode_text']};")
#                 self.parent().setStyleSheet(f"background-color: {config['Settings']['light_mode_bg']}; color: {config['Settings']['light_mode_text']};")
#                 self.parent().settings_button.setIcon(QIcon(f"{get_program_directory()}/images/settings-light.svg"))
#                 self.parent().exit_button.setIcon(QIcon(f"{get_program_directory()}/images/exit-light.svg"))
#                 self.parent().clear_text_button.setIcon(QIcon("images/clear-light.svg"))
#                 self.parent().hide_button.setIcon(QIcon("images/hide-light.svg"))
#                 self.parent().search_bar.setStyleSheet("""
#     QLineEdit {
#         border: 2px solid """ + config["Settings"]["light_mode_text"] + """;
#         border-radius: 10px;
#         padding: 0 8px;
#         selection-background-color: darkgray;
#     }
# """)
#             elif state == 2:
#                 config['Settings']['dark_mode'] = True
#                 self.setStyleSheet(f"background-color: {config['Settings']['dark_mode_bg']}; color: {config['Settings']['dark_mode_text']};")
#                 self.parent().setStyleSheet(f"background-color: {config['Settings']['dark_mode_bg']}; color: {config['Settings']['dark_mode_text']};")
#                 self.parent().settings_button.setIcon(QIcon("images/settings-dark.svg"))
#                 self.parent().exit_button.setIcon(QIcon("images/exit-dark.svg"))
#                 self.parent().clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
#                 self.parent().hide_button.setIcon(QIcon("images/hide-dark.svg"))
#                 self.parent().search_bar.setStyleSheet("""
#     QLineEdit {
#         border: 2px solid """ + config["Settings"]["dark_mode_text"] + """;
#         border-radius: 10px;
#         padding: 0 8px;
#         selection-background-color: darkgray;
#     }
# """)
#             file.seek(0)
#             toml.dump(config, file)
#             file.truncate()

    def change_to_dark_icons(self, fg_colour):
        self.kaboom_logo.setPixmap(QtGui.QPixmap(str(Path(f"{get_program_directory()}/images/logo-dark.svg"))))
        self.parent().settings_button.setIcon(QIcon(f"{get_program_directory()}/images/settings-dark.svg"))
        self.parent().exit_button.setIcon(QIcon(f"{get_program_directory()}/images/exit-dark.svg"))
        self.parent().hide_button.setIcon(QIcon(f"{get_program_directory()}/images/hide-dark.svg"))
        self.parent().clear_text_button.setIcon(QIcon(f"{get_program_directory()}/images/clear-dark.svg"))
        self.parent().search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + fg_colour + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")

    def change_to_light_icons(self, fg_colour):
        self.kaboom_logo.setPixmap(QtGui.QPixmap(str(Path(f"{get_program_directory()}/images/logo-light.svg"))))
        self.parent().settings_button.setIcon(QIcon(f"{get_program_directory()}/images/settings-light.svg"))
        self.parent().exit_button.setIcon(QIcon(f"{get_program_directory()}/images/exit-light.svg"))
        self.parent().hide_button.setIcon(QIcon(f"{get_program_directory()}/images/hide-light.svg"))
        self.parent().clear_text_button.setIcon(QIcon(f"{get_program_directory()}/images/clear-light.svg"))
        # change search bar stylesheet
        self.parent().search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + fg_colour + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")

    def change_theme2(self, state):
        with open(Path(f"{get_program_directory()}/themes", f"{state}.toml"), "r") as file:
            theme = toml.load(file)
            theme_toml = theme
            # if theme styles are different then change the theme style to the first one
            if self.theme_style.checkedButton().text().lower() not in theme.keys():
                theme_style = list(theme.keys())[0]
                self.theme_style_radio = self.theme_style.buttons()[list(theme.keys()).index(theme_style)]
                self.theme_style_radio.setChecked(True)
                # remove all current radio buttons from the group without index out of range error
                for i in range(len(theme.keys())):
                    self.theme_style.removeButton(self.theme_style.buttons()[0])
                # add radio buttons
                for i in range(len(theme.keys())):
                    self.theme_style_radio = QtWidgets.QRadioButton(list(theme.keys())[i].title(), self)
                    self.theme_style.addButton(self.theme_style_radio)
                    self.first_tab_layout.addWidget(self.theme_style_radio)
            else:
                theme_style = self.theme_style.checkedButton().text().lower()
            bg_colour = theme[theme_style]["background"]
            text_colour = theme[theme_style]["text"]
            dark = theme[theme_style]["dark"]
            self.setStyleSheet(f"background-color: {bg_colour}; color: {text_colour};")
            self.parent().setStyleSheet(f"background-color: {bg_colour}; color: {text_colour};")
            # change stylesheet of buttons in buttons_layout with hover making it foreground 2
            button_qss = "QPushButton { border: none; text-align: left; } QPushButton:hover { background-color: " + theme_toml[theme_style]["foreground2"] + "; } QPushButton:pressed { background-color: #44475A; }"
            for button in self.parent().buttons_layout.children():
                button.setStyleSheet(button_qss)
            if dark:
                self.change_to_dark_icons(fg_colour=theme[theme_style]["foreground"])
            else:
                self.change_to_light_icons(fg_colour=theme[theme_style]["foreground"])
            
            # write changes
            with open(get_config(), 'r+') as file:
                config = toml.load(file)
                config['Settings']['theme'] = state
                config['Settings']['theme_style'] = theme_style
                file.seek(0)
                toml.dump(config, file)
                file.truncate()

    def change_theme_radio(self, checked):
        self.change_theme2(self.themes_combobox.currentText())

    def change_colour_overlay(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['colour_overlay_mode'] = False
                self.dark_mode_switch.setCheckable(True)
                if config["Settings"]["dark_mode"]:
                    self.dark_mode_switch.setChecked(True)
                    bg_colour = config["Settings"]["dark_mode_bg"]
                    text_colour = config["Settings"]["dark_mode_text"]
                    self.parent().settings_button.setIcon(QIcon("images/settings-dark.svg"))
                else:
                    self.dark_mode_switch.setChecked(False)
                    bg_colour = config["Settings"]["light_mode_bg"]
                    text_colour = config["Settings"]["light_mode_text"]
                    self.parent().settings_button.setIcon(QIcon("images/settings-light.svg"))
                self.setStyleSheet(f"background-color: {bg_colour}; color: {text_colour};")
                self.parent().setStyleSheet(f"background-color: {bg_colour}; color: {text_colour};")
            elif state == 2:
                config['Settings']['colour_overlay_mode'] = True
                self.setStyleSheet(f"background-color: {config['Settings']['colour_overlay_bg']}; color: {config['Settings']['colour_overlay_text']};")
                self.parent().setStyleSheet(f"background-color: {config['Settings']['colour_overlay_bg']}; color: {config['Settings']['colour_overlay_text']};")
                self.dark_mode_switch.setCheckable(False)
                self.parent().settings_button.setIcon(QIcon("images/settings-light.svg"))
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_qt_style(self, text):
        text += ".qss"
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['qt_style'] = text
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            if text in load_themes():
                with open(Path(f"themes/{text}"), "r") as f:
                    text = f.read()
                    app.setStyleSheet(text)
            else:
                QtWidgets.QApplication.setStyle(text)

    def change_borderless(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['borderless'] = False
                self.rounded_corners_switch.setChecked(False)
                self.parent().setWindowFlags(widget.windowFlags() & ~Qt.FramelessWindowHint)
                self.parent().toggle_window()
            elif state == 2:
                config['Settings']['borderless'] = True
                self.parent().setWindowFlag(Qt.FramelessWindowHint)
                self.parent().toggle_window()
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_rounded_corners(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['rounded_corners'] = False
            elif state == 2:
                config['Settings']['rounded_corners'] = True
                config['Settings']['borderless'] = True
                self.borderless_switch.setChecked(True)
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_always_on_top(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['always_on_top'] = False
                self.parent().setWindowFlag(Qt.WindowStaysOnTopHint, False)
                self.parent().toggle_window()
            elif state == 2:
                config['Settings']['always_on_top'] = True
                self.parent().setWindowFlag(Qt.WindowStaysOnTopHint)
                self.parent().toggle_window()
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_translucent_background(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['translucent_background'] = False
            elif state == 2:
                config['Settings']['translucent_background'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_opacity(self, value):
        if len(str(value)) == 2:
            label_value = " " + str(value)
        elif len(str(value)) == 1:
            label_value = "  " + str(value)
        else:
            label_value = str(value)
        self.opacity_label.setText(f"Opacity: {label_value}%")
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['opacity'] = value / 100
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            self.parent().setWindowOpacity(value / 100)

    def change_draggable_window(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['draggable_window'] = False
            elif state == 2:
                config['Settings']['draggable_window'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_sidebar_mode(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['sidebar_mode'] = False
                self.parent().move((QtWidgets.QApplication.primaryScreen().size().width() - self.parent().width()) / 2, (QtWidgets.QApplication.primaryScreen().size().height() - self.parent().height()) / 2)
                self.parent().setFixedHeight(config["Settings"]["height"])
            elif state == 2:
                config['Settings']['sidebar_mode'] = True
                self.parent().move(0, 0)
                self.parent().setFixedHeight(QtWidgets.QApplication.primaryScreen().size().height())
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_max_results(self, value):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['max_results'] = value
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
        max_results = value

    def change_verbatim_search(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['verbatim_search'] = False
            elif state == 2:
                config['Settings']['verbatim_search'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_default_search_engine(self, text):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            config['Settings']['default_search_engine'] = text.lower().replace("ask.com", "askcom")
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_no_results_text(self, text):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            core_config['Settings']['no_results_text'] = text
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_start_menu(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_start_menu'] = False
            elif state == 2:
                config['Settings']['search_start_menu'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_calculator(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_calculator'] = False
            elif state == 2:
                config['Settings']['search_calculator'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_unit_conversion(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_unit_conversion'] = False
            elif state == 2:
                config['Settings']['search_unit_conversion'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_web(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_web'] = False
            elif state == 2:
                config['Settings']['search_web'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_steam(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_steam'] = False
            elif state == 2:
                config['Settings']['search_steam'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_bsman(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_bsman'] = False
            elif state == 2:
                config['Settings']['search_bsman'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_filesystem(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_filesystem'] = False
            elif state == 2:
                config['Settings']['search_filesystem'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_open_on_startup(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['open_on_startup'] = False
                os.system("schtasks /delete /tn Kaboom /f")
            elif state == 2:
                config['Settings']['open_on_startup'] = True
                os.system(f"schtasks /create /tn Kaboom /tr {os.path.abspath('main.py')} /sc onlogon /rl highest")
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_open_in_background(self, state):
        with open(get_config(), 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['open_in_background'] = False
            elif state == 2:
                config['Settings']['open_in_background'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def reset_settings_confirmation(self):
        # confirmation popup
        reset_popup = QtWidgets.QMessageBox(self)
        reset_popup.setWindowTitle("Warning!")
        reset_popup.setText("Warning!\nPermanently reset all settings to default?\nThe program will close.")
        reset_popup.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        reset_popup.setDefaultButton(QtWidgets.QMessageBox.No)
        reset_popup.setStyleSheet(f"background-color: {config['Settings']['light_mode_bg']}; color: {config['Settings']['light_mode_text']};")
        reset_popup.setIcon(QtWidgets.QMessageBox.Warning)
        reset_popup.buttonClicked.connect(self.reset_settings)
        reset_popup.exec()

    def reset_settings(self, button):
        if button.text() == "&Yes":
            with open(Path("configs", f'default-{platform.system().lower().replace("darwin", "macos")}.toml', 'r')) as file:
                default_config = toml.load(file)
            with open(get_config(), 'w') as file:
                toml.dump(default_config, file)
            os._exit(0)

    def edit_toml(self):
        os.system("start config.toml")

class IconLoaderSignals(QtCore.QObject):
    finished = QtCore.Signal()

class IconLoader(QRunnable):
    def __init__(self, shortcut):
        super().__init__()
        self.shortcut = shortcut
        self.signals = IconLoaderSignals()

    @Slot()
    def run(self):
        provider = QFileIconProvider()
        info = QFileInfo(self.shortcut)
        icon = QIcon(provider.icon(info))
        self.signals.finished.emit()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        with open(Path(get_program_directory(), "themes", f"{config_toml['Settings']['theme']}.toml"), "r") as theme_file:
            global theme_toml
            theme_toml = toml.load(theme_file)
            global theme_style
            theme_style = config_toml["Settings"]["theme_style"].lower()
            bg_color = theme_toml[theme_style]["background"]
            fg_color = theme_toml[theme_style]["foreground"]
            text_color = theme_toml[theme_style]["text"]
            icon_color = theme_toml[theme_style]["icons"]
            global dark
            dark = theme_toml[theme_style]["dark"]
        self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")

        if platform.system() == "Windows":
            keyboard.add_hotkey(config_toml["Settings"]["hotkey"], self.toggle_window, suppress=True)
            keyboard.add_hotkey("escape", self.escape_pressed)
            self.current_button_index = 0
            self.button_selected = False
            if config_toml["Settings"]["arrow_key_navigation"]:
                keyboard.add_hotkey("down", self.down_pressed)
                keyboard.add_hotkey("up", self.up_pressed)
            keyboard.add_hotkey("ctrl + x", self.on_yank_key_pressed)
            keyboard.add_hotkey("ctrl + y", self.on_yank_key_pressed)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.textbox_layout = QtWidgets.QHBoxLayout()
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setPlaceholderText("Start typing to search...")
        # make placeholder text bold
        font = self.search_bar.font()
        font.setPointSize(12)
        font.setBold(True)
        self.search_bar.setFont(font)
        self.search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + fg_color + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")
        self.button_style = """
    QPushButton {
        border: none;
    }
    QPushButton:hover {
        background-color: #00000000;
    }
    QPushButton:pressed {
        background-color: #00000000;
        border: none;
    }
"""
        self.settings_button = QtWidgets.QPushButton(self)
        self.settings_button.setFlat(True)
        self.settings_button.setStyleSheet(self.button_style)
        self.settings_button.setToolTip("Preferences")
        self.notes_button = QtWidgets.QPushButton(self)
        self.notes_button.setFlat(True)
        self.notes_button.setStyleSheet(self.button_style)
        self.notes_button.setToolTip("Notes")
        self.exit_button = QtWidgets.QPushButton(self)
        self.exit_button.setToolTip(f"Exit {core_config['Settings']['program_title']}")
        self.exit_button.setFlat(True)
        self.exit_button.setStyleSheet(self.button_style)
        self.hide_button = QtWidgets.QPushButton(self)
        self.hide_button.setStyleSheet(self.button_style)
        self.hide_button.setToolTip(f"Hide {core_config['Settings']['program_title']}")

        self.clear_text_button = QtWidgets.QPushButton(self)
        self.clear_text_button.setToolTip("Clear Text Field")
        self.clear_text_button.setFlat(True)
        self.clear_text_button.setStyleSheet(self.button_style)
        self.clear_text_button.clicked.connect(self.search_bar.clear)
        self.clear_text_button.clicked.connect(self.search_bar.setFocus)
        self.hide_button.clicked.connect(self.toggle_window)
        self.exit_button.clicked.connect(self.exit_program)

        if dark:
            self.settings_button.setIcon(QIcon(f"{get_program_directory()}/images/settings-dark.svg"))
            self.notes_button.setIcon(QIcon(f"{get_program_directory()}/images/notes-dark.svg"))
            self.exit_button.setIcon(QIcon(f"{get_program_directory()}/images/exit-dark.svg"))
            self.hide_button.setIcon(QIcon(f"{get_program_directory()}/images/hide-dark.svg"))
            self.clear_text_button.setIcon(QIcon(f"{get_program_directory()}/images/clear-dark.svg"))
        else:
            self.settings_button.setIcon(QIcon(f"{get_program_directory()}/images/settings-light.svg"))
            self.notes_button.setIcon(QIcon(f"{get_program_directory()}/images/notes.svg"))
            self.exit_button.setIcon(QIcon(f"{get_program_directory()}/images/exit-light.svg"))
            self.hide_button.setIcon(QIcon(f"{get_program_directory()}/images/hide-light.svg"))
            self.clear_text_button.setIcon(QIcon(f"{get_program_directory()}/images/clear-light.svg"))

        self.textbox_layout.addWidget(self.search_bar)
        self.textbox_layout.addWidget(self.clear_text_button)
        self.textbox_layout.addWidget(self.exit_button)
        self.textbox_layout.addWidget(self.hide_button)
        self.textbox_layout.addWidget(self.notes_button)
        self.textbox_layout.addWidget(self.settings_button)

        self.buttons_layout = QtWidgets.QVBoxLayout()
        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_widget.setLayout(self.buttons_layout)
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setStyleSheet("""
    QScrollBar:vertical {
        border: none;
        background: lightgrey;
        width: 12px;
        margin: 15px 0 15px 0;
        border-radius: 6px;
     }
     QScrollBar::handle:vertical {   
        background: grey;
        min-height: 30px;
        border-radius: 6px;
     }
     QScrollBar::add-line:vertical {
        border: none;
        background: none;
        height: 0px;
     }
     QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
     }
                                       
    QScrollBar:horizontal {
        border: none;
        background: lightgrey;
        height: 12px;
        margin: 0 15px 0 15px;
        border-radius: 6px;
    }
    QScrollBar::handle:horizontal {
        background: grey;
        min-width: 30px;
        border-radius: 6px;
    }
    QScrollBar::add-line:horizontal {
        border: none;
        background: none;
        width: 0px;
    }
    QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
        width: 0px;
    }                                   
""")
        self.scroll_area.setWidget(self.buttons_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        if config_toml["Settings"]["search_bar_location"] == "bottom":
            self.layout.addLayout(self.textbox_layout)
            self.layout.addWidget(self.scroll_area)
        else:
            self.layout.addLayout(self.textbox_layout)
            self.layout.addWidget(self.scroll_area)

        self.search_bar.textChanged.connect(self.on_text_changed)
        self.search_bar.returnPressed.connect(self.on_enter_pressed)
        self.notes_button.clicked.connect(self.open_notes)
        self.settings_button.clicked.connect(self.open_settings)

        if config_toml["Settings"]["search_start_menu"]:
            program_list = list_programs()[:max_results]
            program_list = sorted([program.rsplit("\\")[-1] for program in program_list])
            text = ""
            for i in range(len(program_list)):
                # text += program_list[i].replace(".lnk", "").replace(".desktop", "").rsplit("\\")[-1] + "\n"
                # add button
                self.button = QtWidgets.QPushButton(program_list[i].replace(".lnk", "").replace(".desktop", "").replace(".app", "").replace(".kaboom", ""), self)
                self.button.setToolTip("Click to launch")
                global button_qss
                button_qss = "QPushButton { border: none; text-align: left; } QPushButton:hover { background-color: " + theme_toml[theme_style]["foreground2"] + "; } QPushButton:pressed { background-color: #44475A; }"
                self.button.setStyleSheet(button_qss)
                if config["Settings"]["program_icons"]:
                    loader = IconLoader(str(program_name_to_shortcut(program_list[i])))
                    loader.signals.finished.connect(lambda icon, button=self.button: self.set_icon(icon, button))
                    QThreadPool.globalInstance().start(loader)
                self.button.clicked.connect(lambda checked=False, text=program_list[i]: self.on_button_clicked(text))
                self.buttons_layout.addWidget(self.button)
            # self.change_text(text)

        self.m_drag = False
        self.m_DragPosition = QtCore.QPoint()

        self.draggable_window = config_toml["Settings"]["draggable_window"]

        if config_toml["Settings"]["translucent_background"]:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            if platform.system() == "Windows":
                self.windowFX = WindowEffect()
                self.windowFX.setAeroEffect(self.winId())

    def set_icon(self, icon, button):
        button.setIcon(icon)

    def get_ico_from_shortcut(self, shortcut):
        provider = QFileIconProvider()
        info = QFileInfo(shortcut)
        icon = QIcon(provider.icon(info))
        return icon
    
    def on_button_clicked(self, text):
        program = narrow_down(text)[0]
        if self.buttons_layout.count() == 1 and self.buttons_layout.itemAt(0).widget().text() == core_config["Settings"]["no_results_text"]:
            self.search_bar.clear()
        elif program.endswith(".kaboom"):
            if program == "Open kaboom Settings.kaboom":
                self.search_bar.clear()
                self.open_settings()
            elif program == "Reset kaboom Settings.kaboom":
                self.search_bar.clear()
                self.reset_settings_confirmation()
            elif program == "Exit kaboom.kaboom":
                self.exit_program()
        else:
            determine_program(program)
            self.search_bar.clear()
            self.toggle_window()

    def play_audio(self):
        self.player = vlc.MediaPlayer(str(Path("sounds", config["Settings"]["bgm_file"])))

        self.player.audio_set_volume(int(config["Settings"]["bgm_volume"] * 100))
        self.player.play()

    def mousePressEvent(self, event):
        if self.draggable_window and event.button() == QtCore.Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.draggable_window and event.buttons() == QtCore.Qt.LeftButton and self.m_drag:
            self.move(self.pos() + event.globalPosition().toPoint() - self.m_DragPosition)
            self.m_DragPosition = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.m_drag = False
            self.search_bar.setFocus()
        
    def toggle_window(self):
        with open (get_config(), 'r') as file:
            config_toml = toml.load(file)
        if config["Settings"]["auto_pause_bgm"] and config["Settings"]["bgm"]:
            self.player.pause()
        if not self.windowState() == QtCore.Qt.WindowMinimized:
            self.toggle_hide()
        else:
            self.toggle_show()

    def toggle_hide(self):
        if not self.windowState() == QtCore.Qt.WindowMinimized:
            window_animation = config_toml["Settings"]["window_animation"]
            if window_animation == "Fade":
                for i in range(round(config["Settings"]["opacity"] * 100), 0, -5):
                    self.setWindowOpacity(i / 100)
                    time.sleep(0.005)
            if config["Settings"]["hide_from_taskbar"]:
                self.hide()
            self.setWindowState(QtCore.Qt.WindowMinimized)

    def toggle_show(self):
        if self.windowState() == QtCore.Qt.WindowMinimized:
            window_animation = config_toml["Settings"]["window_animation"]
            self.setWindowState(QtCore.Qt.WindowNoState)
            if config["Settings"]["hide_from_taskbar"]:
                self.show()
            if window_animation == "Fade":
                for i in range(0, round(config["Settings"]["opacity"] * 100), 5):
                    self.setWindowOpacity(i / 100)
                    time.sleep(0.005)
                self.setWindowOpacity(config["Settings"]["opacity"])
            self.activateWindow()
            if hasattr(self, "notes_textbox"):
                try:
                    self.notes_textbox.setFocus()
                except:
                    self.search_bar.setFocus()
            else:
                self.search_bar.setFocus()
            if platform.system() == "Windows":
                self.tabtip_process = subprocess.Popen("C:\\Program Files\\Common Files\\microsoft shared\\ink\\TabTip.exe", shell=True)

    def tray_toggle_window(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window()

    def center_window(self):
        widget.move((QtWidgets.QApplication.primaryScreen().size().width() - widget.width()) / 2, (QtWidgets.QApplication.primaryScreen().size().height() - widget.height()) / 2)

    def exit_program(self):
        tray.hide()
        os._exit(0)

    def escape_pressed(self):
        if widget.isVisible():
            self.toggle_window()

    def down_pressed(self):
        if widget.isVisible():
            # Reset the style of the currently active button
            self.buttons_layout.itemAt(self.current_button_index).widget().setStyleSheet("border: none; text-align: left;")

            # Move to the next button
            if self.button_selected:
                self.current_button_index += 1
            else:
                self.current_button_index = 0
                self.button_selected = True
            if self.current_button_index >= self.buttons_layout.count():
                self.current_button_index = 0  # Loop back to the first button

            # Change the style of the new active button
            self.buttons_layout.itemAt(self.current_button_index).widget().setStyleSheet("background-color: " + theme_toml[theme_style]["foreground2"] + ";" + "border: none; text-align: left;")
            self.button_selected = True
            self.search_bar.setFocus()

    def up_pressed(self):
        if widget.isVisible():
            # Reset the style of the currently active button
            self.buttons_layout.itemAt(self.current_button_index).widget().setStyleSheet("border: none; text-align: left;")

            # Move to the previous button
            if self.button_selected:
                self.current_button_index -= 1
            else:
                self.current_button_index = 0
                self.button_selected = True
            if self.current_button_index < 0:
                self.current_button_index = self.buttons_layout.count() - 1

            # Change the style of the new active button
            self.buttons_layout.itemAt(self.current_button_index).widget().setStyleSheet("background-color: " + theme_toml[theme_style]["foreground2"] + ";" + "border: none; text-align: left;")
            self.button_selected = True
            self.search_bar.setFocus()

    def open_settings(self):
        if not widget.isVisible():
            widget.show()
        settings_popup = SettingsPopup2(self)
        settings_popup.exec()

    def hide_window(self):
        widget.hide()

    def resizeEvent(self, event):
        if config["Settings"]["rounded_corners"]:
            self.setMask(self.createMask(self.rect()))

    def createMask(self, rect):
        if config["Settings"]["rounded_corners"]:
            scale_factor = 10
            scaled_rect = QtCore.QRect(0, 0, rect.width() * scale_factor, rect.height() * scale_factor)

            mask = QtGui.QBitmap(scaled_rect.size())
            mask.fill(Qt.color0)

            painter = QtGui.QPainter(mask)
            painter.setBrush(Qt.color1)
            painter.drawRoundedRect(scaled_rect, 20 * scale_factor, 20 * scale_factor)
            painter.end()

            mask = QtGui.QBitmap.fromImage(mask.scaled(rect.size()).toImage())

        return mask

    def remove_buttons(self):
        for layout_name in ['buttons_layout', 'notes_layout', 'notes_buttons_layout']:
            try:
                layout = getattr(self, layout_name)
                if layout is not None:
                    for i in reversed(range(layout.count())):
                        widget = layout.itemAt(i).widget()
                        if widget is not None:
                            widget.deleteLater()
            except AttributeError:
                pass

    def copy_calculation_to_clipboard(self, text):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        self.button.setText("Copied to Clipboard!")
        QtCore.QTimer.singleShot(1000, lambda: self.button.setText(text))

    @QtCore.Slot()
    def on_text_changed(self, text):
        if type(text) == bool:
            text = ""
        self.button_selected = False
        self.remove_buttons()
        self.revert_notes_button()
        narrowed_list = narrow_down(text)
        if is_calculation(self.search_bar.text()) and config_toml["Settings"]["search_calculator"]:
            new_text = narrowed_list[0]
            if ("life" in self.search_bar.text() or "universe" in self.search_bar.text() or "everything" in self.search_bar.text()) and ("*" in self.search_bar.text() or "+" in self.search_bar.text() or "-" in self.search_bar.text() or "/" in self.search_bar.text()):
                # self.label.setStyleSheet(f"font-size: {config['Settings']['font_size'] * 4}px;")
                new_text = "42"
            elif new_text.replace("\n", "") == "666":
                new_text = "The Number of the Beast"
            elif new_text.replace("\n", "") == "668" or new_text.replace("\n", "") == "664":
                new_text = "The Neighbour of the Beast"
            elif new_text.startswith("Error:"):
                new_text = new_text.replace("(<String>, Line 1)", "")
            elif new_text.startswith("3.14159"):
                new_text = "◯"
            new_text = f'={new_text.replace("inf", "Basically ∞").replace("nan", "Not a Number")}'
            self.button = QtWidgets.QPushButton(new_text, self)
            self.button.setStyleSheet("border: none; text-align: left;")
            self.button.setToolTip("Click to copy to clipboard.")
            self.button.setStyleSheet(f"border: none; text-align: left; font-size: {config['Settings']['font_size'] * 4}px;")
            self.button.clicked.connect(lambda: self.copy_calculation_to_clipboard(new_text.strip("=")))
            self.buttons_layout.addWidget(self.button)
        elif not conversion(text) == None and config_toml["Settings"]["search_unit_conversion"]:
            new_text = str(conversion(text))
            self.button = QtWidgets.QPushButton(new_text, self)
            self.button.setStyleSheet(f"border: none; text-align: left; font-size: {config['Settings']['font_size'] * 4}px;")
            self.button.setToolTip("Click to copy to clipboard.")
            self.button.clicked.connect(lambda: self.copy_calculation_to_clipboard(new_text))
            self.buttons_layout.addWidget(self.button)
        else:
            if config_toml["Settings"]["search_start_menu"]:
                new_text = ""
                for i in range(len(narrowed_list)):
                    # new_text += narrowed_list[i].replace(".lnk", "").replace(".desktop", "").rsplit("\\")[-1] + "\n"
                    self.button = QtWidgets.QPushButton(narrowed_list[i].replace(".lnk", "").replace(".desktop", "").replace(".app", "").replace(".kaboom", "").rsplit("\\")[-1], self)
                    self.button.setToolTip("Click to launch")
                    self.button.setStyleSheet(button_qss)
                    self.button.clicked.connect(lambda checked=False, text=narrowed_list[i]: self.on_button_clicked(text))
                    if config["Settings"]["program_icons"]:
                        self.button.setIcon(self.get_ico_from_shortcut(str(program_name_to_shortcut(narrowed_list[i]))))
                    self.buttons_layout.addWidget(self.button)

    def open_notes(self):
        self.search_bar.clear()
        self.remove_buttons()
        self.notes_textbox = QTextEdit(self)
        self.notes_textbox.setPlaceholderText("Type your notes here...")
        self.notes_textbox.setAcceptRichText(False)
        self.notes_textbox.setPlainText(self.load_notes())
        self.notes_textbox.setStyleSheet("""
        QTextEdit {
            border: 2px solid """ + theme_toml[theme_style]["foreground"] + """;
            border-radius: 10px;
            padding: 8px;
        }
        """)

        self.markdown_preview = QTextBrowser(self)
        self.markdown_preview.setStyleSheet("""
        QTextBrowser {
            border: 2px solid """ + theme_toml[theme_style]["foreground"] + """;
            border-radius: 10px;
            padding: 8px;
        }
        QTextBrowser a {
            color: """ + theme_toml[theme_style]["foreground2"] + """;
        }
        """)
        self.markdown_preview.setOpenExternalLinks(True)
        self.markdown_preview.setPlaceholderText("Your Markdown preview will appear here...")
        self.update_markdown_preview()

        self.notes_textbox.textChanged.connect(self.update_markdown_preview)

        # Create a horizontal layout and add the text box and preview to it
        self.notes_layout = QtWidgets.QHBoxLayout()
        self.notes_layout.addWidget(self.notes_textbox)
        self.notes_layout.addWidget(self.markdown_preview)

        # Add the horizontal layout to the main layout
        self.buttons_layout.addLayout(self.notes_layout)

        self.notes_textbox.setFocus()

        self.notes_confirm_button = QtWidgets.QPushButton("Save Notes", self)
        self.notes_confirm_button.setStyleSheet("""
        QPushButton {{
            border: 2px solid {};
            border-radius: 10px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {};
        }}
        QPushButton:pressed {{
            background-color: {};
        }}
        """.format(theme_toml[theme_style]['foreground'], theme_toml[theme_style]['foreground2'], theme_toml[theme_style]['foreground3']))
        self.notes_confirm_button.clicked.connect(self.save_notes)

        self.notes_confirm_and_exit_button = QtWidgets.QPushButton("Save Notes and Exit", self)
        self.notes_confirm_and_exit_button.setStyleSheet("""
        QPushButton {{
            border: 2px solid {};
            border-radius: 10px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {};
        }}
        QPushButton:pressed {{
            background-color: {};
        }}
        """.format(theme_toml[theme_style]['foreground'], theme_toml[theme_style]['foreground2'], theme_toml[theme_style]['foreground3']))
        self.notes_confirm_and_exit_button.clicked.connect(self.save_notes)
        self.notes_confirm_and_exit_button.clicked.connect(self.toggle_window)
        self.notes_confirm_and_exit_button.clicked.connect(self.remove_buttons)
        self.notes_confirm_and_exit_button.clicked.connect(self.on_text_changed)
        self.notes_confirm_and_exit_button.clicked.connect(self.revert_notes_button)

        self.notes_cancel_button = QtWidgets.QPushButton("Cancel", self)
        self.notes_cancel_button.setStyleSheet("""
        QPushButton {{
            border: 2px solid {};
            border-radius: 10px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {};
        }}
        QPushButton:pressed {{
            background-color: {};
        }}
        """.format(theme_toml[theme_style]['foreground'], theme_toml[theme_style]['foreground2'], theme_toml[theme_style]['foreground3']))
        self.notes_cancel_button.clicked.connect(self.toggle_window)
        self.notes_cancel_button.clicked.connect(self.remove_buttons)
        self.notes_cancel_button.clicked.connect(self.on_text_changed)
        self.notes_cancel_button.clicked.connect(self.revert_notes_button)
        
        self.notes_buttons_layout = QtWidgets.QHBoxLayout()
        self.notes_buttons_layout.addWidget(self.notes_confirm_button)
        self.notes_buttons_layout.addWidget(self.notes_confirm_and_exit_button)
        self.notes_buttons_layout.addWidget(self.notes_cancel_button)
        self.buttons_layout.addLayout(self.notes_buttons_layout)
        
        self.change_notes_button()

    def change_notes_button(self):
        self.notes_button.setIcon(QIcon(f"{get_program_directory()}/images/delete-{'dark' if dark else 'light'}.svg"))
        self.notes_button.clicked.connect(lambda: self.notes_textbox.setText(""))

    def revert_notes_button(self):
        self.notes_button.setIcon(QIcon(f"{get_program_directory()}/images/notes-{'dark' if dark else 'light'}.svg"))
        self.notes_button.clicked.connect(self.open_notes)

    @QtCore.Slot()
    def change_text(self, text):
        # self.label.setText(text)
        # self.label.setToolTip(text)
        with open(get_config(), 'r') as file:
            config = toml.load(file)
            # self.label.setFixedWidth(config["Settings"]["width"])
            # self.label.setFixedHeight(config["Settings"]["height"])

    @QtCore.Slot()
    def on_enter_pressed(self):
        if self.isVisible():
            if self.button_selected:
                self.button_selected = False
                self.buttons_layout.itemAt(self.current_button_index).widget().click()
            else:
                if (is_calculation(self.search_bar.text()) and config_toml["Settings"]["search_calculator"]) or conversion(self.search_bar.text()) is not None:
                    self.copy_calculation_to_clipboard(narrow_down(self.search_bar.text())[0])
                else:
                    program = narrow_down(self.search_bar.text())[0]
                    if self.search_bar.text() == "exit":
                        os._exit(0)
                    elif self.buttons_layout.count() == 1 and self.buttons_layout.itemAt(0).widget().text() == core_config["Settings"]["no_results_text"]:
                        self.search_bar.clear()
                    elif program.endswith(".kaboom"):
                        if program == "Open kaboom Settings.kaboom":
                            self.search_bar.clear()
                            self.open_settings()
                        elif program == "Reset kaboom Settings.kaboom":
                            self.search_bar.clear()
                            self.reset_settings_confirmation()
                        elif program == "Exit kaboom.kaboom":
                            self.exit_program()
                        elif program == "Open kaboom Notes.kaboom":
                            self.open_notes()
                    else:
                        determine_program(program)
                        self.search_bar.clear()
                        self.toggle_window()

    @QtCore.Slot()
    def update_markdown_preview(self):
        markdown_text = self.notes_textbox.toPlainText()
        html = markdown(markdown_text)
        
        foreground2_color = theme_toml[theme_style]["foreground2"]

        # Add a style tag to the HTML content
        styled_html = f"""
        <style>
        a {{
            color: {foreground2_color};
        }}
        </style>
        {html}
        """

        self.markdown_preview.setHtml(styled_html)

    def load_notes(self) -> str:
        notes_path = get_config()
        notes_path = Path(str(notes_path).removesuffix("config.toml"))
        try:
            with open(str(Path(notes_path, "notes.md")), "r") as file:
                notes = file.read()
                return notes
        except FileNotFoundError:
            return None

    def save_notes(self):
        notes_path = get_config()
        notes_path = Path(str(notes_path).removesuffix("config.toml"))
        with open(str(Path(notes_path, "notes.md")), "w") as file:
            file.seek(0)
            file.truncate()
            file.write(self.notes_textbox.toPlainText())

    def on_yank_key_pressed(self):
        if self.isVisible and not self.search_bar.selectedText():
            self.search_bar.clear()
            self.search_bar.setFocus()

if platform.system() == "Linux":
    def read_value_from_file(filename):
        with open(filename, 'r') as file:
            data = file.read().strip()
        return data

    def execute_code(filename):
        with open(filename, 'r+') as file:
            data = file.read()
            data = data.replace('1', '0')
            file.seek(0)
            file.write(data)
            file.truncate()
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()
            widget.activateWindow()
            widget.raise_()
            widget.search_bar.setFocus()

    def check_file():
        filename = "toggle_window_socket"
        if not os.path.exists(filename):
            with open(filename, "w") as file:
                data = "0"
                file.write(data)
                subprocess.run(f"chmod 777 {filename}", shell=True)
        value = read_value_from_file(filename)
        if value == '1':
            execute_code(filename)

if __name__ == "__main__":
    global config_path
    config_path = get_config()
    print("Config Directory: " + str(config_path))
    with open(config_path, 'r') as file:
        config = toml.load(file)
        global config_toml
        config_toml = config
        global max_results
        max_results = config_toml["Settings"]["max_results"]
    with open(get_core_config(), 'r') as file:
        global core_config
        core_config = toml.load(file)

    if platform.system() == "Windows":
        windows_theme = get_windows_theme()

    app = QApplication([])
    app.setStyle("macos" if platform.system() == "Darwin" else "Fusion")
    app.setWindowIcon(QIcon(str(Path(f"{get_program_directory()}/images", f"logo-light.svg"))))

    if platform.system() == "Linux":
        timer = QTimer()
        timer.timeout.connect(check_file)
        timer.start(0.1)

    widget = MainWindow()
    widget.setWindowFlag(QtCore.Qt.Window)

    tray = QSystemTrayIcon()
    # tray.setIcon(QIcon(str(Path("images", f"logo-{'light' if windows_theme == 'dark' else 'dark'}.svg"))))
    tray.setIcon(QIcon(str(Path(f"{get_program_directory()}/images", f"logo-dark.svg"))))
    tray.setVisible(True)
    tray.setToolTip(f"{core_config['Settings']['program_title']}")

    menu = QMenu()
    
    menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"logo-light.svg"))), core_config["Settings"]["program_title"])

    show_action = menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"hide-light.svg"))), "&Toggle")
    settings_action = menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"settings-light.svg"))), "&Preferences")
    notes_action = menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"notes-light.svg"))), "&Notes")
    reset_position_action = menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"center-light.svg"))), "&Reset Position")
    exit_action = menu.addAction(QIcon(str(Path(f"{get_program_directory()}/images", f"exit-light.svg"))), "&Quit")
    tray.setContextMenu(menu)

    tray.activated.connect(widget.tray_toggle_window)
    show_action.triggered.connect(widget.toggle_window)
    settings_action.triggered.connect(widget.open_settings)
    notes_action.triggered.connect(widget.open_notes)
    notes_action.triggered.connect(widget.toggle_show)
    reset_position_action.triggered.connect(widget.center_window)
    exit_action.triggered.connect(os._exit)

    font = QtGui.QFont(config["Settings"]["font_family"], config["Settings"]["font_size"])
    app.setFont(font)
    if config["Settings"]["borderless"]:
        widget.setWindowFlag(Qt.FramelessWindowHint)
    if config["Settings"]["always_on_top"]:
        widget.setWindowFlag(Qt.WindowStaysOnTopHint)
    if config["Settings"]["translucent_background"]:
        widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    widget.resize(config["Settings"]["width"], config["Settings"]["height"])
    widget.setWindowOpacity(config["Settings"]["opacity"])
    widget.setWindowTitle(core_config["Settings"]["program_title"])
    if config["Settings"]["sidebar_mode"]:
        widget.move(0, 0)
        widget.setFixedHeight(QtWidgets.QApplication.primaryScreen().size().height())
    else:
        widget.move((QtWidgets.QApplication.primaryScreen().size().width() - widget.width()) / 2, (QtWidgets.QApplication.primaryScreen().size().height() - widget.height()) / 2)
    
    widget.show()
    if config["Settings"]["window_animation"] == "Fade":
        widget.setWindowOpacity(0)
        for i in range(0, round(config["Settings"]["opacity"] * 100), 5):
            widget.setWindowOpacity(i / 100)
            time.sleep(0.005)
        widget.setWindowOpacity(config["Settings"]["opacity"])
    if not config["Settings"]["hide_from_taskbar"]:
        widget.toggle_window()
        widget.toggle_window()
    if config["Settings"]["open_in_background"]:
        widget.toggle_window()
    if config["Settings"]["bgm"]:
        import vlc
        QtCore.QTimer.singleShot(0, widget.play_audio)

    os._exit(app.exec())