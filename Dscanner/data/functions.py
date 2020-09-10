import json
import os
from platform import system


def clear():
    if system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def get_settings():
    with open("data/settings.json", "r", encoding="utf-8") as file:
        return json.load(file)


def save_file(new_thinks, file_path):
    try:
        os.remove(file_path)
    except:
        pass
    with open(file_path, "w") as file:
        file.write(new_thinks)


def get_lang(settings, state=0):
    if state == 1 or settings["language"] is None:
        lang_list = ["en", "it", "tr"]
        while True:
            clear()
            x = int(input('''
    1) English
    2) Italiano
    3) Türkçe 
    
    Select your language: '''))
            if 1 <= x <= len(lang_list):
                settings["language"] = lang_list[x - 1]
                save_file(json.dumps(settings), "data/settings.json")
                break

    with open("data/lang/lang_" + settings["language"] + ".json", "r", encoding="utf-8") as file:
        return json.load(file)
