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
import requests
from bs4 import BeautifulSoup

ARMOR_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + ARMOR_NAME_FILE + JSON_EXT
SET_PATH = GLOBAL_JSON_PATH + DIR_ID_REFERENCES + SET_NAME_FILE + JSON_EXT

REJECTED_ARMORS = {"Empty Bucket", "Boots of Ostara", "Ultrabright Helmet"}
REJECTED_SETS = {"Dragon armor", "Titan armor", "Spectral armor"}
WIKI_URL = "https://terraria.gamepedia.com/"

newURL = WIKI_URL + "Armor"
page = requests.get(newURL)
soup = BeautifulSoup(page.content, 'html.parser')
tables = soup.find_all("table", class_=TERRARIA_TABLE_CLASS)

armorList = []
itemSets = LoadJSONFile(SET_PATH)

#first and second tables
for table in tables[0:2]:
    trTags = table.find_all("tr")

    for trTag in trTags[2:]:
        if trTag.find_all("td")[1].a.text in REJECTED_SETS:
            continue
        newURL = WIKI_URL + trTag.find_all("td")[1].a.text.replace(" ", "_")
        print("processing {}".format(newURL))
        page2 = requests.get(newURL)
        soup2 = BeautifulSoup(page2.content, 'html.parser')
        tableBoxes = soup2.find_all("div", class_="infobox item")
        processedItems = []

        for tableBox in tableBoxes:
            if re.search("armor|set", tableBox.find("div", class_="title").text, re.IGNORECASE):
                continue
            if tableBox.find("div", class_="title").text in processedItems:
                continue

            status = {
                SCRAPING_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_SET_ID: ""
            }
            status[SCRAPING_ID] = tableBox.find("div", class_="section ids").find("li").b.text
            status[SCRAPING_NAME] = tableBox.find("div", class_="title").text

            for set in itemSets:
                if tableBox.find("div", class_="title").text in set[SCRAPING_SET_PIECES]:
                    status[SCRAPING_SET_ID] = str(set[SCRAPING_ID])
                    break

            armorDict = get_statistics(tableBox, itemInstance=status, isArmor=True)
            processedItems.append(armorDict[SCRAPING_NAME])
            armorList.append(armorDict)

#third and fourth tables
for table in tables[2:-1]:
    trTags = table.find_all("tr")
    processedItems = []

    for trTag in trTags[1:]:
        newURL = WIKI_URL + trTag.find_all("td")[1].a.text.replace(" ", "_")
        print("processing {}".format(newURL))
        page2 = requests.get(newURL)
        soup2 = BeautifulSoup(page2.content, 'html.parser')
        tableBox = soup2.find("div", class_="infobox item")

        if tableBox.find("div", class_="title").text in processedItems:
            continue
        
        armorDict = get_statistics(tableBox, isArmor=True)
        processedItems.append(armorDict[SCRAPING_NAME])
        armorList.append(armorDict)

#last table
trTags = tables[-1].find_all("tr")
processedItems = []
for trTag in trTags[1:]:
    if trTag.find_all("td")[1].a.text in REJECTED_ARMORS:
        continue
    
    newURL = WIKI_URL + trTag.find_all("td")[1].a.text.replace(" ", "_")
    print("processing {}".format(newURL))
    page2 = requests.get(newURL)
    soup2 = BeautifulSoup(page2.content, 'html.parser')
    tableBox = soup2.find("div", class_="infobox item")

    if tableBox.find("div", class_="title").text in processedItems:
        continue
    
    armorDict = get_statistics(tableBox, isArmor=True)
    processedItems.append(armorDict[SCRAPING_NAME])
    armorList.append(armorDict)

for armor in armorList:
    for set in itemSets:
        if armor[SCRAPING_NAME] in set[SCRAPING_SET_PIECES]:
            armor[SCRAPING_SET_ID] = str(set[SCRAPING_ID])
            break

SaveJSONFile(ARMOR_PATH, sortListOfDictsByKey(armorList, SCRAPING_ITEM_ID))
