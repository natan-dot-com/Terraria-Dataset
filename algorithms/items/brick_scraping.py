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
import logging
from bs4 import BeautifulSoup
import requests

logging.basicConfig(format='%(asctime)s: %(message)s', filename=LOG_PATH + "brick_scraping.log", encoding='utf-8', level=logging.ERROR)

BRICK_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BRICK_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"
URL_BRICKS = "Bricks"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get brick list to process
brickListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Brick":
        brickListToProcess.append(itemInstance)

brickList = []


@start_threads_decorator(size=len(brickListToProcess), threads_number=THREADS_SIZE)
def brickScraping(init, fin, threadID):

    pageBricks = requests.get(URL + URL_BRICKS)
    soupBricks = BeautifulSoup(pageBricks.content, "html.parser")
    bricksRows = soupBricks.find("table").find_all("tr")[1:]
    for brickInstance in brickListToProcess[init:fin]:
        newURL = URL + brickInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, brickInstance[SCRAPING_ID]))

        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == brickInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        brickDict = get_statistics(tableBox, itemInstance=brickInstance)

        brickDict.pop(SCRAPING_SOURCE)
        brickSourceOther = ""
        for bricksRow in bricksRows:
            if bricksRow.find_all("td")[0].a["title"] == brickInstance[SCRAPING_NAME]:
                try:
                    if bricksRow.find_all("td")[3].span["class"][0] == "t-yes":
                        brickDict[SCRAPING_DESTROYED_BY_EXPLOSIVES] = "Yes"
                    elif bricksRow.find_all("td")[3].span["class"][0] == "t-no":
                        brickDict[SCRAPING_DESTROYED_BY_EXPLOSIVES] = "No"
                except:
                    logging.exception("ERROR: Could not scrap attribute '{}' on item '{}'\n".format(SCRAPING_DESTROYED_BY_EXPLOSIVES, brickInstance[SCRAPING_NAME]))
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
        brickList.append(brickDict)

SaveJSONFile(BRICK_PATH, sortListOfDictsByKey(brickList, SCRAPING_ITEM_ID))
