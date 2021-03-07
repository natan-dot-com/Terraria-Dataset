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

CRITTER_NAME_INDEX = 1
ENVIRONMENT_INDEX = 2
AI_TYPE_INDEX = 3
RARITY_INDEX = 4
SELL_INDEX = 5
BAIT_POWER_INDEX = 6
NOTES_INDEX = 7
NONE = "na"

CRITTER_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + CRITTER_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
critterList = []


page = requests.get(URL + "Critters")
soup = BeautifulSoup(page.content, "html.parser")

isNotCritter = 0
critterTables = soup.find_all("table", class_=TERRARIA_TABLE_CLASS)
for critterTable in critterTables:
    critterRows = critterTable.find_all("tr")[1:]
    for critterRow in critterRows:
        critterColumns = critterRow.find_all("td")
        critterDict = {}
        critterDict[SCRAPING_NAME] = critterColumns[CRITTER_NAME_INDEX].span.span.span.a["title"].rstrip()

        #Check if item is in critter category
        for itemInstance in itemList:
            if critterDict[SCRAPING_NAME] == itemInstance[SCRAPING_NAME]:
                if itemInstance[SCRAPING_TYPE] != "Critter":
                    isNotCritter = 1
                break
        if isNotCritter:
            isNotCritter = 0
            continue

        id = critterColumns[CRITTER_NAME_INDEX].find("div", class_="id")
        if not id:
            continue
        critterDict[SCRAPING_ITEM_ID] = (re.search("\d+", id.text)).group()
        print("Processing {} with ID {}".format(critterDict[SCRAPING_NAME], critterDict[SCRAPING_ITEM_ID]))
        if critterColumns[ENVIRONMENT_INDEX].text.strip() != "n/a":
            critterDict[SCRAPING_ENVIRONMENT] = critterColumns[ENVIRONMENT_INDEX].text.encode("ascii", "ignore").decode().strip().replace("/", " / ")
        critterDict[SCRAPING_AI_TYPE] = critterColumns[AI_TYPE_INDEX].text.strip()
        critterDict[SCRAPING_RARITY] = critterColumns[RARITY_INDEX].find("img")["alt"].split(": ")[-1].strip()
        critterDict[SCRAPING_SELL] = critterColumns[SELL_INDEX].span["title"].strip()
        if critterColumns[BAIT_POWER_INDEX].text.rstrip() != "n/a":
            critterDict[SCRAPING_BAIT_POWER] = critterColumns[BAIT_POWER_INDEX].text.strip()
        if len(critterColumns[NOTES_INDEX].text) > 1:
            critterDict[SCRAPING_NOTES] = critterColumns[NOTES_INDEX].text.encode("ascii", "ignore").decode().rstrip()
        critterDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
        critterList.append(critterDict)

SaveJSONFile(CRITTER_PATH, sortListOfDictsByKey(critterList, SCRAPING_ITEM_ID))
