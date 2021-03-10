# Load 3-level parent directories
from importlib import import_module
import path_manager
if __name__ == '__main__' and __package__ == None:
    __package__ = path_manager.importParents(level=3)
    import_module(__package__)

# Setting the root directory as working directory for Linux systems
from platform import system
import os
systemOS = system()
if systemOS == "Linux":
    os.chdir("../../")
from ..package.scraping_tools import *
from ..package.json_manager import *

for file in os.listdir(GLOBAL_JSON_PATH + DIR_ITEMS_DATA):
    if os.path.splitext(file)[1] == JSON_EXT:
        jsonList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ITEMS_DATA + str(file))
        for jsonInstance in jsonList:
            if not SCRAPING_SOURCE in jsonInstance.keys():
                continue
            #print("Removing: {}".format(jsonInstance[SCRAPING_SOURCE]))
            jsonInstance[SCRAPING_SOURCE][SOURCE_RECIPES] = []
            jsonInstance[SCRAPING_SOURCE][SOURCE_NPC] = []
            jsonInstance[SCRAPING_SOURCE][SOURCE_DROP] = []
            jsonInstance[SCRAPING_SOURCE][SOURCE_GRAB_BAG] = []
        SaveJSONFile(GLOBAL_JSON_PATH + DIR_ITEMS_DATA + file, jsonList)