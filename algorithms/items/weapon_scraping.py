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
from ...package.multithreading_starter import start_threads_decorator
import requests
from bs4 import BeautifulSoup

WEAPON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + WEAPON_NAME_FILE + JSON_EXT
ITEM_URL = ["Enchanted Sword"]
WIKI_URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get weapon list to process
weaponListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Weapon":
        weaponListToProcess.append(itemInstance)

weaponList = []

@start_threads_decorator(size=len(weaponListToProcess), threads_number=THREADS_SIZE)
def weaponScraping(init, fin, threadID):
    for weaponInstance in weaponListToProcess[init:fin]:
        newURL = WIKI_URL + weaponInstance[SCRAPING_NAME].replace(" ", "_")
        if weaponInstance[SCRAPING_NAME] in ITEM_URL:
            newURL += "_(item)"
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, weaponInstance[SCRAPING_ID]))
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        tableBox = soup.find("div", class_="infobox item")

        weaponList.append(get_statistics(tableBox, weaponInstance))

SaveJSONFile(WEAPON_PATH, sortListOfDictsByKey(weaponList, SCRAPING_ITEM_ID))
