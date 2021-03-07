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
PYLON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + PYLON_NAME_FILE + JSON_EXT

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
pylonsList = []

newURL = URL + "Pylons"
page = requests.get(newURL)
soup = BeautifulSoup(page.content, "html.parser")

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Pylon":
        tableBox = soup.find("div", class_="infobox item")
        pylonDict = get_statistics(tableBox, itemInstance=itemInstance)

        pylonTable = soup.find("table", class_=TERRARIA_TABLE_CLASS).find_all("tr")
        for pylonRow in pylonTable[1:]:
            if pylonRow.find("td", class_="il1c").img["alt"] == itemInstance[SCRAPING_NAME]:
                pylonDict.pop(SCRAPING_SOURCE, None)
                if pylonRow.find("sup"):
                    pylonDict[SCRAPING_USABLE] = pylonRow.find_all("td")[6].contents[0].rstrip()
                else:
                    pylonDict[SCRAPING_USABLE] = pylonRow.find_all("td")[6].text.rstrip()
        
        pylonDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
        pylonsList.append(pylonDict)
    
SaveJSONFile(PYLON_PATH, pylonsList)
