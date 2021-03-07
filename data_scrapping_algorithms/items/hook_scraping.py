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

ITEM_ID_COLUMN = 1
SOURCE_COLUMN = 2
REACH_COLUMN = 3
VELOCITY_COLUMN = 4
HOOKS_COLUMN = 5
LATCHING_COLUMN = 6
RARITY_COLUMN = 8

HOOK_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + HOOK_NAME_FILE + JSON_EXT
hooksDictList = []

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

URL = "https://terraria.gamepedia.com/Hooks"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
tables = []
tables.append(soup.find("table", { "id" : "Hooks-Pre-Hardmode-table" }))
tables.append(soup.find("table", { "id" : "Hooks-Hardmode-table" }))
for table in tables:
    rows = table.findAll("tr")
    for row in rows[1::]:
        hooksDict = {
            SCRAPING_ITEM_ID: "",
            SCRAPING_REACH: "",
            SCRAPING_VELOCITY: "",
            SCRAPING_HOOKS: "",
            SCRAPING_LATCHING: "",
            SCRAPING_RARITY: "",
            SCRAPING_SOURCE: ""
        }
        cols = row.findAll("td")
        
        # Scraping all the trivial information
        hooksDict[SCRAPING_ITEM_ID] = (re.search("\d+", cols[ITEM_ID_COLUMN].find("div", class_="id").text)).group()
        print("Getting information from ID " + hooksDict[SCRAPING_ITEM_ID])

        hooksDict[SCRAPING_REACH] = cols[REACH_COLUMN].text.replace("\n", "")
        hooksDict[SCRAPING_VELOCITY] = cols[VELOCITY_COLUMN].text.replace("\n", "")
        hooksDict[SCRAPING_HOOKS] = cols[HOOKS_COLUMN].text.replace("\n", "")
        hooksDict[SCRAPING_LATCHING] = cols[LATCHING_COLUMN].text.replace("\n", "")
        hooksDict[SCRAPING_RARITY] = (re.search("\d+", cols[RARITY_COLUMN].span.a['title'])).group()
        
        sourceDict = {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: ""
        }
        
        # Splitting string to prevent inconsistences
        stringsList = re.split(" or |\n", cols[SOURCE_COLUMN].text)
        for instance in stringsList:
            
            # Check to prevent breakline madness
            if instance:
                
                # If the source is a drop, it will be done together with its specified json (therefore there's no need to do it here)
                # The drop's ID will be put in the 'Drop' dict key later on.
                if (re.search("%", instance)):
                    continue
                
                # If the source is a crafting recipe, it's needed to put it in the recipes json and get its reference ID
                # The recipe's ID will be put in the 'Crafting Recipes' dict key later on
                if (re.search("^Crafted:", instance)):
                    continue
                    
                # If the source is an NPC, it's needed to get its respective ID.
                # This will be done later on.
                elif (re.search("\(", instance)):
                    continue
                    
                # If it's none of the above, we can just put it directly in the 'Other' dict key as open-text.
                elif re.search("Chests", instance):
                    sourceDict[SOURCE_OTHER] = "Found in " + instance.strip().replace("\n", "")

                else:
                    continue
            
        hooksDict[SCRAPING_SOURCE] = sourceDict
        hooksDictList.append(hooksDict)
SaveJSONFile(HOOK_PATH, sorted(hooksDictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
