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
from bs4 import BeautifulSoup
import re
import requests

IN_STONE_SUFFIX = "_In_Stone.png"
PLACED_SUFFIX = "_Placed.png"
SUFFIX_LIST = [IN_STONE_SUFFIX, PLACED_SUFFIX]
DICT_INFO_LIST = [IMAGE_IN_STONE, IMAGE_PLACED]

GEM_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + GEM_NAME_FILE + JSON_EXT
COLS_LIST = [2, 4]

URL = "https://terraria.gamepedia.com/Gems"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
table = soup.find("table", class_=TERRARIA_TABLE_CLASS)
if table:
    gemDictList = []
    rows = table.findAll("tr")
    for row in rows[1::]:
        cols = row.findAll("td")
        gemDict = {
            SCRAPING_ITEM_ID: "",
            SCRAPING_RARITY: "1",
            IMAGE_IN_STONE: "",
            IMAGE_PLACED: ""
        }
        getID = re.search("\d+", (cols[0].find("div", class_="id").text))
        gemDict[SCRAPING_ITEM_ID] = getID.group()
        print("Getting information from ID " + gemDict[SCRAPING_ITEM_ID])
        
        gemName = cols[0].find("img")['alt']
        for suffixIdentity, colsIdentity, dictInfoIdentity in zip(SUFFIX_LIST, COLS_LIST, DICT_INFO_LIST):
            imgSrc = cols[colsIdentity].find("img")['src']
            imgPath = IMAGE_DIR_GEMS + gemName + suffixIdentity
            
            imgOutput = requests.get(imgSrc, stream=True)
            if imgOutput.ok:
                with open(GLOBAL_JSON_PATH + imgPath, "wb+") as handler:
                    for block in imgOutput.iter_content(1024):
                        if not block:
                            break
                        handler.write(block)
            gemDict[dictInfoIdentity] = imgPath
        gemDictList.append(gemDict)
SaveJSONFile(GEM_PATH, sorted(gemDictList, key = lambda i: i[SCRAPING_ITEM_ID]))


