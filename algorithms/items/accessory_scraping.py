#Load 3-level parent directories
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

URL = "https://terraria.gamepedia.com/"
ACCESSORY_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + ACCESSORY_NAME_FILE + JSON_EXT

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get accessory list to process
accessoryListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Accessory":
        accessoryListToProcess.append(itemInstance)

accessoryList = []

@start_threads_decorator(size=len(accessoryListToProcess), threads_number=THREADS_SIZE)
def accessoryScraping(init, fin, threadID):
    for accessoryInstance in accessoryListToProcess[init:fin]:
        newURL = URL + accessoryInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, accessoryInstance[SCRAPING_ID]))

        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == accessoryInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        accessoryList.append(get_statistics(tableBox, itemInstance=accessoryInstance))


SaveJSONFile(ACCESSORY_PATH, sortListOfDictsByKey(accessoryList, SCRAPING_ITEM_ID))
