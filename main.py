#!/usr/bin/env python3

import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QScrollArea,
    QMessageBox,
    QFrame,
    QStyleFactory,
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QPalette

from datas import data 


class ScrollableList(QFrame):
    item_selected = pyqtSignal(str)

    def __init__(self, title):
        super().__init__()
        self.setStyleSheet("background-color: #242424; color: white;")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(title)
        self.label.setStyleSheet("color: white;")
        self.layout.addWidget(self.label)

        self.buttons_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_content = QWidget()
        self.scroll_area_content.setLayout(self.buttons_layout)
        self.scroll_area.setWidget(self.scroll_area_content)
        self.scroll_area.setStyleSheet("background-color: #242424;")
        self.layout.addWidget(self.scroll_area)

        self.buttons = {}

    def clear(self):
        while self.buttons_layout.count():
            child = self.buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.buttons.clear()

    def add_items(self, items):
        for item in items:
            button = QPushButton(item)
            button.setCheckable(True)
            button.setStyleSheet(
                """
                QPushButton {
                    background-color: #0D47A1;
                    color: white;
                    border: none;
                    padding: 5px;
                }
                QPushButton:checked {
                    background-color: #1976D2;
                }
            """
            )
            button.clicked.connect(self.handle_click)
            self.buttons_layout.addWidget(button)
            self.buttons[item] = button

    @pyqtSlot()
    def handle_click(self):
        sender = self.sender()
        for btn in self.buttons.values():
            btn.setChecked(False)
        sender.setChecked(True)
        self.item_selected.emit(sender.text())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mullvad VPN")
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #242424;")

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.label = QLabel("Mullvad VPN")
        self.label.setStyleSheet("color: white;")
        self.main_layout.addWidget(self.label)

        self.lists_layout = QHBoxLayout()
        self.main_layout.addLayout(self.lists_layout)

        self.scroll_area1_content = ScrollableList("Country")
        self.lists_layout.addWidget(self.scroll_area1_content)

        self.scroll_area2_content = ScrollableList("City")
        self.lists_layout.addWidget(self.scroll_area2_content)

        self.scroll_area3_content = ScrollableList("Server")
        self.lists_layout.addWidget(self.scroll_area3_content)

        self.run_button = QPushButton("Secure my connection")
        self.run_button.setStyleSheet("background-color: #0D47A1; color: white;")
        self.run_button.clicked.connect(self.run_command)
        self.main_layout.addWidget(self.run_button)

        self.scroll_area1_content.item_selected.connect(self.update_option_menu2)
        self.scroll_area2_content.item_selected.connect(self.update_option_menu3)
        self.scroll_area3_content.item_selected.connect(self.update_server_selection)

        self.selected_country = None
        self.selected_city = None
        self.selected_server = None

        self.update_option_menu1()

    def update_option_menu1(self):
        countries = list(data.keys())
        self.scroll_area1_content.clear()
        self.scroll_area1_content.add_items(countries)

    def update_option_menu2(self, country):
        self.selected_country = country
        cities = list(data.get(country, {}).keys())
        self.scroll_area2_content.clear()
        self.scroll_area2_content.add_items(cities)

    def update_option_menu3(self, city):
        self.selected_city = city
        servers = data.get(self.selected_country, {}).get(city, [])
        self.scroll_area3_content.clear()
        self.scroll_area3_content.add_items(servers)

    def update_server_selection(self, server):
        self.selected_server = server

    def run_command(self):
        if (
            not self.selected_country
            or not self.selected_city
            or not self.selected_server
        ):
            QMessageBox.warning(
                self, "Error", "Please select a country, city, and server"
            )
            return

        server_id = self.selected_server.split()[0]
        command = f"mullvad relay set location {server_id}"

        try:
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )
            QMessageBox.information(self, "Command Output", result.stdout)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Command execution failed: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set a dark theme for the entire application
    app.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#242424"))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor("#353535"))
    palette.setColor(QPalette.AlternateBase, QColor("#242424"))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor("#0D47A1"))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor("#1976D2"))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
