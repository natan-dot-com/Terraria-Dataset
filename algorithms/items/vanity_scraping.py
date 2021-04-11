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

VANITY_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + VANITY_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get vanity list to process
vanityListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Vanity":
        vanityListToProcess.append(itemInstance)

vanityList = []

@start_threads_decorator(size=len(vanityListToProcess), threads_number=THREADS_SIZE)
def vanityScraping(init, fin, threadID):
    for vanityInstance in vanityListToProcess[init:fin]:
        newURL = URL + vanityInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, vanityInstance[SCRAPING_ID]))

        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == vanityInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp

        vanityList.append(get_statistics(tableBox, itemInstance=vanityInstance))

SaveJSONFile(VANITY_PATH, sortListOfDictsByKey(vanityList, SCRAPING_ITEM_ID))
