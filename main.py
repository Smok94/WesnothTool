from tkinter import *
import os
import wmlparser3 as wml

class Page(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()

class StartPage(Page):
    def __init__(self, addons, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        Entry(self).pack()
        for f in addons:
            label = Button(self, text = f.name, command = lambda f=f:self.chose_addon(f))
            label.pack()

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        test = parser.parse_file(PATH_ADDON+"/_main.cfg")
        x = Menu(root)
        x.pack()
        test = test.get_all()
        for i, v in enumerate(test):
            Label(x, text = v.get_name()).pack()
        self.destroy()

class Menu(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        Label(self, text = NAME_ADDON).pack()
        Label(self, text = PATH_ADDON).pack()
        Button(self, text = "Menu").pack()
        
root = Tk()

PATH_WESNOTH = "C:/Gry/BattleForWesnoth1_13_6"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]  

startPage = StartPage(addons)
startPage.pack()