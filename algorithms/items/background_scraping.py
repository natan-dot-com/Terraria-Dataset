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
import requests
from bs4 import BeautifulSoup

BACKGROUND_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BACKGROUND_NAME_FILE + JSON_EXT
WALLS_SUBTYPES = {
    "Stained Glass", "Wallpapers", "Fences", "Gemstone Walls",
    "Cave Walls", "Mossy Walls", "Sandstone Walls", "Corruption Walls"
}
DUNGEON_WALLS = {
    "Blue Brick Wall", "Green Brick Wall", "Pink Brick Wall",
    "Blue Slab Wall", "Green Slab Wall", "Pink Slab Wall",
    "Blue Tiled Wall", "Green Tiled Wall", "Pink Tiled Wall"
}

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get background list to process
backgroundListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Background":
        backgroundListToProcess.append(itemInstance)

wallsList = []
url = "https://terraria.gamepedia.com/"

@start_threads_decorator(size=len(backgroundListToProcess), threads_number=THREADS_SIZE)
def backgroundScraping(init, fin, threadID):
    for backgroundInstance in backgroundListToProcess:
        newURL = url + backgroundInstance[SCRAPING_NAME].replace(" ", "_")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, backgroundInstance[SCRAPING_ID]))
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")

        if not backgroundInstance[SCRAPING_NAME] in DUNGEON_WALLS:
            tableBoxes = soup.find_all("div", class_="infobox item")
        elif backgroundInstance[SCRAPING_NAME] in DUNGEON_WALLS:       
            tableBoxes = soup.find_all("div", class_="infobox item float-left")
        else:
            tableBoxes = soup.find_all("div", class_="infobox npc c-normal background object")

        #find the correct wall table
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text in WALLS_SUBTYPES:
                tableBox = tableBoxTmp
                break

        wallDict = get_statistics(tableBox, backgroundInstance)
        wallsList.append(wallDict)

SaveJSONFile(BACKGROUND_PATH, wallsList)
