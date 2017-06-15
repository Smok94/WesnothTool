import os, io

class Generator():
    def __init__(self, path, version):
        self.path = path
        self.header = "###Generated by Wesnoth Addon Creator, version: "+version+"###\n"

    def unit(self, unit):
        with open(self.path+"/units/"+getattr(unit, "id")+".cfg", "w") as f:
            self.lvl = 0
            f.write(self.header)
            self.openTag(f, "unit_type")
            atts = [["experience", 0], ["hitpoints", 0], ["id", 0], ["image", 1], ["movement", 0], ["name", 2]]
            for a in atts:
                self.writeAtt(f, unit, a[0], a[1])
            self.closeTag(f, "unit_type")

    def era(self, era):
        with open(self.path+"/eras/"+getattr(era, "id")+".cfg", "w") as f:
            self.lvl = 0
            f.write(self.header)
            self.openTag(f, "era")
            atts = [["id", 0], ["name", 2]]
            for a in atts:
                self.writeAtt(f, era, a[0], a[1])
            for s in era.sides:
                self.openTag(f, "multiplayer_side")
                atts = [["id", 0], ["name", 2], ["leader", 0], ["recruit", 0]]
                for a in atts:
                    self.writeAtt(f, s, a[0], a[1]) 
                self.closeTag(f, "multiplayer_side")
            self.closeTag(f, "era")

    def addoninfo(self, addon):
        with open(self.path+"/_server.pbl", "w") as f:
            self.lvl = 0
            f.write(self.header)
            f.write('comment = "This file contains informations about addon."\n')
            atts = [["title", 1], ["version", 1], ["author", 1], ["passphrase", 1], ["description", 1], ["type", 1]]
            for a in atts:
                self.writeAtt(f, addon, a[0], a[1])

    def writeAtt(self, f, obj, att, mode):
        """
        modes:
        0 - plain value
        1 - string
        2 - translatable string
        """
        if getattr(obj, att):
            ln = self.getln()
            if mode == 0:
                ln += att+" = "+getattr(obj, att)+"\n"
            elif mode == 1:
                ln += att+" = \""+getattr(obj, att)+"\"\n"
            elif mode == 2:
                ln += att+" = _ \""+getattr(obj, att)+"\"\n"
            f.write(ln)

    def openTag(self, f, tag):
        ln = self.getln()
        ln += "["+tag+"]\n"
        f.write(ln)
        self.lvl += 1

    def closeTag(self, f, tag):
        self.lvl -= 1
        ln = self.getln()
        ln += "[/"+tag+"]\n"
        f.write(ln)

    def getln(self):
        ln = ""
        for i in range(self.lvl):
            ln += "    "
        return ln