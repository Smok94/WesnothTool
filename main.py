import os, io, sys, json, gettext, shutil
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#sys.path.append(os.path.dirname(__file__))
import tools.wmlparser3 as wml
import ui.settings as cfg
import tools.generator as generator

VERSION = "PreAlpha 0.2"

def wesPixmap(pixmap, path):
    if pixmap.load(cfg.cfg["WesnothPath"] + "/data/core/images/"+path):
        return pixmap
    elif pixmap.load(PATH_ADDON+"/images/"+path):
        return pixmap
    else:
        pixmap.load(cfg.cfg["WesnothPath"] + "/data/core/images/"+"units/unknown-unit.png")
        return pixmap    

def reloadAddon():
    global data
    global addon_toolbar
    data = WesData(PATH_ADDON+"/_main.cfg")
    addon_toolbar.setParent(None)
    addon_toolbar = AddonToolBar(mdi)
    mainWindow.addToolBar(Qt.LeftToolBarArea, addon_toolbar)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global mdi
        self.setWindowTitle(_("Wesnoth Addon Creator"))
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
        addons = [f for f in os.scandir(cfg.cfg["AddonsPath"]) if f.is_dir()]
        w = StartPage(addons, self.mdi)
        self.mdi.addSubWindow(w, "addons")

    def aSettings(self):
        w = cfg.SettingsWindow()
        self.mdi.addSubWindow(w, "settings")

class AddonToolBar(QToolBar):
    def __init__(self, mdi, parent = None):
        super().__init__()
        self.mdi = mdi
        self.addAction(NAME_ADDON).triggered.connect(self.addonSettings)
        self.addAction("+ New Unit").triggered.connect(self.newUnit)
        self.unit()
        self.addAction("+ New Era").triggered.connect(self.newEra)
        self.era()

    def addonSettings(self):
        w = AddonSettings()
        self.mdi.addSubWindow(w, "addonsettings")  

    def newUnit(self):
        w = UnitCreator()
        self.mdi.addSubWindow(w)

    def newEra(self):
        w = EraCreator()
        self.mdi.addSubWindow(w)

    def newUnit(self):
        w = UnitCreator()
        self.mdi.addSubWindow(w)
            
    def unit(self):
        combo = QComboBox()
        self.addWidget(combo)
        combo.activated.connect(self.unitEdit)
        for unit in data.units:
            combo.addItem(unit.name)

    def era(self):
        combo = QComboBox()
        self.addWidget(combo)
        combo.activated.connect(self.eraEdit)
        for era in data.eras:
            combo.addItem(era.name)
            
    def unitEdit(self, value):
        w = UnitEditor(data.units[value])
        self.mdi.addSubWindow(w)

    def eraEdit(self, value):
        w = EraEditor(data.eras[value])
        self.mdi.addSubWindow(w)     


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

    def addSubWindow(self, widget, id = None):
        if not id or not any(x.id == id for i, x in enumerate(self.subWindowList())):
            sw = SubWindow(widget, id)
            sw.setAttribute(Qt.WA_DeleteOnClose);
            super().addSubWindow(sw)
            sw.show()
        else:
            x = next(x for x in self.subWindowList() if x.id == id)
            x.setFocus()
        
class SubWindow(QMdiSubWindow):
    def __init__(self, widget, id = None, parent = None):
        super().__init__()
        sa = QScrollArea()
        sa.setWidget(widget)
        self.setWidget(sa)
        self.resize(self.sizeHint().width()*1.1,self.sizeHint().height()*1.2)
        self.id = id
        
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
        vBox.addWidget(QLabel("Addons:"))
        for f in addons:
            button = QPushButton(f.name)
            button.clicked.connect(lambda value, f=f:self.chose_addon(f))
            vBox.addWidget(button)

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global data
        global addon_toolbar
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        data = WesData(PATH_ADDON+"/_main.cfg")
        addon_toolbar = AddonToolBar(self.mdi)
        mainWindow.addToolBar(Qt.LeftToolBarArea, addon_toolbar)
        self.mdi.removeSubWindow(self.parentWidget().parentWidget().parentWidget())

    def create(self):
        os.makedirs(cfg.cfg["AddonsPath"]+"/"+self.le.text())
        with io.open(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/_main.cfg", 'w', encoding='utf8') as f:
            f.write("[binary_path]\n    path=data/add-ons/"+self.le.text()+"\n[/binary_path]\n[units]\n    {~add-ons/"+self.le.text()+"/units}\n[/units]\n{~add-ons/"+self.le.text()+"/eras}")
        io.open(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/_server.pbl", 'w', encoding='utf8').close()
        if not os.path.exists(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/units"):
            os.makedirs(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/units")
        if not os.path.exists(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/images"):
            os.makedirs(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/images")
        if not os.path.exists(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/eras"):
            os.makedirs(cfg.cfg["AddonsPath"]+"/"+self.le.text()+"/eras")
        self.mdi.removeSubWindow(self.parentWidget().parentWidget().parentWidget())

class WesData():
    def __init__(self, path):
        self.units = []
        self.campaigns = []
        self.eras = []
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
        self.loadEras()

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

    def loadEras(self):
        eraTags = self.wmltree.get_all(tag = "era")
        for tag in eraTags:
            sides = tag.get_all(tag = "multiplayer_side")
            sides_list = []
            for side in sides:
                sides_list.append(SSide(self.att(side, "id"), self.att(side, "name"), self.att(side, "leader"), self.att(side, "recruit")))
            self.eras.append(SEra(self.att(tag, "id"), self.att(tag, "name"), sides_list))

class SEra():
    def __init__(self, id, name, sides):
        self.id = id
        self.name = name
        self.sides = sides

class SSide():
    def __init__(self, id, name, leader, recruit):
        self.id = id
        self.name = name
        self.leader = leader
        self.recruit = recruit
        
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

class SAddonInfo():
    def __init__(self, title, version, author, passphrase, description, type):
        self.title = title
        self.version = version
        self.author = author
        self.passphrase = passphrase
        self.description = description
        self.type = type

class EraEditor(QWidget):
    def __init__(self, era, parent = None):
        super().__init__(parent)
        self.era = era
        vvBox = QVBoxLayout()
        self.setLayout(vvBox)
        self.vBox = QVBoxLayout()
        vvBox.addLayout(self.vBox)
        h = QHBoxLayout()
        
        v = QVBoxLayout()
        v.addWidget(QLabel("Name"))
        le = QLineEdit(self.era.name)
        le.textEdited.connect(self.name)
        v.addWidget(le)
        h.addLayout(v)

        v = QVBoxLayout()
        v.addWidget(QLabel("ID"))
        le = QLineEdit(self.era.id)
        le.textEdited.connect(self.id)
        v.addWidget(le)
        h.addLayout(v)
        
        self.vBox.addLayout(h)

        b = QPushButton("Add New Side")
        b.clicked.connect(self.newSide)
        self.vBox.addWidget(b)
        for i, side in enumerate(self.era.sides):
            self.addSide(i, side)

        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vvBox.addWidget(b)

    def name(self, val):
        self.era.name = val

    def id(self, val):
        self.era.id = val

    def addSide(self, i, side):
        v = QVBoxLayout()
        v.addWidget(QLabel("Side "+str(i+1)))
        h = QHBoxLayout()
        h.addWidget(QLabel("ID"))
        le = QLineEdit(side.id)
        le.textEdited.connect(lambda val, i=i: self.sid(val, i))
        h.addWidget(le)
        v.addLayout(h)
        h = QHBoxLayout()
        h.addWidget(QLabel("Name"))
        le = QLineEdit(side.name)
        le.textEdited.connect(lambda val, i=i: self.sname(val, i))
        h.addWidget(le)
        v.addLayout(h)
        h = QHBoxLayout()
        h.addWidget(QLabel("Leaders list"))
        le = QLineEdit(side.leader)
        le.textEdited.connect(lambda val, i=i: self.sleader(val, i))
        h.addWidget(le)
        v.addLayout(h)
        h = QHBoxLayout()
        h.addWidget(QLabel("Recruit list"))
        le = QLineEdit(side.recruit)
        le.textEdited.connect(lambda val, i=i: self.srecruit(val, i))
        h.addWidget(le)
        v.addLayout(h)
        self.vBox.addLayout(v)

    def newSide(self):
        self.era.sides.append(SSide("newside","New",None,None))
        i = len(self.era.sides) - 1
        self.addSide(i, self.era.sides[i])
        hint = self.sizeHint()
        self.resize(hint.width(), hint.height() + 120)

    def sid(self, val, i):
        self.era.sides[i].id = val

    def sname(self, val, i):
        self.era.sides[i].name = val

    def sleader(self, val, i):
        self.era.sides[i].leader = val

    def srecruit(self, val, i):
        self.era.sides[i].recruit = val

    def save(self):
        generator.Generator(PATH_ADDON, VERSION).era(self.era)
        reloadAddon()

class UnitEditor(QWidget):
    def __init__(self, unit, parent = None):
        super().__init__(parent)
        self.unit = unit
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        h = QHBoxLayout()
        
        v = QVBoxLayout()
        v.addWidget(QLabel("Name"))
        le = QLineEdit(self.unit.name)
        le.textEdited.connect(self.name)
        v.addWidget(le)
        h.addLayout(v)

        v = QVBoxLayout()
        v.addWidget(QLabel("ID"))
        le = QLineEdit(self.unit.id)
        le.textEdited.connect(self.id)
        v.addWidget(le)
        h.addLayout(v)
        
        vBox.addLayout(h)

        h = QHBoxLayout()
        vBox.addLayout(h)
        v = QVBoxLayout()
        self.l = QLabel()
        self.l.setPixmap(wesPixmap(QPixmap(), self.unit.image))
        v.addWidget(self.l)
        b = QPushButton("Change")
        b.clicked.connect(self.image)
        v.addWidget(b)
        h.addLayout(v)
        v = QVBoxLayout()
        h.addLayout(v)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("HP"))
        le = QLineEdit(self.unit.hitpoints)
        le.textEdited.connect(self.hp)
        v1.addWidget(le)
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("XP"))
        le = QLineEdit(self.unit.experience)
        le.textEdited.connect(self.xp)
        v1.addWidget(le)
        v.addLayout(v1)
        v1 = QVBoxLayout()
        v.addLayout(v1)
        v1.addWidget(QLabel("MP"))
        le = QLineEdit(self.unit.movement)
        le.textEdited.connect(self.mp)
        v1.addWidget(le)
        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vBox.addWidget(b)

    def hp(self, val):
        self.unit.hitpoints = val

    def xp(self, val):
        self.unit.experience = val

    def mp(self, val):
        self.unit.movement = val

    def name(self, val):
        self.unit.name = val

    def id(self, val):
        self.unit.id = val

    def image(self):
        self.dialog = QFileDialog()
        self.dialog.setFileMode(QFileDialog.ExistingFile)
        self.dialog.fileSelected.connect(self.changed)
        self.dialog.show()

    def changed(self, val):
        shutil.copy2(val, PATH_ADDON+"/images/"+os.path.basename(val))
        self.unit.image = os.path.basename(val)
        self.l.setPixmap(wesPixmap(QPixmap(), self.unit.image))

    def save(self):
        generator.Generator(PATH_ADDON, VERSION).unit(self.unit)
        reloadAddon()

class AddonSettings(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.load()
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel("Title"))
        le = QLineEdit(self.addon.title)
        le.textEdited.connect(self.Title)
        vBox.addWidget(le)
        vBox.addWidget(QLabel("Description"))
        self.pte = QPlainTextEdit(self.addon.description)
        self.Description()
        self.pte.textChanged.connect(self.Description)
        vBox.addWidget(self.pte)
        vBox.addWidget(QLabel("Type"))
        self.combo = QComboBox()
        self.combo.activated.connect(self.Type)
        self.combo.addItem("era")
        self.combo.addItem("faction")
        self.combo.addItem("core")
        self.combo.addItem("campaign")
        self.combo.addItem("scenario")
        self.combo.addItem("campaign_sp_mp")
        self.combo.addItem("map_pack")
        self.combo.addItem("campaign_mp")
        self.combo.addItem("scenario_mp")
        self.combo.addItem("mod_mp")
        self.combo.addItem("media")
        self.combo.addItem("other")
        vBox.addWidget(self.combo)
        vBox.addWidget(QLabel("Author"))
        le = QLineEdit(self.addon.author)
        le.textEdited.connect(self.Author)
        vBox.addWidget(le)
        vBox.addWidget(QLabel("Version"))
        le = QLineEdit(self.addon.version)
        le.textEdited.connect(self.Version)
        vBox.addWidget(le)
        vBox.addWidget(QLabel("Passphrase"))
        le = QLineEdit(self.addon.passphrase)
        le.textEdited.connect(self.Passphrase)
        vBox.addWidget(le)
        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vBox.addWidget(b)

    def load(self):
        parser = wml.Parser()
        self.tree = parser.parse_file(PATH_ADDON+"/_server.pbl")
        self.addon = SAddonInfo(self.att(self.tree,"title"),self.att(self.tree,"version"),self.att(self.tree,"author"),self.att(self.tree,"passphrase"),self.att(self.tree,"description"),self.att(self.tree,"type"))

    def att(self, tag, at):
        list = tag.get_all(att = at)
        if len(list) > 0:
            return list[0].get_text()
        return None
    
    def Title(self, value):
        self.addon.title = value

    def Description(self):
        self.addon.description = self.pte.toPlainText()
        
    def Type(self, value):
        self.addon.type = self.combo.itemText(value)
        
    def Version(self, value):
        self.addon.version = value

    def Author(self, value):
        self.addon.author = value
        
    def Passphrase(self, value):
        self.addon.passphrase = value

    def save(self):
        generator.Generator(PATH_ADDON, VERSION).addoninfo(self.addon)

class UnitCreator(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel("Unit ID"))
        self.le = QLineEdit("newunit")
        vBox.addWidget(self.le)
        b = QPushButton("Create")
        b.clicked.connect(self.create)
        vBox.addWidget(b)

    def create(self):
        with io.open(cfg.cfg["AddonsPath"]+"/"+NAME_ADDON+"/units/"+self.le.text()+".cfg", 'w', encoding='utf8') as f:
            f.write('[unit_type]\n    id = "'+self.le.text()+'"\n    name = _ "New"\n[/unit_type]')
        reloadAddon()
        mdi.removeSubWindow(self.parentWidget().parentWidget().parentWidget())

class EraCreator(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel("Era ID"))
        self.le = QLineEdit("newera")
        vBox.addWidget(self.le)
        b = QPushButton("Create")
        b.clicked.connect(self.create)
        vBox.addWidget(b)

    def create(self):
        with io.open(cfg.cfg["AddonsPath"]+"/"+NAME_ADDON+"/eras/"+self.le.text()+".cfg", 'w', encoding='utf8') as f:
            f.write('[era]\n    id = "'+self.le.text()+'"\n    name = _ "New"\n[/era]')
        reloadAddon()
        mdi.removeSubWindow(self.parentWidget().parentWidget().parentWidget())
    
#################
cfg.load()

if "Language" in cfg.cfg and os.path.isfile("translations/"+cfg.cfg["Language"]+"/LC_MESSAGES/wac.mo"):
    translation = gettext.translation('wac', localedir='translations', languages=[cfg.cfg["Language"]])
    translation.install()
else:
    _ = lambda s: s

app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create("windows"))
qssFile="darkorange.qss"
with open(qssFile,"r") as fh:
    app.setStyleSheet(fh.read())
app.setStyle("plastique")

mainWindow = MainWindow()
mainWindow.show()

sys.exit(app.exec_())