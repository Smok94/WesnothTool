from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#import tools.generator

class AddonSetting(QWidget):
    def __init__(self, addon, parent = None):
        super().__init__(parent)
        self.addon = addon
        vBox = QVBoxLayout()
        self.setLayout(vBox)
        vBox.addWidget(QLabel("Name"))
        #le = QLineEdit(self.unit.hitpoints)
        #le.textEdited.connect(self.hp)
        #vBox.addWidget(le)
        b = QPushButton("Save")
        #b.clicked.connect(self.save)
        vBox.addWidget(b)