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

MAIN_URL = "https://terraria.gamepedia.com"
EXCEPTION_SUFFIX = "/Eternia_Crystal"
MAIN_URL_SUFFIX = "/Consumables#Summoning_items"
INFOBOX_LABELS = ["Tooltip", "Rarity"]
TABLE_HEAD_LABELS = ["Item", "Event", "Notes"]
EVENT_SUMMON_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + EVENT_SUMMON_NAME_FILE + JSON_EXT
dictList = []

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)

html = requests.get(MAIN_URL + MAIN_URL_SUFFIX)
soup = BeautifulSoup(html.content, 'html.parser')
tables = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)
for table in tables:
    if table.caption:
        if table.caption.text == "Event-summoning items\n":
            rightTable = table
            break
rows = rightTable.findAll("tr")
index = getTableColumns(table.findAll("th"), TABLE_HEAD_LABELS)
for row in rows[1::]:
    cols = row.findAll("td")
    eventDict = {
        SCRAPING_ITEM_ID: "",
        SCRAPING_RARITY: "",
        SCRAPING_EVENT: "",
        SCRAPING_TOOLTIP: "",
        SCRAPING_NOTES: "",
        SCRAPING_SOURCE: SOURCE_SOURCES_DICT
    }

    eventDict[SCRAPING_ITEM_ID] = searchForID(cols[index["Item"]].img['alt'], itemList)
    print("Getting information from '" + cols[index["Item"]].img['alt'] + "' with ID " + eventDict[SCRAPING_ITEM_ID])

    itemURLprefix = row.find("td", class_="il2c").a['href']
    itemHtml = requests.get(MAIN_URL + itemURLprefix)
    itemSoup = BeautifulSoup(itemHtml.content, 'html.parser')
    itemTable = itemSoup.find("table", class_="stat")
    itemIndex = getTableColumns(itemTable.findAll("th"), INFOBOX_LABELS)
    itemRows = itemTable.findAll("td")

    eventDict[SCRAPING_RARITY] = re.search("\d+", itemRows[itemIndex["Rarity"]].img['alt']).group()

    eventTooltip = itemRows[itemIndex["Tooltip"]].text.split("\'")
    string = ""
    for tooltip in eventTooltip:
        if len(eventTooltip) > 1:
            if tooltip != "":
                string += tooltip + ". "
                eventDict[SCRAPING_TOOLTIP] = string[:-2]
        else:
            eventDict[SCRAPING_TOOLTIP] = tooltip + "."
    
    eventDict[SCRAPING_EVENT] = cols[index["Event"]+1].a['title']
    eventDict[SCRAPING_NOTES] = cols[index["Notes"]+1].text.replace("\n", "")
    dictList.append(eventDict)

# Eternia Crystal threatment
html = requests.get(MAIN_URL + EXCEPTION_SUFFIX)
soup = BeautifulSoup(html.content, 'html.parser')
table = soup.find("table", class_="stat")
rows = table.findAll("td")
index = getTableColumns(table.findAll("th"), INFOBOX_LABELS)
eventDict = {
    SCRAPING_ITEM_ID: "",
    SCRAPING_RARITY: "",
    SCRAPING_EVENT: "",
    SCRAPING_TOOLTIP: "",
    SCRAPING_NOTES: "",
    SCRAPING_SOURCE: SOURCE_SOURCES_DICT
}
eventDict[SCRAPING_ITEM_ID] = searchForID("Eternia Crystal", itemList)
print("Getting information from 'Eternia Crystal' with ID " + eventDict[SCRAPING_ITEM_ID])

eventDict[SCRAPING_RARITY] = re.search("\d+", rows[index["Rarity"]].img['alt']).group()
eventDict[SCRAPING_EVENT] = "Old's One Army"
eventDict[SCRAPING_TOOLTIP] = re.sub(r'(Crystal)', r'\1.', rows[index["Tooltip"]].text) + "."
removeEmptyFields(eventDict)
dictList.append(eventDict)

SaveJSONFile(EVENT_SUMMON_PATH, sorted(dictList, key = lambda i: int(i[SCRAPING_ITEM_ID])))
