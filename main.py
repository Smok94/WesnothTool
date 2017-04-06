import os, io, sys, json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#sys.path.append(os.path.dirname(__file__))
import tools.wmlparser3 as wml
import ui.settings as cfg
from tools import generator

VERSION = "PreAlpha 0.1"

def wesPixmap(pixmap, path):
    if pixmap.load(cfg.cfg["WesnothPath"] + "/data/core/images/"+path):
        return pixmap
    elif pixmap.load(PATH_ADDON+"/images/"+path):
        return pixmap
    else:
        pixmap.load(cfg.cfg["WesnothPath"] + "/data/core/images/"+"units/unknown-unit.png")
        return pixmap    

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
        self.addAction("Settings")

    def aLoadAddon(self):
        addons = [f for f in os.scandir(cfg.cfg["AddonsPath"]) if f.is_dir()]
        w = StartPage(addons, self.mdi)
        self.mdi.addSubWindow(w)
        w.show()

    def aSettings(self):
        w = cfg.SettingsWindow()
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
        w = UnitEditor(data.units[value])
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
###        
class SubWindow(QMdiSubWindow):
    def __init__(self, id, widget, parent = None):
        super().__init__(widget)
        self.id = id

    def closeEvent(event):
        super().closeEvent(event)
###        
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
        global data
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        data = WesData(PATH_ADDON+"/_main.cfg")
        mainWindow.addToolBar(Qt.LeftToolBarArea, AddonToolBar(self.mdi))
        self.mdi.removeSubWindow(self.parentWidget())

    def create(self):
        os.makedirs(cfg.cfg["AddonsPath"]+"/"+self.le.text())
        io.open(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/_main.cfg", 'w', encoding='utf8').close()

class WesData():
    def __init__(self, path):
        self.units = []
        self.campaigns = []
        self.path = path
        self.parser = wml.Parser(cfg.cfg["WesnothPath"]+"/wesnoth.exe")
        self.defines = "MULTIPLAYER,EDITOR"
        self.load()

    def att(self, tag, at):
        list = tag.get_all(att = at)
        if len(list) > 0:
            return list[0].get_text()
        return  None

    def load(self):
        self.wmltree = self.parser.parse_file(self.path, self.defines)
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
        self.wmltree = self.parser.parse_file(self.path, self.defines)           

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
    def __init__(self, unit, parent = None):
        super().__init__(parent)
        self.unit = unit
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        h = QHBoxLayout()
        vBox.addLayout(h)
        v = QVBoxLayout()
        l = QLabel()
        l.setPixmap(wesPixmap(QPixmap(), self.unit.image))
        h.addWidget(l)
        h.addLayout(v)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("HP"))
        le = QLineEdit(self.unit.hitpoints)
        le.textEdited.connect(self.hp)
        v1.addWidget(le)
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("XP"))
        v1.addWidget(QLineEdit(self.unit.experience))
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v.addLayout(v1)
        v1.addWidget(QLabel("MP"))
        v1.addWidget(QLineEdit(self.unit.movement))
        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vBox.addWidget(b)

    def hp(self, val):
        self.unit.hitpoints = val

    def save(self):
        tools.generator.Generator(PATH_ADDON, VERSION).unit(self.unit)

cfg.load()

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("windows"))
qssFile="darkorange.qss"
with open(qssFile,"r") as fh:
    app.setStyleSheet(fh.read())
app.setStyle("plastique")

mainWindow = MainWindow()
mainWindow.show()

sys.exit(app.exec_())