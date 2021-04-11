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

# Get potion list to process
potionListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Potion":
        potionListToProcess.append(itemInstance)

potionList = []

@start_threads_decorator(size=len(potionListToProcess), threads_number=THREADS_SIZE)
def potionScraping(init, fin, threadID):
    for potionInstance in potionListToProcess[init:fin]:
        newURL = URL + potionInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, potionInstance[SCRAPING_ID]))

        tableBox = soup.find("div", class_="infobox item")
        potionList.append(get_statistics(tableBox, itemInstance=potionInstance))
        
SaveJSONFile(POTION_PATH, sortListOfDictsByKey(potionList, SCRAPING_ITEM_ID))
