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

# List of strings that we must ignore (since they're related to drops)
DROP_LIST = ["Eater of Worlds", "Eye of Cthulhu", "Brain of Cthulhu", "Ocram", "Moon Lord"]

IN_STONE_SUFFIX = "_In_Stone"
ORE_PATH = GLOBAL_JSON_PATH + ORE_NAME_FILE + JSON_EXT
oreDictList = []

URL = "https://terraria.gamepedia.com/Ores"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
tables = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)

# Getting data from the first table (Relevant: ID and Rarity)
rows = tables[0].findAll("tr")
for row in rows[1::]:
    oreDict = {
        SCRAPING_ITEM_ID: "",
        SCRAPING_ORE_TIER: "",
        SCRAPING_RARITY: "",
        SCRAPING_MINIMUM_PICKAXE_POWER: "",
        IMAGE_IN_STONE: "",
        SCRAPING_SOURCE: {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: ""
        }
    }
    cols = row.findAll("td")
    oreDict[SCRAPING_ITEM_ID] = (re.search("\d+", cols[1].div.text)).group()
    oreDict[SCRAPING_RARITY] = (re.search("\d+", cols[2].a['title'])).group()
    oreDictList.append(oreDict)

# Getting data from the second/third table (Relevant: the other ones)
oreIndex = 0
for table in tables[1:3:]:
    rows = table.findAll("tr")
    for row in rows[1::]:
        cols = row.findAll("td")
        colsNumber = len(cols)
        
        # For when there's just one ore in the table row
        if colsNumber == 4:
            
            # Table row header (ore tier)
            oreDictList[oreIndex][SCRAPING_ORE_TIER] = (re.search("\d+", row.th.text)).group()
            print("Getting information from ID " + oreDictList[oreIndex][SCRAPING_ITEM_ID])
            
            # First column (image)
            colImages = cols[0].findAll("img")
            imgPath = DIR_ITEMS_DATA + IMAGE_DIR_ORES + colImages[1]['alt'].replace(" ", "_") + IN_STONE_SUFFIX + STATIC_IMAGE_EXT
            writeImage(colImages[0]['src'], GLOBAL_JSON_PATH + imgPath)
            oreDictList[oreIndex][IMAGE_IN_STONE] = imgPath
            
            # Second column (pickaxe power)
            oreDictList[oreIndex][SCRAPING_MINIMUM_PICKAXE_POWER] = (cols[1].find("img"))['alt']
            
            # Fourth column (source)
            allSources = cols[3].text.replace("\n", "").split(", ")
            biomeSources = []
            for source in allSources:
                biomeSourceFlag = True
                for npc in DROP_LIST:
                    if re.search(npc, source):
                        biomeSourceFlag = False
                        break
                if biomeSourceFlag:
                    biomeSources.append(source)
                
            oreDictList[oreIndex][SCRAPING_SOURCE][SOURCE_OTHER] = ", ".join(biomeSources)
            oreIndex += 1
            
        # For when there's two ores in the same table row
        if colsNumber == 5:
            
            print("Getting information from ID " + oreDictList[oreIndex][SCRAPING_ITEM_ID])
            print("Getting information from ID " + oreDictList[oreIndex+1][SCRAPING_ITEM_ID])

            # Table row header (ore tier)
            oreDictList[oreIndex][SCRAPING_ORE_TIER] = (re.search("\d+", row.th.text)).group()
            oreDictList[oreIndex+1][SCRAPING_ORE_TIER] = (re.search("\d+", row.th.text)).group()
            
            # First column (first ore image)
            colImages = cols[0].findAll("img")
            imgPath = DIR_ITEMS_DATA + IMAGE_DIR_ORES + colImages[1]['alt'].replace(" ", "_") + IN_STONE_SUFFIX + STATIC_IMAGE_EXT
            writeImage(colImages[0]['src'], GLOBAL_JSON_PATH + imgPath)
            oreDictList[oreIndex][IMAGE_IN_STONE] = imgPath
            
            # Second column (second ore image)
            colImages = cols[1].findAll("img")
            imgPath = DIR_ITEMS_DATA + IMAGE_DIR_ORES + colImages[1]['alt'].replace(" ", "_") + IN_STONE_SUFFIX + STATIC_IMAGE_EXT
            writeImage(colImages[0]['src'], GLOBAL_JSON_PATH + imgPath)
            oreDictList[oreIndex+1][IMAGE_IN_STONE] = imgPath
            
            # Third column (pickaxe power) 
            oreDictList[oreIndex][SCRAPING_MINIMUM_PICKAXE_POWER] = (cols[2].find("img"))['alt']
            oreDictList[oreIndex+1][SCRAPING_MINIMUM_PICKAXE_POWER] = (cols[2].find("img"))['alt']
            
            # Fifth column (source)
            allSources = cols[4].text.replace("\n", "").split(", ")
            biomeSources = []
            for source in allSources:
                biomeSourceFlag = True
                for npc in DROP_LIST:
                    if re.search(npc, source):
                        biomeSourceFlag = False
                        break
                if biomeSourceFlag:
                    biomeSources.append(source)
             
            oreDictList[oreIndex][SCRAPING_SOURCE][SOURCE_OTHER] = ", ".join(biomeSources)
            oreDictList[oreIndex+1][SCRAPING_SOURCE][SOURCE_OTHER] = ", ".join(biomeSources)
            oreIndex += 2
            
SaveJSONFile(ORE_PATH, sorted(oreDictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
