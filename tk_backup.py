from tkinter import *
import os, io
import wmlparser3 as wml

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()

class StartPage(Page):
    def __init__(self, addons, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.entry = Entry(self)
        self.entry.pack()
        Button(self, text="Create", command=self.create).pack()
        for f in addons:
            Button(self, text = f.name, command = lambda f=f:self.chose_addon(f)).pack()

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global wmltree
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        Menu(root).pack()
        self.destroy()

    def create(self):
        os.makedirs(PATH_ADDONS+"/"+self.entry.get())
        io.open(PATH_ADDONS+"/"+self.entry.get()+"/_main.cfg", 'w', encoding='utf8').close()

class Menu(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        Label(self, text = NAME_ADDON).pack()
        Label(self, text = PATH_ADDON).pack()
        Button(self, text = "Eras").pack()
        Label(self, text = len(wmltree.get_all(tag = "era"))).pack()
        
root = Tk()

"""
PATH_WESNOTH = "C:/Gry/BattleForWesnothStable"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"
"""
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]  

startPage = StartPage(addons)
startPage.pack()