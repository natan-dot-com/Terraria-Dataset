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
STORAGE_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + STORAGE_NAME_FILE + JSON_EXT
STORAGE_WITH_SOURCES = [
    "Blue Dungeon Dresser", "Green Dungeon Dresser", "Pink Dungeon Dresser", "Obsidian Dresser"
]

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get storage list to process
storageListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Storage":
        storageListToProcess.append(itemInstance)

storageList = []

@start_threads_decorator(size=len(storageListToProcess), threads_number=THREADS_SIZE)
def storageScraping(init, fin, threadID):
    for storageInstance in storageListToProcess[init:fin]:
        newURL = URL + storageInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, storageInstance[SCRAPING_ID]))
    
        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == storageInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        storageDict = get_statistics(tableBox, itemInstance=storageInstance)

        storageDict.pop(SCRAPING_SOURCE)
        storageSourceOther = ""
        if storageInstance[SCRAPING_NAME] in STORAGE_WITH_SOURCES:
            newURL = URL + "Dressers"
            pageDresser = requests.get(newURL)
            soupDresser = BeautifulSoup(pageDresser.content, "html.parser")
            tableRows = soupDresser.find("table", class_="terraria lined").find_all("tr")[1:]

            for tableRow in tableRows:
                if tableRow.find("img")["alt"] == storageInstance[SCRAPING_NAME]:
                    storageSourceOther = tableRow.find_all("td")[1].text.strip()

        elif re.search("Chest", storageInstance[SCRAPING_NAME]):
            newURL = URL + "Chests"
            pageChest = requests.get(newURL)
            soupChest = BeautifulSoup(pageChest.content, "html.parser")
            tableRows = soupChest.find("table", class_="terraria lined").find_all("tr")[1:]

            for tableRow in tableRows:
                if tableRow.find("img")["alt"] == storageInstance[SCRAPING_NAME]:
                    textHTML = BeautifulSoup(str(tableRow.find_all("td")[1]).replace("<br/>", ","), 'html.parser')
                    storageSourceOther = "Found in " + textHTML.text.replace(" ,", ",").strip()

        storageDict[SCRAPING_SOURCE] = {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: storageSourceOther,
        }

        storageList.append(storageDict)
              
    
SaveJSONFile(STORAGE_PATH, sortListOfDictsByKey(storageList, SCRAPING_ITEM_ID))
