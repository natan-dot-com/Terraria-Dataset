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

SHIELD_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + SHIELD_NAME_FILE + JSON_EXT
itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
shieldsList = []

URL = "https://terraria.gamepedia.com/Shields"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
table = soup.find("table", class_=TERRARIA_TABLE_CLASS)
if table:
    rows = table.findAll("tr")
    for row in rows[2::]:
        cols = row.findAll("td")
        if cols:
            shieldsDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_EFFECT: [],
                SCRAPING_SOURCE: {
                    SOURCE_RECIPES: [],
                    SOURCE_NPC: [],
                    SOURCE_DROP: [],
                    SOURCE_GRAB_BAG: [],
                    SOURCE_OTHER: ""
                }
            }
            shieldsDict[SCRAPING_ITEM_ID] = searchForID(cols[0].find("img")['alt'], itemList)
            shieldEffects = cols[2].findAll("li")
            print("Getting information from ID " + shieldsDict[SCRAPING_ITEM_ID])

            for effect in shieldEffects:
                if effect.text:
                    shieldsDict[SCRAPING_EFFECT].append(effect.text.replace("\n", "").replace("\"", "").strip())

            if re.search("Chests", cols[1].text):
                keywords = cols[1].findAll("a")
                string = "Found in "
                for key in keywords:
                    if not key.find("img"):
                        string += key.text.strip() + ", "
                shieldsDict[SCRAPING_SOURCE][SOURCE_OTHER] = string[:-2]
            shieldsList.append(shieldsDict)
SaveJSONFile(SHIELD_PATH, sorted(shieldsList, key = lambda i: int(i[SCRAPING_ITEM_ID])))


