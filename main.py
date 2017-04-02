import os, io, sys, json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import wmlparser3 as wml
import ui.settings
import tools.wmlgen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wesnoth Addon Creator")
        mdi = MdiArea()
        self.setCentralWidget(mdi)
        self.addToolBar(MainToolBar(mdi))

class MainToolBar(QToolBar):
    def __init__(self, mdi, parent = None):
        super().__init__()
        self.mdi = mdi
        self.addAction("Load Addon").triggered.connect(self.aLoadAddon)
        self.addAction("Settings").triggered.connect(self.aSettings)

    def aLoadAddon(self):
        w = StartPage(addons, self.mdi)
        self.mdi.addSubWindow(w)
        w.show()

    def aSettings(self):
        w = ui.settings.SettingsWindow(cfg)
        self.mdi.addSubWindow(w)
        w.show()

class AddonToolBar(QToolBar):
    def __init__(self, mdi, parent = None):
        super().__init__()
        self.mdi = mdi
        self.addAction(NAME_ADDON)
        self.unit()

    def unit(self):
        combo = QComboBox()
        self.addWidget(combo)
        combo.activated.connect(self.unitEdit)
        for unit in data.units:
            combo.addItem(unit.name)
            
    def unitEdit(self, value):
        w = UnitEditor(value)
        self.mdi.addSubWindow(w)
        w.show()      

class MdiArea(QMdiArea):
    def __init__(self, parent = None):
        super().__init__()

    def paintEvent (self, event):
        super().paintEvent(event)
        painter = QPainter()
        painter.begin(self.viewport())
        painter.fillRect(0, 0, self.width(), self.height(), QColor(50,50,50,255))
        pixmap = QPixmap("images/bfw-logo.png")
        x = self.width() - pixmap.width()
        y = self.height() - pixmap.height()
        painter.drawPixmap(x, y, pixmap)
        painter.end()

class StartPage(QWidget):
    def __init__(self, addons, mdi, parent = None):
        super().__init__()
        self.mdi = mdi
        hBox = QHBoxLayout()
        vBox = QVBoxLayout()
        hBox.addLayout(vBox)
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

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global wmltree
        global data
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        data = WesData(PATH_ADDON+"/_main.cfg")
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        mainWindow.addToolBar(Qt.LeftToolBarArea, AddonToolBar(self.mdi))
        self.mdi.removeSubWindow(self.parentWidget())

    def create(self):
        os.makedirs(PATH_ADDONS+"/"+self.le.text())
        io.open(PATH_ADDONS+"/"+self.le.text()+"/_main.cfg", 'w', encoding='utf8').close()

###
class ElementsList(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.unitSelected)
        self.setLayout(vBox)
        vBox.addWidget(self.list)
        for unit in data.units:
            widget = UnitListItem(unit.name, PATH_IMAGES+unit.image)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.list.addItem(item)
            self.list.setItemWidget(item, widget);           

    def unitSelected(self, num):
        editor = UnitEditor(data.units[num])
        mainWindow.centralWidget().layout().addWidget(editor)

class UnitListItem(QWidget):
    def __init__(self, name, image, parent = None):
        super().__init__(parent)
        hBox = QHBoxLayout()
        self.setLayout(hBox)
        l = QLabel()
        l.setPixmap(QPixmap(image))
        hBox.addWidget(l)
        hBox.addWidget(QLabel(name))

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
        b = QPushButton("Units")
        b.clicked.connect(self.createList)
        hBox.addWidget(b)
        units = wmltree.get_all(tag = "units")
        uNumber = 0
        if len(units) > 0:
            for tag in units:
                uNumber += len(tag.get_all(tag = "unit_type"))
        hBox.addWidget(QLabel(str(uNumber)))
        vBox.addLayout(hBox)
        for unit in data.units:
            hBox = QHBoxLayout()
            hBox.addWidget(QLabel(unit.id))
            hBox.addWidget(QLabel(unit.name))
            l = QLabel()
            l.setPixmap(QPixmap(PATH_IMAGES+unit.image))
            hBox.addWidget(l)
            vBox.addLayout(hBox)

    def createList(self):
        el = ElementsList()
        mainWindow.centralWidget().layout().addWidget(el)
###

class WesData():
    def __init__(self, path):
        self.units = []
        self.campaigns = []
        self.path = path
        self.defines = "MULTIPLAYER,EDITOR"
        self.load()

    def att(self, tag, at):
        list = tag.get_all(att = at)
        if len(list) > 0:
            return list[0].get_text()
        return  None

    def load(self):
        self.wmltree = parser.parse_file(self.path, self.defines)
        #campaigns must go first
        self.loadCampaigns()
        self.loadUnits()

    def loadCampaigns(self):
        tags = self.wmltree.get_all(tag = "campaign")
        for tag in tags:
            define = self.att(tag, "define")
            self.campaigns.append(SCampaign(self.att(tag, "id"), self.att(tag, "name"), define))
            if define:
                self.defines = self.defines + "," + self.att(tag, "define")
        self.wmltree = parser.parse_file(self.path, self.defines)           

    def loadUnits(self):
        unitsTag = self.wmltree.get_all(tag = "units")
        for tags in unitsTag:
            unitTags = tags.get_all(tag = "unit_type")
            for tag in unitTags:
                self.units.append(SUnit(self.att(tag, "experience"), self.att(tag, "hitpoints"), self.att(tag, "id"), self.att(tag, "image"), self.att(tag, "movement"), self.att(tag, "name")))
        
class SUnit():
    def __init__(self, experience, hitpoints, id, image, movement, name):
        self.experience = experience
        self.hitpoints = hitpoints
        self.id = id
        if not image:
            image = "units/unknown-unit.png"
        self.image = image
        self.movement = movement
        self.name = name
        
class SCampaign():
    def __init__(self, id, name, define):
        self.id = id
        self.name = name
        self.define = define

class UnitEditor(QWidget):
    def __init__(self, num, parent = None):
        super().__init__(parent)
        self.num = num
        unit = data.units[self.num]
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        h = QHBoxLayout()
        vBox.addLayout(h)
        v = QVBoxLayout()
        l = QLabel()
        l.setPixmap(QPixmap(PATH_IMAGES+unit.image))
        h.addWidget(l)
        h.addLayout(v)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("HP"))
        le = QLineEdit(unit.hitpoints)
        le.textEdited.connect(self.hp)
        v1.addWidget(le)
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("XP"))
        v1.addWidget(QLineEdit(unit.experience))
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v.addLayout(v1)
        v1.addWidget(QLabel("MP"))
        v1.addWidget(QLineEdit(unit.movement))
        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vBox.addWidget(b)

    def hp(self, val):
        data.units[self.num].hitpoints = val

    def save(self):
        tools.wmlgen.Gen(PATH_ADDON, VERSION).unit(data.units[self.num])

VERSION = "PreAlpha 0.1"
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_IMAGES = PATH_WESNOTH + "/data/core/images/"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

cfg = ui.settings.load()

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