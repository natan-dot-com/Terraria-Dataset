#Everything seems to work.

# Load 3-level parent directories
from importlib import import_module
import path_manager
if __name__ == '__main__' and __package__ == None:
    __package__ = path_manager.importParents(level=3)
    import_module(__package__)

# Setting the root directory as working directory for Linux systems
from platform import system
from pathlib import Path
import os
systemOS = system()
if systemOS == "Linux":
    os.chdir("../../")

from ...package.scraping_tools import *
from ...package.json_manager import *
import requests
from bs4 import BeautifulSoup

WEAPON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + WEAPON_NAME_FILE + JSON_EXT
ITEM_URL = ["Enchanted Sword"]
WIKI_URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
weaponsList = []

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Weapon":
        newURL = WIKI_URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        if itemInstance[SCRAPING_NAME] in ITEM_URL:
            newURL += "_(item)"
        print("Processing " + newURL + " with ID " + itemInstance[SCRAPING_ID])
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        tableBox = soup.find("div", class_="infobox item")

        weaponsList.append(get_statistics(tableBox, itemInstance))

SaveJSONFile(WEAPON_PATH, weaponsList)
