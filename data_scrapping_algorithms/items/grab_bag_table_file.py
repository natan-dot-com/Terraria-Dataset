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

bagList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ITEMS_DATA + GRAB_BAG_NAME_FILE + JSON_EXT)
itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

newList = []
IDcounter = 1
for bagInstance in bagList:
    newDict = {
        BAG_ID: "",
        SCRAPING_NAME: "",
        GRAB_BAGS_LOOT_LIST: [],
    } 
    newDict[BAG_ID] = str(IDcounter)
    newDict[SCRAPING_NAME] = itemList[int(bagInstance[SCRAPING_ITEM_ID])-1][SCRAPING_NAME]
    print("Processing " + newDict[SCRAPING_NAME]) 
    newList.append(newDict)
    IDcounter += 1
SaveJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + BAGS_NAME_FILE + JSON_EXT, newList)
