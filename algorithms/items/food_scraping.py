#Load 3-level parent directories
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
from bs4 import BeautifulSoup
import requests

FOOD_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + FOOD_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

# Get food list to process
foodListToProcess = []
for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Food":
        foodListToProcess.append(itemInstance)

foodList = []

pageFoods = requests.get(URL + "Food_and_drink_potions")
soupFoods = BeautifulSoup(pageFoods.content, "html.parser")

def get_desktop_text(foodRow):
    eicos = foodRow.find_all("span", class_="eico")
    if eicos:
        for eico in eicos:
            re.search("Desktop", eico.find("img")["alt"])
            return eico.parent.text
    else:
        return foodRow.text

@start_threads_decorator(size=len(foodListToProcess), threads_number=THREADS_SIZE)
def foodScraping(init, fin, threadID):
    for foodInstance in foodListToProcess[init:fin]:
        newURL = URL + foodInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("Thread {}: Processing {} with ID {}".format(threadID, newURL, foodInstance[SCRAPING_ID]))

        tableBox = soup.find("div", class_="infobox item")
        foodList.append(get_statistics(tableBox, itemInstance=foodInstance))
    
SaveJSONFile(FOOD_PATH, sortListOfDictsByKey(foodList, SCRAPING_ITEM_ID))
