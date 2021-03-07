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
from ...package.multithreading_starter import *
from bs4 import BeautifulSoup
import requests
import threading
import math

FURNITURE_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + FURNITURE_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"
OTHER_FOUNDS = ["Dungeon", "Obsidian"]
OTHER_FOUNDS_SOURCE = ["Found in the Dungeon", "Found in Ruined Houses, in the Underworld"]

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
furnituresList = []

@start_threads_decorator(size=len(itemList), threads_number=8)
def furniturescraping(init, fin, threadID):
    for itemInstance in itemList[init:fin]:
        if itemInstance[SCRAPING_TYPE] == "Furniture":
            newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
            page = requests.get(newURL)
            soup = BeautifulSoup(page.content, "html.parser")
            print("Thread {}: Processing {} with ID {}".format(threadID, newURL, itemInstance[SCRAPING_ID]))

            tableBoxes = soup.find_all("div", class_="infobox item")
            tableBox = tableBoxes[0]
            for tableBoxTmp in tableBoxes:
                if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                    tableBox = tableBoxTmp
            furnitureDict = get_statistics(tableBox, itemInstance=itemInstance)

            furnitureDict.pop(SCRAPING_SOURCE)
            furnitureSourceOther = ""
            for otherFoundInstance, otherFoundSourceInstance in zip(OTHER_FOUNDS, OTHER_FOUNDS_SOURCE):
                if re.search(otherFoundInstance, itemInstance[SCRAPING_NAME]) and not re.search("Sink|Obsidian Watcher Banner", itemInstance[SCRAPING_NAME]):
                    furnitureSourceOther = otherFoundSourceInstance
                    break
                elif itemInstance[SCRAPING_NAME] == "Book":
                    furnitureSourceOther = "Found in the Dungeon"

            furnitureDict[SCRAPING_SOURCE] = {
                SOURCE_RECIPES: [],
                SOURCE_NPC: [],
                SOURCE_DROP: [],
                SOURCE_GRAB_BAG: [],
                SOURCE_OTHER: furnitureSourceOther,
            }

            furnituresList.append(furnitureDict)

SaveJSONFile(FURNITURE_PATH, sortListOfDictsByKey(furnituresList, SCRAPING_ITEM_ID))
