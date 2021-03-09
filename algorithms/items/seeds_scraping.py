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

URL = "https://terraria.gamepedia.com/"
SEEDS_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + SEEDS_NAME_FILE + JSON_EXT

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
seedsList = []

newURL = URL + "Seeds"
pageSeeds = requests.get(newURL)
soupSeeds = BeautifulSoup(pageSeeds.content, "html.parser")

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Seeds":
        newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("processing {}".format(newURL))
        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        
        seedDict = get_statistics(tableBox, itemInstance=itemInstance)

        seedDict.pop(SCRAPING_SOURCE, None)
        seedsTables = soupSeeds.find_all("table", class_=TERRARIA_TABLE_CLASS)
        found = 0
        for seedsTable in seedsTables:
            seedsTags = seedsTable.find_all("tr")
            for seedsRows in seedsTags[1:]:
                if seedsRows.find("td").find("img")["alt"] == itemInstance[SCRAPING_NAME]:
                    seedDict[SCRAPING_CREATES] = seedsRows.find_all("td")[1].text.rstrip()
                    seedDict[SCRAPING_PLANTED_IN] = seedsRows.find_all("td")[2].text.rstrip()
                    found = 1
                    break
            if found:
                break
        
        seedDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
        seedsList.append(seedDict)
    
SaveJSONFile(SEEDS_PATH, seedsList)
