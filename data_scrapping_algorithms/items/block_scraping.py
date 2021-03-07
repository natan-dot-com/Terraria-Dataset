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
import re
import requests

BLOCK_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BLOCK_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
blockList = []

blockCounter = 0
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Block":
        newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("processing {}".format(newURL))

        tableBox = soup.find("div", class_="infobox item")
        blockList.append(get_statistics(tableBox, itemInstance=itemInstance))
        blockCounter += 1
        
SaveJSONFile(BLOCK_PATH, blockList)
