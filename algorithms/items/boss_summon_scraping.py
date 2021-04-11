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
BOSS_SUMMON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + BOSS_SUMMON_NAME_FILE + JSON_EXT

newURL = URL + "Consumables"
pageConsumables = requests.get(newURL)
soupConsumables = BeautifulSoup(pageConsumables.content, "html.parser")

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get boss summon list to process
bossSummonListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Boss summon":
        bossSummonListToProcess.append(itemInstance)

bossSummonsList = []

@start_threads_decorator(size=len(bossSummonListToProcess), threads_number=THREADS_SIZE)
def bossSummonsScraping(init, fin, threadID):
    for bossSummonInstance in bossSummonListToProcess[init:fin]:
        newURL = URL + bossSummonInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, bossSummonInstance[SCRAPING_ID]))
    
        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == bossSummonInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
        bossSummonDict = get_statistics(tableBox, itemInstance=bossSummonInstance)

        bossSummonDict.pop(SCRAPING_SOURCE)
        bossSummonRows = soupConsumables.find_all("table")[4].find_all("tr")[1:]
        for bossSummonRow in bossSummonRows:
            if bossSummonRow.find("td").find("img")["alt"] == bossSummonInstance[SCRAPING_NAME]:
                bossSummonDict[SCRAPING_SUMMONS] = bossSummonRow.find_all("td")[2].text.strip()
                bossSummonDict[SCRAPING_USABLE] = bossSummonRow.find_all("td")[3].text.strip()

        bossSummonDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
        bossSummonsList.append(bossSummonDict)
              
SaveJSONFile(BOSS_SUMMON_PATH, sortListOfDictsByKey(bossSummonsList, SCRAPING_ITEM_ID))
