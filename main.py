import os, io, sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
import wmlparser3 as wml

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wesnoth Addon Creator")
        self.setStyleSheet("MainWindow {background-image: url(images/bfw-logo.png); background-repeat: no-repeat; background-position: center;}")
        self.setCentralWidget(StartPage(addons))

class StartPage(QWidget):
    def __init__(self, addons, parent = None):
        super().__init__(parent)
        hBox = QHBoxLayout()
        hBox.addStretch(1)
        vBox = QVBoxLayout()
        vBox.addStretch(1)
        hBox.addLayout(vBox)
        hBox.addStretch(1)
        self.setLayout(hBox)
        self.le = QLineEdit()
        vBox.addWidget(self.le)
        button = QPushButton("Create")
        button.clicked.connect(self.create)
        vBox.addWidget(button)
        for f in addons:
            button = QPushButton(f.name)
            button.clicked.connect(lambda value, f=f:self.chose_addon(f))
            vBox.addWidget(button)
        vBox.addStretch(1)

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global wmltree
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        data.loadAddon()
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        mainWindow.setCentralWidget(MainWidget())

    def create(self):
        os.makedirs(PATH_ADDONS+"/"+self.le.text())
        io.open(PATH_ADDONS+"/"+self.le.text()+"/_main.cfg", 'w', encoding='utf8').close()

class MainWidget(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        hBox = QHBoxLayout()
        self.setLayout(hBox)
        hBox.addWidget(Menu())

class UnitsList(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

class Menu(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel(NAME_ADDON))
        vBox.addWidget(QLabel(PATH_ADDON))
        hBox = QHBoxLayout()
        hBox.addWidget(QPushButton("Eras"))
        hBox.addWidget(QLabel(str(len(wmltree.get_all(tag = "era")))))
        vBox.addLayout(hBox)
        hBox = QHBoxLayout()
        hBox.addWidget(QPushButton("Units"))
        units = wmltree.get_all(tag = "units")
        uNumber = 0
        if len(units) > 0:
            for tag in units:
                uNumber += len(tag.get_all(tag = "unit_type"))
        hBox.addWidget(QLabel(str(uNumber)))
        vBox.addLayout(hBox)
        for unit in data.addon.units:
            hBox = QHBoxLayout()
            hBox.addWidget(QLabel(unit.id))
            hBox.addWidget(QLabel(unit.name))
            l = QLabel()
            l.setPixmap(QPixmap(PATH_IMAGES+unit.image))
            hBox.addWidget(l)
            vBox.addLayout(hBox)

class DataLoader():
    def __init__(self):
        pass

    def att(self, tag, at):
        list = tag.get_all(att = at)
        if len(list) > 0:
            return list[0].get_text()
        return  None
    
    def loadAddon(self):
        self.addon = DataStructure()
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        unitsTag = wmltree.get_all(tag = "units")
        for tags in unitsTag:
            unitTags = tags.get_all(tag = "unit_type")
            for tag in unitTags:
                self.addon.units.append(SUnit(self.att(tag, "id"), self.att(tag, "name"), self.att(tag, "image")))

class DataStructure():
    def __init__(self):
        self.units = []

class SUnit():
    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        if not image:
            image = "units/unknown-unit.png"
        self.image = image
        
"""
PATH_WESNOTH = "C:/Gry/BattleForWesnothStable"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"
"""
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_IMAGES = PATH_WESNOTH + "/data/core/images/"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]  

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("windows"))
sshFile="darkorange.qss"
with open(sshFile,"r") as fh:
    app.setStyleSheet(fh.read())
app.setStyle("plastique")

data = DataLoader()

mainWindow = MainWindow()
mainWindow.show()

sys.exit(app.exec_())