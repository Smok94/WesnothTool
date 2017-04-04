from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import tools.generator

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