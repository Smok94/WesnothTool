import io, os, json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

def save(cfg):
    with open("config.json", "w") as f:
        json.dump(cfg, f)
        f.close()

def load():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            cfg = json.loads(f.read())
            f.close()
    else:
        cfg = []
    return cfg

class SettingsWindow(QWidget):
    def __init__(self, cfg, parent = None):
        super().__init__()
        self.cfg = cfg
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        hBox = QHBoxLayout()
        vBox.addLayout(hBox)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.changePage)
        hBox.addWidget(self.list)
        self.sw = QStackedWidget()
        self.sw.setLayout(QVBoxLayout())
        self.dir("Paths")
        hBox.addWidget(self.sw)
        b = QPushButton("Save")
        b.clicked.connect(self.save)
        vBox.addWidget(b)

    def save(self):
        save(self.cfg)

    def changePage(self, int):
        self.sw.setCurrentIndex(int)

    def addPage(self, name):
        if not any(self.sw.widget(x).name == name for x in range(self.sw.count())):
            page = Page(name)
            self.sw.addWidget(page)
            self.list.addItem(name)

    def dir(self, page):
        self.addPage(page)
        x = next(x for x in range(self.sw.count()) if self.sw.widget(x).name == page)
        self.sw.widget(x).addWidget(Directory())

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
    def __init__(self, parent = None):
        super().__init__()
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        self.select()

    def select(self):
        self.dialog = QFileDialog()
        self.dialog.setFileMode(QFileDialog.Directory)
        self.dialog.setOption(QFileDialog.ShowDirsOnly)
        self.dialog.show()
        