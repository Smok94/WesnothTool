import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
import os, io
import wmlparser3 as wml

class WACApp(App):
    def build(self):
        global interface
        interface = InterfaceManager()
        return interface

class InterfaceManager(BoxLayout):
    def __init__(self):
        super(InterfaceManager, self).__init__()
        self.add_widget(StartPage())
        

class StartPage(BoxLayout):
    def __init__(self):
        super(StartPage, self).__init__(orientation='vertical')
        self.input = TextInput()
        self.add_widget(self.input)
        w = Button(text="Create")
        w.bind(on_press = lambda a: self.create())
        self.add_widget(w)
        for f in addons:
            w = Button(text = f.name)
            w.bind(on_press = lambda a, f=f:self.chose_addon(f))
            self.add_widget(w)

    def chose_addon(self, addon):
        global PATH_ADDON
        global NAME_ADDON
        global wmltree
        PATH_ADDON = addon.path
        NAME_ADDON = addon.name
        wmltree = parser.parse_file(PATH_ADDON+"/_main.cfg", "MULTIPLAYER,EDITOR")
        interface.clear_widgets()
        interface.add_widget(Menu())

    def create(self):
        os.makedirs(PATH_ADDONS+"/"+self.input.text)
        io.open(PATH_ADDONS+"/"+self.input.text+"/_main.cfg", 'w', encoding='utf8').close()

class Menu(BoxLayout):
    def __init__(self):
        super(Menu, self).__init__(orientation='vertical')
        self.add_widget(Label(text = NAME_ADDON))
        self.add_widget(Label(text = PATH_ADDON))
        self.add_widget(Button(text = "Eras"))
        self.add_widget(Label(text = str(len(wmltree.get_all(tag = "era")))))

"""
PATH_WESNOTH = "C:/Gry/BattleForWesnothStable"
PATH_ADDONS = "C:/Gry/BattleForWesnothStable/userdata/data/add-ons"
"""
PATH_WESNOTH = "D:/BattleForWesnothDev"
PATH_ADDONS = "C:/Users/DarekZ/Documents/My Games/Wesnoth1.13/data/add-ons"

parser = wml.Parser(PATH_WESNOTH+"/wesnoth.exe")

addons = [f for f in os.scandir(PATH_ADDONS) if f.is_dir()]

app = WACApp()
app.run()