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

#put the name of category in input
nameFile = input("Name File: ")
NAME_FILE = "items_" + nameFile.lower()

itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)
compareList = LoadJSONFile(GLOBAL_JSON_PATH + NAME_FILE + JSON_EXT)

found = 0
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE].lower() == NAME_FILE:
        for compareInstance in compareList:
            if  itemInstance[SCRAPING_NAME] == compareInstance[SCRAPING_NAME]:
                found = 1
                break
            if not found:
                print("{} Not found on compareList".format(itemInstance[SCRAPING_NAME]))
            found = 0

found = 0
for compareInstance in compareList:
    for itemInstance in itemList:
        if itemInstance[SCRAPING_NAME] == compareInstance[SCRAPING_NAME]:
            if itemInstance[SCRAPING_TYPE].lower() == nameFile:
                found = 1
                break
            else:
                print("{} Not found on itemList with type {}".format(compareInstance[SCRAPING_NAME], nameFile))
    found = 0