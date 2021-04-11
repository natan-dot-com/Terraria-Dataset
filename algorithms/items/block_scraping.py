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
from bs4 import BeautifulSoup
import re
import requests

BLOCK_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BLOCK_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get block list to process
blockListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Block":
        blockListToProcess.append(itemInstance)

blockList = []

@start_threads_decorator(size=len(blockListToProcess), threads_number=THREADS_SIZE)
def blockScraping(init, fin, threadID):
    for blockInstance in blockListToProcess[init:fin]:
        newURL = URL + blockInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, blockInstance[SCRAPING_ID]))

        tableBox = soup.find("div", class_="infobox item")
        blockList.append(get_statistics(tableBox, itemInstance=blockInstance))
            
SaveJSONFile(BLOCK_PATH, sortListOfDictsByKey(blockList, SCRAPING_ITEM_ID))
