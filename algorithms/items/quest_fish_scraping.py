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

QUEST_FISH_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + QUEST_FISH_NAME_FILE + JSON_EXT
questFishDictList = []

URL = "https://terraria.gamepedia.com/Angler/Quests"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
table = soup.find("table", class_=TERRARIA_TABLE_CLASS)
rows = table.findAll("tr")
for row in rows[1::]:
    cols = row.findAll("td")
    questFishDict = {
        SCRAPING_ITEM_ID: "",
        SCRAPING_RARITY: "-11",
        SCRAPING_HEIGHT: "",
        SCRAPING_BIOME: "",
        SCRAPING_ANGLER_QUOTE: ""
    }
    string = cols[0].text
    questFishDict[SCRAPING_ANGLER_QUOTE] = string[:string.find("(")]
    questFishDict[SCRAPING_ITEM_ID] = re.search("\d+", cols[2].find("div", class_="id").text).group()
    print("Getting information from ID " + questFishDict[SCRAPING_ITEM_ID])
    questFishDict[SCRAPING_HEIGHT] = cols[3].text.replace("\n", "")
    questFishDict[SCRAPING_BIOME] = cols[4].text.replace("\n", "").replace("[1]", "")
    questFishDictList.append(questFishDict)

SaveJSONFile(QUEST_FISH_PATH, sorted(questFishDictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))

