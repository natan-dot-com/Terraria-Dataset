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

FIND_FIRST_TABLE = -10
FIND_ALL_TABLES = -11

MAIN_URL = "https://terraria.gamepedia.com"
MAIN_URL_SUFFIX = "/Grab_bags"
CRATES_URL_SUFFIX = "/Crates"
TREASURE_BAG_URL_SUFFIX = "/Treasure_Bag"

GRAB_BAG_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + GRAB_BAG_FILE + JSON_EXT

# Constant value lists
CRATES_TABLE_HEAD_LABELS = [
    "Pre-Hardmode type", "Hardmode type", "Sell", 
    "Rarity", "Biome", "Catch quality"
]
GENERIC_SCRAPPING_DATA = [
    "Rarity", "Sell"
]

def getTableContent(urlSuffix: str, tableClass: str, Mode: int):
    html = requests.get(MAIN_URL + urlSuffix)
    soup = BeautifulSoup(html.content, 'html.parser')
    if Mode == FIND_FIRST_TABLE:
        table = soup.find("table", class_=tableClass)
    elif Mode == FIND_ALL_TABLES:
        table = soup.findAll("table", class_=tableClass)
    return table

def cratesScrap(cratesTable: list, dictList: list):
    tableRows = cratesTable.findAll("tr")
    tableHead = getTableColumns(tableRows[0].findAll("th"), CRATES_TABLE_HEAD_LABELS)
    cratesList = ["Pre-Hardmode type", "Hardmode type"]
    for row in tableRows[1::]:
        tableCols = row.findAll("td")
        for idColumn in cratesList:
            bagDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_RARITY: "",
                SCRAPING_SELL: "",
                SCRAPING_CATCH_QUALITY: "",
                SCRAPING_BAG_DROPS: [],
                SCRAPING_SOURCE: {
                    SOURCE_RECIPES: [],
                    SOURCE_NPC: [],
                    SOURCE_DROP: [],
                    SOURCE_GRAB_BAG: [],
                    SOURCE_OTHER: ""
                }
            }
            
            divText = tableCols[tableHead[idColumn]].find("div", class_="id").text
            bagDict[SCRAPING_ITEM_ID] = re.search("\d+", divText).group()
            print("Started getting information from " + bagDict[SCRAPING_ITEM_ID])

            rarityTitle = tableCols[tableHead["Rarity"]].a['title']
            bagDict[SCRAPING_RARITY] = re.search("\d+", rarityTitle).group()

            bagDict[SCRAPING_SELL] = tableCols[tableHead["Sell"]].span['title']
            bagDict[SCRAPING_CATCH_QUALITY] = tableCols[tableHead["Catch quality"]].text.strip().replace(" [2]", "")

            # Crate source
            middleString = tableCols[tableHead["Biome"]].a
            if middleString:
                sourceString = "Fishing in " + middleString['title']
            else:
                sourceString = "Fishing in any biome"
            bagDict[SCRAPING_SOURCE][SOURCE_OTHER] = sourceString

            dictList.append(bagDict)

def treasureBagScrap(treasureBagTables: list, dictList: list):
    rarityTable = treasureBagTables[-2].findAll("td")
    for table in treasureBagTables:
        tableCaption = table.find("tr")
        treasureDict = {
            SCRAPING_ITEM_ID: "",
            SCRAPING_RARITY: "",
            SCRAPING_BAG_DROPS: [],
            SCRAPING_SOURCE: {
                SOURCE_RECIPES: [],
                SOURCE_NPC: [],
                SOURCE_DROP: [],
                SOURCE_GRAB_BAG: [],
                SOURCE_OTHER: ""
            }
        }
        bagID = tableCaption.find("div", class_="id")
        if bagID:
            treasureDict[SCRAPING_ITEM_ID] = re.search("\d+", bagID.text).group()
            print("Started getting information from " + treasureDict[SCRAPING_ITEM_ID])
        else:
            return

        bagName = tableCaption.img['alt']
        for bag in rarityTable:
            if bagName == bag.img['alt'][:-4:]:
                treasureDict[SCRAPING_RARITY] = re.search("\d+", bag.find("span", class_="rarity").text).group().lstrip("0")
        dictList.append(treasureDict)
        
def getGrabBagLinks():
    linksList = []
    exceptions = [CRATES_URL_SUFFIX, TREASURE_BAG_URL_SUFFIX]
    html = requests.get(MAIN_URL + MAIN_URL_SUFFIX)
    soup = BeautifulSoup(html.content, 'html.parser')
    rows = soup.find("table", class_=TERRARIA_TABLE_CLASS).findAll("tr")
    for row in rows[1::]:
        linkCol = row.find("td", class_="il2c")
        if linkCol:
            if linkCol.a['href'] not in exceptions:
                linksList.append(linkCol.a['href'])
    return linksList

def genericScrap(urlSuffix, tableClass, dictList):
    infobox = getTableContent(urlSuffix, tableClass, FIND_FIRST_TABLE)
    tableHead = getTableColumns(infobox.findAll("th"), GENERIC_SCRAPPING_DATA)
    rows = infobox.findAll("tr")
    genericDict = {
        SCRAPING_ITEM_ID: "",
        SCRAPING_RARITY: "",
        SCRAPING_SELL: "",
        SCRAPING_BAG_DROPS: [],
        SCRAPING_SOURCE: {
            SOURCE_RECIPES: [],
            SOURCE_NPC: [],
            SOURCE_DROP: [],
            SOURCE_GRAB_BAG: [],
            SOURCE_OTHER: ""
        }
    }
    divID = infobox.parent.parent.find("div", class_="section ids").text
    genericDict[SCRAPING_ITEM_ID] = re.search("\d+", divID).group()
    print("Started getting information from " + genericDict[SCRAPING_ITEM_ID])

    rarityNumber = rows[tableHead["Rarity"]].td.a['title']
    genericDict[SCRAPING_RARITY] = re.search("\d+", rarityNumber).group()

    if tableHead["Sell"] != -1:
        genericDict[SCRAPING_SELL] = rows[tableHead["Sell"]].td.span['title']
    
    removeEmptyFields(genericDict)
    dictList.append(genericDict)


def main():
    dictList = []
    
    print("Starting crates scrap...")
    # Crates scrap
    cratesTable = getTableContent(CRATES_URL_SUFFIX, SORTABLE_TABLE_CLASS, FIND_FIRST_TABLE)
    cratesScrap(cratesTable, dictList)

    print("Starting treasure bags scrap...")
    # Treasure Bags scrap
    treasureBagsTables = getTableContent(TREASURE_BAG_URL_SUFFIX, TERRARIA_TABLE_CLASS, FIND_ALL_TABLES)
    treasureBagScrap(treasureBagsTables, dictList)

    print("Starting generic bags scrap...")
    # Another bags scrap
    linkList = getGrabBagLinks()
    for linkSuffix in linkList:
        genericScrap(linkSuffix, STAT_TABLE_CLASS, dictList)

    SaveJSONFile(GRAB_BAG_PATH, sorted(dictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))

if __name__ == "__main__":
    main()
