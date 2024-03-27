import sys, toml, os, platform, subprocess, signal, psutil, PySide6
from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect, QStyle, QStyleFactory, QApplication, QSystemTrayIcon, QMenu, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Slot, QTimer, QUrl
from PySide6.QtGui import QIcon, QPainterPath, QColor, QFont
from PySide6.QtMultimedia import QMediaPlayer
from PySide6 import QtCore, QtWidgets, QtGui
from pathlib import Path

if platform.system() == "Windows":
    import keyboard
    import wmi

from utils import list_programs, narrow_down, determine_program, load_qt_styles, load_themes, is_calculation, get_windows_theme

class SettingsPopup2(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config['Settings']['program_title']} Settings")
        self.resize(600, 100)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)
        self.first_tab = QtWidgets.QWidget(self)
        self.second_tab = QtWidgets.QWidget(self)
        self.third_tab = QtWidgets.QWidget(self)
        self.fourth_tab = QtWidgets.QWidget(self)
        self.fifth_tab = QtWidgets.QWidget(self)
        self.sixth_tab = QtWidgets.QWidget(self)
        self.tab_widget.addTab(self.first_tab, "&Appearance")
        self.tab_widget.addTab(self.second_tab, "&Compositing")
        self.tab_widget.addTab(self.third_tab, "&Search")
        self.tab_widget.addTab(self.fifth_tab, "&Music")
        self.tab_widget.addTab(self.fourth_tab, "Config &File")
        self.tab_widget.addTab(self.sixth_tab, "A&bout")

        # First tab
        self.first_tab_layout = QtWidgets.QVBoxLayout(self.first_tab)
        
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
        with open(Path("themes", f"{config['Settings']['theme']}.toml"), "r") as theme_file:
            theme = toml.load(theme_file)
            theme_styles = list(theme.keys())
            for i in range(len(theme_styles)):
                self.theme_style_radio = QtWidgets.QRadioButton(theme_styles[i].title(), self)
                self.theme_style.addButton(self.theme_style_radio)
                self.first_tab_layout.addWidget(self.theme_style_radio)
        self.theme_style_radio = self.theme_style.buttons()[theme_styles.index(config["Settings"]["theme_style"].lower())]
        self.theme_style_radio.setChecked(True)
        self.theme_style.buttonClicked.connect(self.change_theme_radio)

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

        self.translucent_background_switch = QtWidgets.QCheckBox("Translucent Background (Requires Restart)", self)
        self.translucent_background_switch.setChecked(config["Settings"]["translucent_background"])
        self.translucent_background_switch.stateChanged.connect(self.change_translucent_background)
        self.second_tab_layout.addWidget(self.translucent_background_switch)

        # third tab
        self.third_tab_layout = QtWidgets.QGridLayout(self.third_tab)

        self.verbatim_search_switch = QtWidgets.QCheckBox("Verbatim Search", self)
        self.verbatim_search_switch.setChecked(config["Settings"]["verbatim_search"])
        self.verbatim_search_switch.stateChanged.connect(self.change_verbatim_search)
        self.third_tab_layout.addWidget(self.verbatim_search_switch)

        self.default_search_label = QtWidgets.QLabel("Default Search Engine:", self)
        self.third_tab_layout.addWidget(self.default_search_label)

        self.default_search_engine_combobox = QtWidgets.QComboBox(self)
        search_engines = []
        for search_engine in config["Search_Engines"].keys(): search_engines.append(search_engine.title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com").replace("Youtube", "YouTube"))
        self.default_search_engine_combobox.addItems(search_engines)
        self.default_search_engine_combobox.setCurrentText(config["Settings"]["default_search_engine"].title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com").replace("Youtube", "YouTube"))
        self.default_search_engine_combobox.currentTextChanged.connect(self.change_default_search_engine)
        self.third_tab_layout.addWidget(self.default_search_engine_combobox)

        self.no_results_text_label = QtWidgets.QLabel("No Results Text:", self)
        self.third_tab_layout.addWidget(self.no_results_text_label)

        self.no_results_text_input = QtWidgets.QLineEdit(self)
        self.no_results_text_input.setText(config["Settings"]["no_results_text"])
        self.no_results_text_input.textChanged.connect(self.change_no_results_text)
        self.third_tab_layout.addWidget(self.no_results_text_input)

        self.search_start_menu_switch = QtWidgets.QCheckBox("Start Menu", self)
        self.search_start_menu_switch.setChecked(config["Settings"]["search_start_menu"])
        self.search_start_menu_switch.stateChanged.connect(self.change_search_start_menu)
        self.third_tab_layout.addWidget(self.search_start_menu_switch)

        self.search_calculator_switch = QtWidgets.QCheckBox("Calculator", self)
        self.search_calculator_switch.setChecked(config["Settings"]["search_calculator"])
        self.search_calculator_switch.stateChanged.connect(self.change_search_calculator)
        self.third_tab_layout.addWidget(self.search_calculator_switch)

        self.search_web_switch = QtWidgets.QCheckBox("Web", self)
        self.search_web_switch.setChecked(config["Settings"]["search_web"])
        self.search_web_switch.stateChanged.connect(self.change_search_web)
        self.third_tab_layout.addWidget(self.search_web_switch)

        self.search_steam_switch = QtWidgets.QCheckBox("Steam", self)
        self.search_steam_switch.setChecked(config["Settings"]["search_steam"])
        self.search_steam_switch.stateChanged.connect(self.change_search_steam)
        self.third_tab_layout.addWidget(self.search_steam_switch)

        self.search_bsman_switch = QtWidgets.QCheckBox("BSManager", self)
        self.search_bsman_switch.setChecked(config["Settings"]["search_bsman"])
        self.search_bsman_switch.stateChanged.connect(self.change_search_bsman)
        self.third_tab_layout.addWidget(self.search_bsman_switch)

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
        self.bgm_file_combobox.addItems([file for file in os.listdir("sounds") if file.endswith(".mp3") or file.endswith(".wav")])
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
        self.kaboom_logo.setPixmap(QtGui.QPixmap(str(Path(f"images/logo-{theme}.svg"))))
        self.sixth_tab_layout.addWidget(self.kaboom_logo)

        self.kaboom_info_title = QtWidgets.QLabel("Kaboom Info:", self)
        self.kaboom_info_title.setStyleSheet("font-weight: bold;")
        self.sixth_tab_layout.addWidget(self.kaboom_info_title)

        self.kaboom_info = QtWidgets.QLabel(f"Config File Location: {os.path.abspath('config.toml')}\nProgram Version: {config['Settings']['program_version']}", self)
        self.sixth_tab_layout.addWidget(self.kaboom_info)

        self.your_pc_info_title = QtWidgets.QLabel("Your PC Info:", self)
        self.your_pc_info_title.setStyleSheet("font-weight: bold;")
        self.sixth_tab_layout.addWidget(self.your_pc_info_title)

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

    def change_bgm(self, state):
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            config['Settings']['bgm_volume'] = value / 100
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            self.parent().player.audio_set_volume(value)

    def change_bgm_file(self, text):
        with open('config.toml', 'r+') as file:
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

    def showEvent(self, event):
        with open('config.toml', 'r') as file:
            config = toml.load(file)

    def change_theme(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['dark_mode'] = False
                self.setStyleSheet(f"background-color: {config['Setting']['light_mode_bg']}; color: {config['Settings']['light_mode_text']};")
                self.parent().setStyleSheet(f"background-color: {config['Settings']['light_mode_bg']}; color: {config['Settings']['light_mode_text']};")
                self.parent().settings_button.setIcon(QIcon("images/settings-light.svg"))
                self.parent().exit_button.setIcon(QIcon("images/exit-light.svg"))
                self.parent().clear_text_button.setIcon(QIcon("images/clear-light.svg"))
                self.parent().hide_button.setIcon(QIcon("images/hide-light.svg"))
                self.parent().search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + config["Settings"]["light_mode_text"] + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")
            elif state == 2:
                config['Settings']['dark_mode'] = True
                self.setStyleSheet(f"background-color: {config['Settings']['dark_mode_bg']}; color: {config['Settings']['dark_mode_text']};")
                self.parent().setStyleSheet(f"background-color: {config['Settings']['dark_mode_bg']}; color: {config['Settings']['dark_mode_text']};")
                self.parent().settings_button.setIcon(QIcon("images/settings-dark.svg"))
                self.parent().exit_button.setIcon(QIcon("images/exit-dark.svg"))
                self.parent().clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
                self.parent().hide_button.setIcon(QIcon("images/hide-dark.svg"))
                self.parent().search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + config["Settings"]["dark_mode_text"] + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_to_dark_icons(self, fg_colour):
        self.parent().settings_button.setIcon(QIcon("images/settings-dark.svg"))
        self.parent().exit_button.setIcon(QIcon("images/exit-dark.svg"))
        self.parent().hide_button.setIcon(QIcon("images/hide-dark.svg"))
        self.parent().clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
        self.parent().search_bar.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + fg_colour + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")

    def change_to_light_icons(self, fg_colour):
        self.parent().settings_button.setIcon(QIcon("images/settings-light.svg"))
        self.parent().exit_button.setIcon(QIcon("images/exit-light.svg"))
        self.parent().hide_button.setIcon(QIcon("images/hide-light.svg"))
        self.parent().clear_text_button.setIcon(QIcon("images/clear-light.svg"))
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
        with open(Path("themes", f"{state}.toml"), "r") as file:
            theme = toml.load(file)
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
            if dark:
                self.change_to_dark_icons(fg_colour=theme[theme_style]["foreground"])
            else:
                self.change_to_light_icons(fg_colour=theme[theme_style]["foreground"])

    def change_theme_radio(self, checked):
        self.change_theme2(self.themes_combobox.currentText())

    def change_colour_overlay(self, state):
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
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
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            config['Settings']['opacity'] = value / 100
            file.seek(0)
            toml.dump(config, file)
            file.truncate()
            self.parent().setWindowOpacity(value / 100)

    def change_draggable_window(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['draggable_window'] = False
            elif state == 2:
                config['Settings']['draggable_window'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_sidebar_mode(self, state):
        with open('config.toml', 'r+') as file:
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

    def change_verbatim_search(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['verbatim_search'] = False
            elif state == 2:
                config['Settings']['verbatim_search'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_default_search_engine(self, text):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            config['Settings']['default_search_engine'] = text.lower().replace("ask.com", "askcom")
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_no_results_text(self, text):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            config['Settings']['no_results_text'] = text
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_start_menu(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_start_menu'] = False
            elif state == 2:
                config['Settings']['search_start_menu'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_calculator(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_calculator'] = False
            elif state == 2:
                config['Settings']['search_calculator'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_web(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_web'] = False
            elif state == 2:
                config['Settings']['search_web'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_steam(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_steam'] = False
            elif state == 2:
                config['Settings']['search_steam'] = True
            file.seek(0)
            toml.dump(config, file)
            file.truncate()

    def change_search_bsman(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['search_bsman'] = False
            elif state == 2:
                config['Settings']['search_bsman'] = True
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
            with open('config.toml', 'w') as file:
                toml.dump(default_config, file)
            sys.exit()

    def edit_toml(self):
        os.system("start config.toml")

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        with open('config.toml', 'r') as file:
            config = toml.load(file)
            with open(Path("themes", f"{config['Settings']['theme']}.toml"), "r") as theme_file:
                theme = toml.load(theme_file)
                theme_style = config["Settings"]["theme_style"].lower()
                bg_color = theme[theme_style]["background"]
                fg_color = theme[theme_style]["foreground"]
                text_color = theme[theme_style]["text"]
                icon_color = theme[theme_style]["icons"]
                global dark
                dark = theme[theme_style]["dark"]
            self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")

        if platform.system() == "Windows":
            keyboard.add_hotkey(config["Settings"]["hotkey"], self.toggle_window)
            keyboard.add_hotkey("escape", self.escape_pressed)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.textbox_layout = QtWidgets.QHBoxLayout()
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setPlaceholderText("Start typing to search...")
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
        self.exit_button = QtWidgets.QPushButton(self)
        self.exit_button.setToolTip(f"Exit {config['Settings']['program_title']}")
        self.exit_button.setFlat(True)
        self.exit_button.setStyleSheet(self.button_style)
        self.hide_button = QtWidgets.QPushButton(self)
        self.hide_button.setStyleSheet(self.button_style)
        self.hide_button.setToolTip(f"Hide {config['Settings']['program_title']}")

        self.clear_text_button = QtWidgets.QPushButton(self)
        self.clear_text_button.setToolTip("Clear Text Field")
        self.clear_text_button.setFlat(True)
        self.clear_text_button.setStyleSheet(self.button_style)
        self.clear_text_button.clicked.connect(self.search_bar.clear)
        self.clear_text_button.clicked.connect(self.search_bar.setFocus)
        self.hide_button.clicked.connect(self.toggle_window)
        self.exit_button.clicked.connect(sys.exit)

        if dark:
            self.settings_button.setIcon(QIcon("images/settings-dark.svg"))
            self.exit_button.setIcon(QIcon("images/exit-dark.svg"))
            self.hide_button.setIcon(QIcon("images/hide-dark.svg"))
            self.clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
        else:
            self.settings_button.setIcon(QIcon("images/settings-light.svg"))
            self.exit_button.setIcon(QIcon("images/exit-light.svg"))
            self.hide_button.setIcon(QIcon("images/hide-light.svg"))
            self.clear_text_button.setIcon(QIcon("images/clear-light.svg"))

        self.textbox_layout.addWidget(self.search_bar)
        self.textbox_layout.addWidget(self.clear_text_button)
        self.textbox_layout.addWidget(self.exit_button)
        self.textbox_layout.addWidget(self.hide_button)
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
""")
        self.scroll_area.setWidget(self.buttons_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)

        if config["Settings"]["search_bar_location"] == "bottom":
            self.layout.addLayout(self.textbox_layout)
            self.layout.addWidget(self.scroll_area)
        else:
            self.layout.addLayout(self.textbox_layout)
            self.layout.addWidget(self.scroll_area)

        self.search_bar.textChanged.connect(self.on_text_changed)
        self.search_bar.returnPressed.connect(self.on_enter_pressed)
        self.settings_button.clicked.connect(self.open_settings)

        program_list = list_programs()
        program_list = sorted([program.rsplit("\\")[-1] for program in program_list])
        text = ""
        for i in range(len(program_list)):
            # text += program_list[i].replace(".lnk", "").replace(".desktop", "").rsplit("\\")[-1] + "\n"
            # add button
            self.button = QtWidgets.QPushButton(program_list[i].replace(".lnk", "").replace(".desktop", "").replace(".kaboom", ""), self)
            self.buttons_layout.addWidget(self.button)
            self.button.setStyleSheet("border: solid; text-align: left;")
        # self.change_text(text)

        self.m_drag = False
        self.m_DragPosition = QtCore.QPoint()

        with open('config.toml', 'r') as file:
            config = toml.load(file)
            self.draggable_window = config["Settings"]["draggable_window"]


    def update_font_size(self):
        # volume = self.player.audio_get_volume()
        # print(int(volume))
        # font = self.textbox.font()
        # font.setPointSize(volume)
        # self.textbox.setFont(font)
        pass

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
        
    def toggle_window(self):
        with open ('config.toml', 'r') as file:
            config = toml.load(file)
        if config["Settings"]["auto_pause_bgm"] and config["Settings"]["bgm"]:
            self.player.pause()
        # if minimized
        if not self.windowState() == QtCore.Qt.WindowMinimized:
            self.hide()
            self.setWindowState(QtCore.Qt.WindowMinimized)
        else:
            self.setWindowState(QtCore.Qt.WindowNoState)
            self.show()
            widget.activateWindow()
            self.search_bar.setFocus()
            if platform.system() == "Windows":
                self.tabtip_process = subprocess.Popen("C:\\Program Files\\Common Files\\microsoft shared\\ink\\TabTip.exe", shell=True)

    def tray_toggle_window(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window()

    def center_window(self):
        widget.move((QtWidgets.QApplication.primaryScreen().size().width() - widget.width()) / 2, (QtWidgets.QApplication.primaryScreen().size().height() - widget.height()) / 2)

    def escape_pressed(self):
        if self.isVisible:
            self.hide()

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
        for i in reversed(range(self.buttons_layout.count())):
            widget = self.buttons_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    @QtCore.Slot()
    def on_text_changed(self, text):
        self.remove_buttons()
        narrowed_list = narrow_down(text)
        if is_calculation(self.search_bar.text()):
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
            new_text = f"={new_text.replace("inf", "Basically ∞").replace("nan", "Not a Number")}"
            self.button = QtWidgets.QPushButton(new_text, self)
            self.button.setStyleSheet("border: none; text-align: left;")
            self.button.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(new_text.strip("=")))
            self.buttons_layout.addWidget(self.button)
        else:
            new_text = ""
            for i in range(len(narrowed_list)):
                # new_text += narrowed_list[i].replace(".lnk", "").replace(".desktop", "").rsplit("\\")[-1] + "\n"
                self.button = QtWidgets.QPushButton(narrowed_list[i].replace(".lnk", "").replace(".desktop", "").replace(".kaboom", "").rsplit("\\")[-1], self)
                self.button.setStyleSheet("border: none; text-align: left;")
                self.buttons_layout.addWidget(self.button)
        print(new_text)


    @QtCore.Slot()
    def change_text(self, text):
        # self.label.setText(text)
        # self.label.setToolTip(text)
        with open('config.toml', 'r') as file:
            config = toml.load(file)
            # self.label.setFixedWidth(config["Settings"]["width"])
            # self.label.setFixedHeight(config["Settings"]["height"])

    @QtCore.Slot()
    def on_enter_pressed(self):
        program = narrow_down(self.search_bar.text())[0]
        if self.search_bar.text() == "exit":
            sys.exit()
        elif self.buttons_layout.count() == 1 and self.buttons_layout.itemAt(0).widget().text() == config["Settings"]["no_results_text"]:
            self.search_bar.clear()
        elif program.endswith(".kaboom"):
            if program == "Open kaboom Settings.kaboom":
                self.search_bar.clear()
                self.open_settings()
            elif program == "Reset kaboom Settings.kaboom":
                self.search_bar.clear()
                self.reset_settings_confirmation()
            elif program == "Exit kaboom.kaboom":
                sys.exit()
        else:
            determine_program(self.search_bar.text())
            self.search_bar.clear()
            self.toggle_window()

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
    with open('config.toml', 'r') as file:
        config = toml.load(file)

    if platform.system() == "Windows":
        windows_theme = get_windows_theme()

    app = QApplication([])
    app.setStyle("macos" if platform.system() == "Darwin" else "Fusion")
    app.setWindowIcon(QIcon(str(Path("images", f"logo-light.svg"))))

    if platform.system() == "Linux":
        timer = QTimer()
        timer.timeout.connect(check_file)
        timer.start(0.1)

    widget = MainWindow()
    widget.setWindowFlag(QtCore.Qt.Window)

    tray = QSystemTrayIcon()
    # tray.setIcon(QIcon(str(Path("images", f"logo-{'light' if windows_theme == 'dark' else 'dark'}.svg"))))
    tray.setIcon(QIcon(str(Path("images", f"logo-dark.svg"))))
    tray.setVisible(True)
    tray.setToolTip(f"{config['Settings']['program_title']}")

    menu = QMenu()
    
    menu.addAction(QIcon(str(Path("images", f"logo-light.svg"))), config["Settings"]["program_title"])

    show_action = menu.addAction(QIcon(str(Path("images", f"hide-light.svg"))), "&Toggle")
    settings_action = menu.addAction(QIcon(str(Path("images", f"settings-light.svg"))), "&Preferences")
    reset_position_action = menu.addAction(QIcon(str(Path("images", f"center-light.svg"))), "&Reset Position")
    exit_action = menu.addAction(QIcon(str(Path("images", f"exit-light.svg"))), "&Quit")
    tray.setContextMenu(menu)

    tray.activated.connect(widget.tray_toggle_window)
    show_action.triggered.connect(widget.toggle_window)
    settings_action.triggered.connect(widget.open_settings)
    reset_position_action.triggered.connect(widget.center_window)
    exit_action.triggered.connect(sys.exit)

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
    widget.setWindowTitle(config["Settings"]["program_title"])
    if config["Settings"]["sidebar_mode"]:
        widget.move(0, 0)
        widget.setFixedHeight(QtWidgets.QApplication.primaryScreen().size().height())
    else:
        widget.move((QtWidgets.QApplication.primaryScreen().size().width() - widget.width()) / 2, (QtWidgets.QApplication.primaryScreen().size().height() - widget.height()) / 2)

    widget.show()
    if config["Settings"]["bgm"]:
        import vlc
        QtCore.QTimer.singleShot(0, widget.play_audio)

    sys.exit(app.exec())