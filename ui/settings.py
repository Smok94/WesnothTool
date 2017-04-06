import io, os, json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def save():
    with open("config.json", "w") as f:
        json.dump(cfg, f)
        f.close()

def load():
    global cfg
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            cfg = json.loads(f.read())
            f.close()
    else:
        cfg = {}

class SettingsWindow(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        hBox = QHBoxLayout()
        vBox.addLayout(hBox)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.changePage)
        hBox.addWidget(self.list)
        self.sw = QStackedWidget()
        self.sw.setLayout(QVBoxLayout())
        self.dir("Paths", "WesnothPath", "Path to Wesnoth folder")
        self.dir("Paths", "AddonsPath", "Path to addons folder")
        hBox.addWidget(self.sw)
        b = QPushButton("Save")
        b.clicked.connect(save)
        vBox.addWidget(b)

    def changePage(self, int):
        self.sw.setCurrentIndex(int)

    def addPage(self, name):
        if not any(self.sw.widget(x).name == name for x in range(self.sw.count())):
            page = Page(name)
            self.sw.addWidget(page)
            self.list.addItem(name)

    def dir(self, page, id, name):
        self.addPage(page)
        x = next(x for x in range(self.sw.count()) if self.sw.widget(x).name == page)
        self.sw.widget(x).addWidget(Directory(id, name))

class Page(QWidget):
    def __init__(self, name, parent = None):
        super().__init__()
        self.name = name
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLabel(self.name))

    def addWidget(self, widget):
        self.layout.addWidget(widget)

class Directory(QWidget):
    def __init__(self, id, name, parent = None):
        super().__init__()
        self.id = id
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel(name))
        hBox = QHBoxLayout()
        vBox.addLayout(hBox)
        self.l = QLabel()
        if self.id in cfg:
            self.l.setText(cfg[self.id])
        else:
            self.l.setText("UNSET")
        hBox.addWidget(self.l)
        b = QPushButton("Change")
        b.clicked.connect(self.change)
        hBox.addWidget(b)

    def change(self):
        self.dialog = QFileDialog()
        self.dialog.setFileMode(QFileDialog.DirectoryOnly)
        self.dialog.setOption(QFileDialog.ShowDirsOnly)
        self.dialog.fileSelected.connect(self.changed)
        self.dialog.show()

    def changed(self, val):
        self.l.setText(val)
        cfg[self.id] = val