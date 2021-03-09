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

GET_PAINTING_ICONS = 0

TABLE_HEAD_LABELS = ["Painting", "Name", "Placed", "Tooltip", "Description"]
PAINTINGS_ICONS_DIRECTORY = "paintings_icons/"
PAINTING_JSON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + PAINTING_NAME_FILE + JSON_EXT
dictList = []

URL = "https://terraria.gamepedia.com/Paintings"
html = requests.get(URL)
soup = BeautifulSoup(html.content, 'html.parser')
tables = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)
for table in tables:
    rows = table.findAll("tr")
    index = getTableColumns(rows[0].findAll("th"), TABLE_HEAD_LABELS)
    for row in rows[1::]:
        cols = row.findAll("td")
        paintingDict = {
            SCRAPING_ITEM_ID: "",
            IMAGE_PLACED: "",
            SCRAPING_TOOLTIP: "",
            SCRAPING_DESCRIPTION: "",
            SCRAPING_SOURCE: SOURCE_SOURCES_DICT
        }
        if index["Name"] != NOT_FOUND:
            paintingDict[SCRAPING_ITEM_ID] = re.search("\d+", cols[index["Name"]].find("div", class_="id").text).group()
            print("Getting information from ID " + paintingDict[SCRAPING_ITEM_ID])
            
        if GET_PAINTING_ICONS:
            if index["Painting"] != NOT_FOUND:
                imagePath = DIR_ITEMS_DATA + PAINTINGS_ICONS_DIRECTORY + cols[index["Painting"]].img['alt'].replace(" ", "_") + STATIC_IMAGE_EXT
                writeImage(cols[index["Painting"]].img['src'], GLOBAL_JSON_PATH + imagePath)
            
        if index["Placed"] != NOT_FOUND:
            imagePath = IMAGE_DIR_PAINTINGS + cols[index["Painting"]].img['alt'].replace(" ", "_") + "_Placed" + STATIC_IMAGE_EXT
            writeImage(cols[index["Placed"]].img['src'], GLOBAL_JSON_PATH + imagePath)
            paintingDict[IMAGE_PLACED] = imagePath
            
        if index["Tooltip"] != NOT_FOUND:
            paintingDict[SCRAPING_TOOLTIP] = cols[index["Tooltip"]].text.replace("\n", "")
            
        if index["Description"] != NOT_FOUND:
            paintingDict[SCRAPING_DESCRIPTION] = cols[index["Description"]].text.replace("\n", "").replace("\"", "")
           
        removeEmptyFields(paintingDict)
        dictList.append(paintingDict)
SaveJSONFile(PAINTING_JSON_PATH, sorted(dictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
