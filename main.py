import os, io, sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import wmlparser3 as wml

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wesnoth Addon Creator")
        vBox = QVBoxLayout() 
        hBox = QHBoxLayout()
        l = QLabel()
        l.setPixmap(QPixmap("images/bfw-logo.png"))
        hBox.addStretch(1)
        hBox.addWidget(l)
        hBox.addStretch(1)
        self.setLayout(vBox)
        vBox.addLayout(hBox)
        self.startPage = StartPage(addons, self)
        self.startPage.setGeometry(0, 0, self.width(), self.height())
        self.startPage.show()

class StartPage(QWidget):
    def __init__(self, addons, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        self.le = QLineEdit()
        vBox.addWidget(self.le)
        button = QPushButton("Create")
        button.clicked.connect(self.create)
        vBox.addWidget(button)
        for f in addons:
            button = QPushButton(f.name)
            button.clicked.connect(lambda value, f=f:self.chose_addon(f))
            vBox.addWidget(button)

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global wmltree
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        self.menu = Menu()
        self.menu.show()

    def create(self):
        os.makedirs(PATH_ADDONS+"/"+self.le.text())
        io.open(PATH_ADDONS+"/"+self.le.text()+"/_main.cfg", 'w', encoding='utf8').close()
        self.update()

class Menu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel(NAME_ADDON))
        vBox.addWidget(QLabel(PATH_ADDON))
        vBox.addWidget(QPushButton("Eras"))
        vBox.addWidget(QLabel(str(len(wmltree.get_all(tag = "era")))))

"""
PATH_WESNOTH = "C:/Gry/BattleForWesnothStable"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"
"""
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]  

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("windows"))
sshFile="darkorange.qss"
with open(sshFile,"r") as fh:
    app.setStyleSheet(fh.read())
app.setStyle("plastique")

mainWindow = MainWindow()
mainWindow.show()

sys.exit(app.exec_())