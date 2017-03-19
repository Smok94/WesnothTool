import os, io, sys
from PyQt5 import QtWidgets as qt
import wmlparser3 as wml

class StartPage(qt.QWidget):
    def __init__(self, addons):
        super().__init__()
        vBox = qt.QVBoxLayout()
        self.setLayout(vBox)
        self.le = qt.QLineEdit()
        vBox.addWidget(self.le)
        button = qt.QPushButton("Create")
        button.clicked.connect(self.create)
        vBox.addWidget(button)
        for f in addons:
            button = qt.QPushButton(f.name)
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

class Menu(qt.QWidget):
    def __init__(self):
        super().__init__()
        vBox = qt.QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(qt.QLabel(NAME_ADDON))
        vBox.addWidget(qt.QLabel(PATH_ADDON))
        vBox.addWidget(qt.QPushButton("Eras"))
        vBox.addWidget(qt.QLabel(str(len(wmltree.get_all(tag = "era")))))

"""
PATH_WESNOTH = "C:/Gry/BattleForWesnothStable"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"
"""
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]  

app = qt.QApplication(sys.argv)

startPage = StartPage(addons)
startPage.show()

sys.exit(app.exec_())