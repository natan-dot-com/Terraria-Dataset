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

POTION_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + POTION_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
potionList = []

@start_threads_decorator(size=len(itemList), threads_number=8)
def potionScraping(init, fin, threadID):
    for itemInstance in itemList[init:fin]:
        if itemInstance[SCRAPING_TYPE] == "Potion":
            newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
            page = requests.get(newURL)
            soup = BeautifulSoup(page.content, "html.parser")
            print("Thread {}: Processing {} with ID {}".format(threadID, newURL, itemInstance[SCRAPING_ID]))

            tableBox = soup.find("div", class_="infobox item")
            potionList.append(get_statistics(tableBox, itemInstance=itemInstance))
        
SaveJSONFile(POTION_PATH, sortListOfDictsByKey(potionList, SCRAPING_ITEM_ID))
