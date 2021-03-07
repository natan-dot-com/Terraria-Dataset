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
import re
import requests

KEY_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + KEY_NAME_FILE + JSON_EXT
keyDictList = []

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

URL = "https://terraria.gamepedia.com/Keys"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
table = soup.find("table", class_=TERRARIA_TABLE_CLASS)
rows = table.findAll("tr")
for row in rows[1::]:
    cols = row.findAll("td")
    keyDict = {
        SCRAPING_ITEM_ID: "",
        SCRAPING_USED_IN: "",
        SCRAPING_CONSUMED: "",
        SCRAPING_SOURCE: {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: ""
        }
    }
    keyDict[SCRAPING_ITEM_ID] = searchForID(cols[0].find("img")['alt'], itemList)
    print("Getting information from ID " + keyDict[SCRAPING_ITEM_ID])

    if cols[2].find("img"):
        keyDict[SCRAPING_USED_IN] = cols[2].find("img")['alt'].replace(".png", "")
    else:
        keyDict[SCRAPING_USED_IN] = cols[2].find("a")['title']

    keyDict[SCRAPING_CONSUMED] = cols[3].img['alt']

    # Drop dict as PLACEHOLDER. It will be in the drop-data json.
    if re.search("Drop", cols[1].text, re.IGNORECASE):
        if not re.search("Plantera", cols[1].text):
            dropDict = {
                DROP_ID: "",
                DROP_NPC: "",
                DROP_PROBABILITY: "",
                DROP_QUANTITY: "",
            }
            string = "Hardmode drop in"
            for biome in cols[1].findAll("a"):
                string += " " + biome.text + ","
            string = string[:-1] + "."
            dropDict[DROP_NPC] = string
            dropDict[DROP_PROBABILITY] = "0.04%"

            dropDict[DROP_QUANTITY] = "1"
            keyDict[SCRAPING_SOURCE][SOURCE_DROP].append(dropDict)

    elif not re.search("Soul", cols[1].text):
        if cols[1].find("img"):
            keyDict[SCRAPING_SOURCE][SOURCE_OTHER] = cols[1].find("img")['alt']
        else:
            keyDict[SCRAPING_SOURCE][SOURCE_OTHER] = cols[1].a['title']
    keyDictList.append(keyDict)
SaveJSONFile(KEY_PATH, sorted(keyDictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
