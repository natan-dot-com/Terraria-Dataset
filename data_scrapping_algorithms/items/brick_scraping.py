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
import requests

BRICK_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BRICK_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"
URL_BRICKS = "Bricks"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
bricksList = []

pageBricks = requests.get(URL + URL_BRICKS)
soupBricks = BeautifulSoup(pageBricks.content, "html.parser")
bricksRows = soupBricks.find("table").find_all("tr")[1:]

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Brick":
        newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("processing {}".format(newURL))

        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        brickDict = get_statistics(tableBox, itemInstance=itemInstance)

        brickDict.pop(SCRAPING_SOURCE, None)
        brickSourceOther = ""
        for bricksRow in bricksRows:
            if bricksRow.find_all("td")[0].a["title"] == itemInstance[SCRAPING_NAME]:
                brickDict[SCRAPING_DESTROYED_BY_EXPLOSIVES] = bricksRow.find_all("td")[3].img["alt"]
                if re.search("Looted", bricksRow.find_all("td")[2].text):
                    brickSourceOther = bricksRow.find_all("td")[2].text.rstrip()
                break

        brickDict[SCRAPING_SOURCE] = {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: brickSourceOther,
        }
        bricksList.append(brickDict)

SaveJSONFile(BRICK_PATH, bricksList)
