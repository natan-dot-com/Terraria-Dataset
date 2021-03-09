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

DYNAMIC_IMAGE_ITEMS = ["Crimson Heart", "Wisp", "Suspicious Looking Eye", "Flickerwick", "Jack 'O Lantern", "Toy Golem", "Fairy Princess"]
LIGHT_PET_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + LIGHT_PET_NAME_FILE + JSON_EXT
dictList = []

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

URL = "https://terraria.gamepedia.com/Pets#Light_Pets"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
tables = []
tables.append(soup.find("table", { "id" : "table-Light-Pets"}))
tables.append(soup.find("table", { "id" : "table-Master-Mode-Light-Pets"}))
if tables:
    for table in tables:
        rows = table.findAll("tr")
        for row in rows[1::]:
            cols = row.findAll("td")
            petDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_LIGHT_PET: "",
                SCRAPING_BRIGHTNESS: "",
                SCRAPING_NOTES: "",
                SCRAPING_MASTER_MODE: "",
                SCRAPING_BUFF_IMAGE: "",
                SCRAPING_PET_IMAGE: [],
                SCRAPING_SOURCE: SOURCE_SOURCES_DICT
            }
            petDict[SCRAPING_ITEM_ID] = searchForID(cols[2].text.replace("\n", ""), itemList)
            print("Getting information from ID " + petDict[SCRAPING_ITEM_ID])

            petDict[SCRAPING_LIGHT_PET] = cols[1].text.replace("\n", "")
            petDict[SCRAPING_BRIGHTNESS] = cols[3].text.replace("\n", "")
            if len(cols) == 6:
                petDict[SCRAPING_NOTES] = cols[5].text.replace("\n", "")

            imagePath = DIR_ITEMS_DATA + IMAGE_DIR_LIGHT_PETS + cols[2].text.replace("\n", "").replace(" ", "_") + "_Buff" + STATIC_IMAGE_EXT
            writeImage(cols[0].find("img")['src'], GLOBAL_JSON_PATH + imagePath)
            petDict[SCRAPING_BUFF_IMAGE] = imagePath

            if cols[1].text.replace("\n", "") == "Fairy":
                imageCounter = 1
                for petImage in cols[1].findAll("img"):
                    imagePath = DIR_ITEMS_DATA + IMAGE_DIR_LIGHT_PETS + cols[1].text.replace("\n", "").replace(" ", "_")
                    imagePath += "_" + str(imageCounter)
                    if petDict[SCRAPING_LIGHT_PET] in DYNAMIC_IMAGE_ITEMS:
                        imagePath += DYNAMIC_IMAGE_EXT
                    else:
                        imagePath += STATIC_IMAGE_EXT
                    writeImage(petImage['src'], GLOBAL_JSON_PATH + imagePath)
                    petDict[SCRAPING_PET_IMAGE].append(imagePath)
                    imageCounter += 1
            else:
                imagePath = DIR_ITEMS_DATA + IMAGE_DIR_LIGHT_PETS + cols[1].text.replace("\n", "").replace(" ", "_")
                if petDict[SCRAPING_LIGHT_PET] not in DYNAMIC_IMAGE_ITEMS:
                    imagePath += STATIC_IMAGE_EXT
                else:
                    imagePath += DYNAMIC_IMAGE_EXT
                writeImage(cols[1].find("img")['src'], GLOBAL_JSON_PATH + imagePath)
                petDict[SCRAPING_PET_IMAGE].append(imagePath)

            if tables.index(table) == 0:
                petDict[SCRAPING_MASTER_MODE] = "No"
            else:
                petDict[SCRAPING_MASTER_MODE] = "Yes"

            petDict = removeEmptyFields(petDict)
            dictList.append(petDict)

SaveJSONFile(LIGHT_PET_PATH, sorted(dictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
