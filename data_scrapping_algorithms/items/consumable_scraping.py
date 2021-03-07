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
from bs4 import BeautifulSoup
import requests

CONSUMABLE_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + CONSUMABLE_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"
LIQUID_BOMBS = {"Dry Bomb", "Wet Bomb", "Lava Bomb", "Honey Bomb"}

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
consumablesList = []

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Consumable":
        newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("processing {}".format(newURL))

        if not itemInstance[SCRAPING_NAME] in LIQUID_BOMBS:
            tableBox = soup.find("div", class_="infobox item")
            consumableDict = get_statistics(tableBox, itemInstance=itemInstance)
            #Remove Sell key from Vine rope
            if itemInstance[SCRAPING_NAME] == "Vine Rope":
                consumableDict.pop("Sell", None)
            consumablesList.append(consumableDict)
        #If item is a liquid bomb
        else:
            tableBoxes = soup.find_all("div", class_="infobox item")
            tableBox = tableBoxes[0]
            for tableBoxTmp in tableBoxes:
                if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                    tableBox = tableBoxTmp
            consumablesList.append(get_statistics(tableBox, itemInstance=itemInstance))

SaveJSONFile(CONSUMABLE_PATH, consumablesList)
