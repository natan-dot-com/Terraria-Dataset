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
url = "https://terraria.gamepedia.com/"
wallsList = []

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Background":
        newURL = url + itemInstance[SCRAPING_NAME].replace(" ", "_")
        print("Processing " + newURL + " with ID " + itemInstance[SCRAPING_ID])
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")

        if not itemInstance[SCRAPING_NAME] in DUNGEON_WALLS:
            tableBoxes = soup.find_all("div", class_="infobox item")
        elif itemInstance[SCRAPING_NAME] in DUNGEON_WALLS:       
            tableBoxes = soup.find_all("div", class_="infobox item float-left")
        else:
            tableBoxes = soup.find_all("div", class_="infobox npc c-normal background object")

        #find the correct wall table
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text in WALLS_SUBTYPES:
                tableBox = tableBoxTmp
                break

        wallDict = get_statistics(tableBox, itemInstance)
        wallsList.append(wallDict)

SaveJSONFile(BACKGROUND_PATH, wallsList)
