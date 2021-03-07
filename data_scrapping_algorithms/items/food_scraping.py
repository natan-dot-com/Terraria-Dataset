import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir) 
from scraping_tools import *
from json_manager import *
from bs4 import BeautifulSoup
import requests
from multithreading_starter import start_threads_decorator

FOOD_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + FOOD_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
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

@start_threads_decorator(size=len(itemList), threads_number=8)
def bossSummonsScraping(init, fin, threadID):
    for itemInstance in itemList[init:fin]:
        if itemInstance[SCRAPING_TYPE] == "Food":
            newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
            page = requests.get(newURL)
            soup = BeautifulSoup(page.content, "html.parser")
            print("Thread {}: Processing {} with ID {}".format(threadID, newURL, itemInstance[SCRAPING_ID]))

            tableBox = soup.find("div", class_="infobox item")
            foodList.append(get_statistics(tableBox, itemInstance=itemInstance))
        
SaveJSONFile(FOOD_PATH, sortListOfDictsByKey(foodList, SCRAPING_ITEM_ID))
