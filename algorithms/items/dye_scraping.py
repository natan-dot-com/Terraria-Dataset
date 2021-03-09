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
    os.chdir("../../../")
from ...package.scraping_tools import *
from ...package.json_manager import *
from ...package.multithreading_starter import *

POTION_PATH = GLOBAL_JSON_PATH + DYE_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)
dyeList = []

@start_threads_decorator(size=len(itemList), threads_number=8)
def potionScraping(init, fin, threadID):
    for itemInstance in itemList[init:fin]:
        if itemInstance[SCRAPING_TYPE] == "Dye":
            print("Thread {}: Processing {} with ID {}".format(threadID, itemInstance[SCRAPING_NAME], itemInstance[SCRAPING_ID]))
            dyeDict = {}
            dyeDict[SCRAPING_NAME] = itemInstance[SCRAPING_NAME]
            dyeDict[SCRAPING_ITEM_ID] = itemInstance[SCRAPING_ID]
            dyeDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
            dyeList.append(dyeDict)
        
SaveJSONFile(POTION_PATH, sortListOfDictsByKey(dyeList, SCRAPING_ITEM_ID))