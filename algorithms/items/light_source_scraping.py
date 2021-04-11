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

URL = "https://terraria.gamepedia.com/"
LIGHT_SOURCE_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + LIGHT_SOURCE_NAME_FILE + JSON_EXT
DATA_TO_BE_SCRAPPED = [SCRAPING_HOUSE, SCRAPING_MECHANISM, SCRAPING_WATERPROOF]
GENERAL_LIGHT_SOURCES = ["Torch", "Candle", "Candelabra", "Lantern", "Chandelier", "Lamps"]

newURL = URL + "Light_sources"
pageLightSources = requests.get(newURL)
soupLightSources = BeautifulSoup(pageLightSources.content, "html.parser")

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get light source list to process
lightSourceListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Light source":
        lightSourceListToProcess.append(itemInstance)

lightSourcesList = []

@start_threads_decorator(size=len(lightSourceListToProcess), threads_number=THREADS_SIZE)
def lightSourceScraping(init, fin, threadID):
    for lightInstance in lightSourceListToProcess[init:fin]:
        newURL = URL + lightInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, lightInstance[SCRAPING_ID]))
    
        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == lightInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp

        lightSourceDict = get_statistics(tableBox, itemInstance=lightInstance)

        lightSourcesList.append(lightSourceDict)
              
SaveJSONFile(LIGHT_SOURCE_PATH, sortListOfDictsByKey(lightSourcesList, SCRAPING_ITEM_ID))
