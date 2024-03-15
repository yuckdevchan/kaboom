import sys, win32gui, win32con, keyboard, toml, os
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QStyle, QStyleFactory
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QPainterPath, QColor
from PySide6 import QtCore, QtWidgets, QtGui

from utils import list_programs, narrow_down, determine_program, load_themes

class SettingsPopup(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{config["Settings"]["program_title"]} Settings")

        # Main layout
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Checkboxes layout
        self.checkboxes_layout = QtWidgets.QVBoxLayout()
        self.message_label = QtWidgets.QLabel("Settings are saved automatically.", self)
        self.colours_label = QtWidgets.QLabel("Colours", self)
        self.dark_mode_switch = QtWidgets.QCheckBox("Dark Mode", self)
        self.colour_overlay_switch = QtWidgets.QCheckBox("Colour Overlay", self)
        self.qt_style_label = QtWidgets.QLabel("Qt Style", self)
        self.qt_style_combobox = QtWidgets.QComboBox(self)
        self.compositing_label = QtWidgets.QLabel("Compositing", self)
        self.borderless_switch = QtWidgets.QCheckBox("Borderless (Requires Restart)", self)
        self.rounded_corners_switch = QtWidgets.QCheckBox("Rounded Corners (Requires Restart and Borderless mode)", self)
        self.always_on_top_switch = QtWidgets.QCheckBox("Always on Top (Requires Restart)", self)
        self.translucent_background_switch = QtWidgets.QCheckBox("Translucent Background (Requires Restart)", self)
        self.checkboxes_layout.addWidget(self.message_label)
        self.message_label.setStyleSheet("font-style: italic; color: grey;")
        self.checkboxes_layout.addWidget(self.colours_label)
        self.colours_label.setStyleSheet("font-weight: bold;")
        self.checkboxes_layout.addWidget(self.dark_mode_switch)
        self.checkboxes_layout.addWidget(self.colour_overlay_switch)
        self.checkboxes_layout.addWidget(self.qt_style_label)
        self.checkboxes_layout.addWidget(self.qt_style_combobox)
        self.checkboxes_layout.addWidget(self.compositing_label)
        self.compositing_label.setStyleSheet("font-weight: bold;")
        self.checkboxes_layout.addWidget(self.borderless_switch)
        self.checkboxes_layout.addWidget(self.rounded_corners_switch)
        self.checkboxes_layout.addWidget(self.always_on_top_switch)
        self.checkboxes_layout.addWidget(self.translucent_background_switch)

        self.dark_mode_switch.setChecked(config["Settings"]["dark_mode"])
        self.colour_overlay_switch.setChecked(config["Settings"]["colour_overlay_mode"])
        themes = load_themes()
        themes_without_file_extension = [theme.replace(".qss", "") for theme in themes]
        self.qt_style_combobox.addItems(QStyleFactory.keys() + themes_without_file_extension)
        self.qt_style_combobox.setCurrentText(config["Settings"]["qt_style"].replace(".qss", ""))
        self.borderless_switch.setChecked(config["Settings"]["borderless"])
        self.rounded_corners_switch.setChecked(config["Settings"]["rounded_corners"])
        self.always_on_top_switch.setChecked(config["Settings"]["always_on_top"])
        self.translucent_background_switch.setChecked(config["Settings"]["translucent_background"])

        # Slider layout
        self.slider_layout = QtWidgets.QHBoxLayout()
        self.opacity_label = QtWidgets.QLabel("Opacity:", self)
        with open ('config.toml', 'r') as file:
            toml_config = toml.load(file)
            opacity_percent = toml_config["Settings"]["opacity"] * 100
            self.opacity_percentage_label = QtWidgets.QLabel(f"{opacity_percent}%", self)
        self.opacity_slider = QtWidgets.QSlider(Qt.Horizontal, self)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(config["Settings"]["opacity"] * 100)
        self.slider_layout.addWidget(self.opacity_label)
        self.slider_layout.addWidget(self.opacity_slider)
        self.slider_layout.addWidget(self.opacity_percentage_label)

        self.other_layout = QtWidgets.QVBoxLayout()
        self.window_behaviour_label = QtWidgets.QLabel("Window Behaviour", self)
        self.window_behaviour_label.setStyleSheet("font-weight: bold;")
        self.draggable_window_switch = QtWidgets.QCheckBox("Draggable Window", self)
        self.sidebar_mode_switch = QtWidgets.QCheckBox("Sidebar Mode", self)
        self.search_behaviour_label = QtWidgets.QLabel("Search Behaviour", self)
        self.search_behaviour_label.setStyleSheet("font-weight: bold;")
        self.default_search_label = QtWidgets.QLabel("Default Search Engine:", self)
        self.default_search_engine_combobox = QtWidgets.QComboBox(self)
        search_engines = []
        for search_engine in config["Search_Engines"].keys(): search_engines.append(search_engine.title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com"))
        self.default_search_engine_combobox.addItems(search_engines)
        self.verbatim_search_switch = QtWidgets.QCheckBox("Verbatim Search", self)
        self.no_results_text_label = QtWidgets.QLabel("No Results Text:", self)
        self.no_results_text_input = QtWidgets.QLineEdit(self)
        self.search_providers_label = QtWidgets.QLabel("Search Providers", self)
        self.search_providers_label.setStyleSheet("font-weight: bold;")
        self.search_start_menu_switch = QtWidgets.QCheckBox("Start Menu", self)
        self.search_calculator_switch = QtWidgets.QCheckBox("Calculator", self)
        self.search_web_switch = QtWidgets.QCheckBox("Web", self)
        self.search_steam_switch = QtWidgets.QCheckBox("Steam", self)
        self.search_bsman_switch = QtWidgets.QCheckBox("BSManager", self)
        self.reset_settings_button = QtWidgets.QPushButton("Reset All Settings", self)
        self.edit_toml_button = QtWidgets.QPushButton("Edit TOML In Text Editor", self)
        self.other_layout.addWidget(self.window_behaviour_label)
        self.other_layout.addWidget(self.draggable_window_switch)
        self.other_layout.addWidget(self.sidebar_mode_switch)
        self.other_layout.addWidget(self.search_behaviour_label)
        self.other_layout.addWidget(self.default_search_label)
        self.other_layout.addWidget(self.default_search_engine_combobox)
        self.other_layout.addWidget(self.verbatim_search_switch)
        self.other_layout.addWidget(self.no_results_text_label)
        self.other_layout.addWidget(self.no_results_text_input)
        self.other_layout.addWidget(self.search_providers_label)
        self.other_layout.addWidget(self.search_start_menu_switch)
        self.other_layout.addWidget(self.search_calculator_switch)
        self.other_layout.addWidget(self.search_web_switch)
        self.other_layout.addWidget(self.search_steam_switch)
        self.other_layout.addWidget(self.search_bsman_switch)
        self.other_layout.addWidget(self.reset_settings_button)
        self.other_layout.addWidget(self.edit_toml_button)

        self.draggable_window_switch.setChecked(config["Settings"]["draggable_window"])
        self.sidebar_mode_switch.setChecked(config["Settings"]["sidebar_mode"])
        self.default_search_engine_combobox.setCurrentText(config["Settings"]["default_search_engine"].title().replace("Github", "GitHub").replace("Duckduckgo", "DuckDuckGo").replace("Aol", "AOL").replace("Askcom", "Ask.com"))
        self.verbatim_search_switch.setChecked(config["Settings"]["verbatim_search"])
        self.no_results_text_input.setText(config["Settings"]["no_results_text"])
        self.search_start_menu_switch.setChecked(config["Settings"]["search_start_menu"])
        self.search_calculator_switch.setChecked(config["Settings"]["search_calculator"])
        self.search_web_switch.setChecked(config["Settings"]["search_web"])
        self.search_steam_switch.setChecked(config["Settings"]["search_steam"])
        self.search_bsman_switch.setChecked(config["Settings"]["search_bsman"])

        # Add layouts to the main layout
        self.main_layout.addLayout(self.checkboxes_layout)
        self.main_layout.addLayout(self.slider_layout)
        self.main_layout.addLayout(self.other_layout)

        self.dark_mode_switch.stateChanged.connect(self.change_theme)
        self.colour_overlay_switch.stateChanged.connect(self.change_colour_overlay)
        self.qt_style_combobox.currentTextChanged.connect(self.change_qt_style)
        self.borderless_switch.stateChanged.connect(self.change_borderless)
        self.rounded_corners_switch.stateChanged.connect(self.change_rounded_corners)
        self.always_on_top_switch.stateChanged.connect(self.change_always_on_top)
        self.translucent_background_switch.stateChanged.connect(self.change_translucent_background)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.draggable_window_switch.stateChanged.connect(self.change_draggable_window)
        self.sidebar_mode_switch.stateChanged.connect(self.change_sidebar_mode)
        self.verbatim_search_switch.stateChanged.connect(self.change_verbatim_search)
        self.default_search_engine_combobox.currentTextChanged.connect(self.change_default_search_engine)
        self.no_results_text_input.textChanged.connect(self.change_no_results_text)
        self.search_start_menu_switch.stateChanged.connect(self.change_search_start_menu)
        self.search_calculator_switch.stateChanged.connect(self.change_search_calculator)
        self.search_web_switch.stateChanged.connect(self.change_search_web)
        self.search_steam_switch.stateChanged.connect(self.change_search_steam)
        self.search_bsman_switch.stateChanged.connect(self.change_search_bsman)
        self.reset_settings_button.clicked.connect(self.reset_settings_confirmation)
        self.edit_toml_button.clicked.connect(self.edit_toml)

    def closeEvent(self, event):
        self.parent().textbox.setFocus()

    def change_theme(self, state):
        with open('config.toml', 'r+') as file:
            config = toml.load(file)
            if state == 0:
                config['Settings']['dark_mode'] = False
                self.setStyleSheet(f"background-color: {config["Settings"]["light_mode_bg"]}; color: {config["Settings"]["light_mode_text"]};")
                self.parent().setStyleSheet(f"background-color: {config["Settings"]["light_mode_bg"]}; color: {config["Settings"]["light_mode_text"]};")
                self.parent().settings_button.setIcon(QIcon("images/settings-light.svg"))
                self.parent().exit_button.setIcon(QIcon("images/exit-light.svg"))
                self.parent().clear_text_button.setIcon(QIcon("images/clear-light.svg"))
                self.parent().textbox.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + config["Settings"]["light_mode_text"] + """;
        border-radius: 10px;
        padding: 0 8px;
        selection-background-color: darkgray;
    }
""")
            elif state == 2:
                config['Settings']['dark_mode'] = True
                self.setStyleSheet(f"background-color: {config["Settings"]["dark_mode_bg"]}; color: {config["Settings"]["dark_mode_text"]};")
                self.parent().setStyleSheet(f"background-color: {config["Settings"]["dark_mode_bg"]}; color: {config["Settings"]["dark_mode_text"]};")
                self.parent().settings_button.setIcon(QIcon("images/settings-dark.svg"))
                self.parent().exit_button.setIcon(QIcon("images/exit-dark.svg"))
                self.parent().clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
                self.parent().textbox.setStyleSheet("""
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
                self.setStyleSheet(f"background-color: {config["Settings"]["colour_overlay_bg"]}; color: {config["Settings"]["colour_overlay_text"]};")
                self.parent().setStyleSheet(f"background-color: {config["Settings"]["colour_overlay_bg"]}; color: {config["Settings"]["colour_overlay_text"]};")
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
                print(load_themes())
                with open(f"themes\\{text}", "r") as f:
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
            elif state == 2:
                config['Settings']['borderless'] = True
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
            elif state == 2:
                config['Settings']['always_on_top'] = True
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
        self.opacity_percentage_label.setText(f"{label_value}%")
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
            config['Settings']['default_search_engine'] = text.lower().replace("Ask.com", "askcom")
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
        reset_popup.setStyleSheet(f"background-color: {config["Settings"]["light_mode_bg"]}; color: {config["Settings"]["light_mode_text"]};")
        reset_popup.setIcon(QtWidgets.QMessageBox.Warning)
        reset_popup.buttonClicked.connect(self.reset_settings)
        reset_popup.exec_()

    def reset_settings(self, button):
        if button.text() == "&Yes":
            with open('default.toml', 'r') as file:
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
            if config["Settings"]["dark_mode"]:
                bg_color = config["Settings"]["dark_mode_bg"]
                text_color = config["Settings"]["dark_mode_text"]
            else:
                bg_color = config["Settings"]["light_mode_bg"]
                text_color = config["Settings"]["light_mode_text"]
            self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")

        keyboard.add_hotkey(config["Settings"]["hotkey"], self.toggle_window)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.textbox_layout = QtWidgets.QHBoxLayout()
        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.setPlaceholderText("Start typing to search...")
        self.textbox.setStyleSheet("""
    QLineEdit {
        border: 2px solid """ + text_color + """;
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
        self.exit_button = QtWidgets.QPushButton(self)
        self.exit_button.setFlat(True)
        self.exit_button.setStyleSheet(self.button_style)
        self.clear_text_button = QtWidgets.QPushButton(self)
        self.clear_text_button.setFlat(True)
        self.clear_text_button.setStyleSheet(self.button_style)
        self.clear_text_button.clicked.connect(self.textbox.clear)
        self.clear_text_button.clicked.connect(self.textbox.setFocus)
        self.exit_button.clicked.connect(sys.exit)

        if config["Settings"]["dark_mode"]:
            self.settings_button.setIcon(QIcon("images/settings-dark.svg"))
            self.exit_button.setIcon(QIcon("images/exit-dark.svg"))
            self.clear_text_button.setIcon(QIcon("images/clear-dark.svg"))
        else:
            self.settings_button.setIcon(QIcon("images/settings-light.svg"))
            self.exit_button.setIcon(QIcon("images/exit-light.svg"))
            self.clear_text_button.setIcon(QIcon("images/clear-light.svg"))

        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setFrameShape(QtWidgets.QScrollArea.NoFrame)
        self.label = QtWidgets.QLabel(self)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.textbox_layout.addWidget(self.textbox)
        self.textbox_layout.addWidget(self.clear_text_button)
        self.textbox_layout.addWidget(self.exit_button)
        self.textbox_layout.addWidget(self.settings_button)
        
        self.layout.addLayout(self.textbox_layout)
        self.layout.addWidget(self.scroll_area)
        
        self.textbox.textChanged.connect(self.on_text_changed)
        self.textbox.returnPressed.connect(self.on_enter_pressed)
        self.settings_button.clicked.connect(self.open_settings)
        
        program_list = list_programs()
        text = ""
        for i in range(len(program_list)):
            text += program_list[i].replace(".lnk", "").rsplit("\\")[-1] + "\n"
        self.change_text(text)

        self.m_drag = False
        self.m_DragPosition = QtCore.QPoint()
    
    with open('config.toml', 'r') as file:
        config = toml.load(file)
        if config["Settings"]["draggable_window"]:
            def mousePressEvent(self, event):
                if event.button() == QtCore.Qt.LeftButton:
                    self.m_drag = True
                    self.m_DragPosition = event.globalPos() - self.pos()
                    event.accept()

            def mouseMoveEvent(self, event):
                if event.buttons() == QtCore.Qt.LeftButton and self.m_drag:
                    self.move(event.globalPos() - self.m_DragPosition)
                    event.accept()

            def mouseReleaseEvent(self, event):
                self.m_drag = False
                self.textbox.setFocus()
        
    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            widget.activateWindow()
            widget.raise_()
            self.textbox.setFocus()

    def open_settings(self):
        settings_popup = SettingsPopup(self)
        settings_popup.exec_()

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

    @QtCore.Slot()
    def on_text_changed(self, text):
        if text.lower() == "exit":
            self.change_text("Press Enter to Exit.")
        else:
            narrowed_list = narrow_down(text)
            new_text = ""
            for i in range(len(narrowed_list)):
                new_text += narrowed_list[i].replace(".lnk", "").rsplit("\\")[-1] + "\n"
            self.change_text(new_text)

    @QtCore.Slot()
    def change_text(self, text):
        self.label.setText(text)
        with open('config.toml', 'r') as file:
            config = toml.load(file)
            self.label.setFixedWidth(config["Settings"]["width"])
            self.label.setFixedHeight(config["Settings"]["height"])

    @QtCore.Slot()
    def on_enter_pressed(self):
        if self.textbox.text() == "exit":
            sys.exit()
        elif self.label.text() == config["Settings"]["no_results_text"] + "\n":
            self.textbox.clear()
        else:
            determine_program(self.textbox.text())
            self.textbox.clear()
            self.toggle_window()

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    app.setStyle("Macintosh" if sys.platform == "darwin" else "Fusion")
    app.setWindowIcon(QIcon("logo.png"))

    widget = MainWindow()
    with open('config.toml', 'r') as file:
        config = toml.load(file)
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

    sys.exit(app.exec())