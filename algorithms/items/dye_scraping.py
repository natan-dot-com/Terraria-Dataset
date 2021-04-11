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

DYE_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + DYE_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get dye list to process
dyeListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Dye":
        dyeListToProcess.append(itemInstance)

dyeList = []

@start_threads_decorator(size=len(dyeListToProcess), threads_number=THREADS_SIZE)
def dyeScraping(init, fin, threadID):
    for dyeInstance in dyeListToProcess[init:fin]:
        print("Thread {}: Processing {} with ID {}".format(threadID, dyeInstance[SCRAPING_NAME], dyeInstance[SCRAPING_ID]))
        dyeDict = {}
        dyeDict[SCRAPING_NAME] = dyeInstance[SCRAPING_NAME]
        dyeDict[SCRAPING_ITEM_ID] = dyeInstance[SCRAPING_ID]
        dyeDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
        dyeList.append(dyeDict)
        
SaveJSONFile(DYE_PATH, sortListOfDictsByKey(dyeList, SCRAPING_ITEM_ID))