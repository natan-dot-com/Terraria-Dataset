#Everything seems to work.
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
import re
import requests
from bs4 import BeautifulSoup

TOOL_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + TOOL_NAME_FILE + JSON_EXT
FISHING_POLES = [
    "Wood Fishing Pole", "Reinforced Fishing Pole", "Fisher of Souls", "Fleshcatcher",
    "Scarab Fishing Rod", "Chum Caster", "Fiberglass Fishing Pole", "Mechanic's Rod",
    "Sitting Duck's Fishing Pole", "Hotline Fishing Hook", "Golden Fishing Rod"
]

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
url = "https://terraria.gamepedia.com/"
toolsList = []

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Tool":
        newURL = url + itemInstance[SCRAPING_NAME].replace(" ", "_")
        print("Processing " + newURL + " with ID " + itemInstance[SCRAPING_ID])
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")

        if not itemInstance[SCRAPING_NAME] in FISHING_POLES:
            tableBox = soup.find("div", class_="infobox item")
            toolDict = get_statistics(tableBox, itemInstance)
            toolsList.append(toolDict)
            
        #get fishing poles
        else:
            trTags = soup.find("table", id="fishing-poles-table").find_all("tr")
            for trTag in trTags[1:]:
                tdTags = trTag.find_all("td")
                if tdTags[1].span.span.span.text == itemInstance[SCRAPING_NAME]:
                    toolDict = {
                        SCRAPING_ITEM_ID: "",
                        SCRAPING_NAME: "",
                        SCRAPING_RARITY: "",
                        SCRAPING_VELOCITY: "",
                        SCRAPING_FISHING_POWER: "",
                        SCRAPING_SOURCE: SOURCE_SOURCES_DICT
                    }
                    
                    toolDict[SCRAPING_ITEM_ID] = itemInstance[SCRAPING_ID]
                    toolDict[SCRAPING_NAME] = itemInstance[SCRAPING_NAME]
                    toolDict[SCRAPING_FISHING_POWER] = tdTags[3].text.rstrip()
                    toolDict[SCRAPING_VELOCITY] = tdTags[4].text.rstrip()
                    toolDict[SCRAPING_RARITY] = (re.search("-*\d+", tdTags[6].a["title"])).group()
                    statistics = soup.find("div", class_="infobox item").find("div", class_="section statistics").find_all("tr")
                    for statistic in statistics:
                        if statistic.th.text == SCRAPING_USE_TIME:
                            toolDict[SCRAPING_USE_TIME] = statistic.td.text.rstrip()
                    toolsList.append(toolDict)
                    break

SaveJSONFile(TOOL_PATH, toolsList)
