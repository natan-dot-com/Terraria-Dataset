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
from ...package.item_hash import *
from ...package.log_manager import *
from bs4 import BeautifulSoup
import re
import requests

# Constant values
BAGS_FILE_PATH = GLOBAL_JSON_PATH + DIR_ID_REFERENCES + BAGS_NAME_FILE + JSON_EXT
BAGS_DROP_PATH = GLOBAL_JSON_PATH + DIR_ID_REFERENCES + BAGS_DROP_NAME_FILE + JSON_EXT

MAIN_URL = "https://terraria.gamepedia.com"
MAIN_SUFFIX = "/Grab_bags"
CRATES_SUFFIX = "/Crates"

# Table Head Labels
CRATE_TABLE_HEAD_LABELS = ["Pre-Hardmode type", "Hardmode type"]
DROP_TABLE_HEAD_LABELS = ["Item", "Quantity", "Chance"]
BAG_DROP_TABLE_HEAD_LABELS = ["Item", "Chance", "Amount"]

# Initializes both item hash table and bag hash table
def initializeHashTables(itemList: list, bagList: list):
    itemHash = hashTable(ITEMS_HASH_SIZE, SCRAPING_NAME)
    for itemInstance in itemList:
        itemHash.add(itemInstance[SCRAPING_NAME], itemInstance)

    bagHash = hashTable(TABLES_HASH_SIZE, SCRAPING_NAME)
    for bagInstance in bagList:
        bagHash.add(bagInstance[SCRAPING_NAME], bagInstance)

    return itemHash, bagHash

# Gets every crate URL suffix from the crates table (in '/Crates'). Used inside the next function scope
def getCratesSuffixes(suffixesList: list):
    html = requests.get(MAIN_URL + CRATES_SUFFIX)
    soup = BeautifulSoup(html.content, 'html.parser')
    rows = soup.find("table", class_=TERRARIA_TABLE_CLASS).findAll("tr")
    tableHead = getTableColumns(rows[0].findAll("th"), CRATE_TABLE_HEAD_LABELS)
    for row in rows[1::]:
        for columnLabel in CRATE_TABLE_HEAD_LABELS:
            cols = row.findAll("td")
            crateSuffix = cols[tableHead[columnLabel]].a['href']
            if crateSuffix:
                suffixesList.append(crateSuffix)

# Gets every URL suffix from the grab bag table (in '/Grab_bags')
def getURLSuffixes():
    suffixesList = []
    html = requests.get(MAIN_URL + MAIN_SUFFIX)
    soup = BeautifulSoup(html.content, 'html.parser')
    rows = soup.find("table", class_=TERRARIA_TABLE_CLASS).findAll("tr")
    for row in rows[1::]:
        firstCol = row.find("td", class_="il2c")
        if firstCol:
            suffix = firstCol.a['href']
            if suffix == CRATES_SUFFIX:
                getCratesSuffixes(suffixesList)
            else:
                suffixesList.append(suffix)
    return suffixesList

# Finds the bag ID using the bag hash table
def findBagID(bagName: str, bagHash: hashTable, logFile):
    hashResult = bagHash.search(bagName, BAG_ID)
    if hashResult == NOT_FOUND:
        logFile.write("FATAL ERROR: Bag not found in the database.\n")
        logFile.write("\tACTION: Aborted process. \n\n")
    else:
        print("Bag ID for '" + bagName + "' found.")
    return hashResult

# Write algorithm uses a specific structure to avoid rewriting the file every time a number is written
def feedWriteStructure(dropDict, writeStructure, itemList):
    itemIndex = int(dropDict[BAG_DROP_RESULT])-1
    itemType = itemList[itemIndex][SCRAPING_TYPE]
    if itemType not in writeStructure.keys():
        writeStructure[itemType] = {}
    if itemIndex+1 not in writeStructure[itemType].keys():
        writeStructure[itemType][itemIndex+1] = []
    writeStructure[itemType][itemIndex+1].append(dropDict[BAG_DROP_ID])

# Writes every bag drop ID on every respective source list inside each items-prefixed json file
def writeOnJSONFiles(writeStructure, logFile):
    for itemType in writeStructure.keys():
        filename = MAIN_ITEM_SUBFILE_PREFIX + itemType.lower().replace(" ", "_") + JSON_EXT
        filePath = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + filename
        typeList = LoadJSONFile(filePath)

        if not typeList:
            logFile.write("WRITING ERROR: Can't reach file " + filePath + ". No such file or directory.\n")
            logFile.write("\tACTION: Writing process for type " + itemType + " aborted.\n\n")
            continue

        for itemID in writeStructure[itemType].keys():
            for itemInstance in typeList:
                if int(itemID) == int(itemInstance[SCRAPING_ITEM_ID]):
                    for bagDropID in writeStructure[itemType][itemID]:
                        if bagDropID not in itemInstance[SCRAPING_SOURCE][SOURCE_GRAB_BAG]:
                            itemInstance[SCRAPING_SOURCE][SOURCE_GRAB_BAG].append(bagDropID)
                        else:
                            print("Bag Drop with ID " + str(bagDropID) + " is already on file. Aborting writing proccess.")
                    break
            SaveJSONFile(filePath, typeList)

# Writes every bag drop ID on every respective loot list in grab_bags_drops.json
def writeOnBagFile(writeStructure, bagID: str):
    bagList = LoadJSONFile(BAGS_FILE_PATH)
    for itemType in writeStructure.keys():
        for itemID in writeStructure[itemType].keys():
            for bagDropID in writeStructure[itemType][itemID]:
                if str(bagDropID) not in bagList[int(bagID)-1][GRAB_BAGS_LOOT_LIST]:
                    bagList[int(bagID)-1][GRAB_BAGS_LOOT_LIST].append(str(bagDropID))
    bagList[int(bagID)-1][GRAB_BAGS_LOOT_LIST].sort(key=int)
    SaveJSONFile(BAGS_FILE_PATH, bagList)

# Scraps general information for every grab bag (Treasure bags are exceptions)
def scrapDropInformation(itemHash: hashTable, urlSuffix: str, logFile, IDcounter: int, bagID: str, dropList, itemList):
    writeStructure = {}

    html = requests.get(MAIN_URL + urlSuffix)
    soup = BeautifulSoup(html.content, 'html.parser')
    table = soup.find("table", class_=TERRARIA_TABLE_CLASS)
    if table:
        rows = table.findAll("tr")
        dropTableHead = getTableColumns(rows[0].findAll("th"), DROP_TABLE_HEAD_LABELS)
        quantityValue = 0
        dropChance = 0
        for row in rows[1::]:
            dropDict = {
                BAG_DROP_ID: "",
                BAG_DROP_RESULT: "",
                BAG_DROP_QUANTITY: "",
                BAG_DROP_PROBABILITY: "",
                BAG_ID: ""
            }
            cols = row.findAll("td")

            dropDict[BAG_DROP_ID] = str(IDcounter)

            itemDropID = str(itemHash.search(cols[dropTableHead["Item"]].a['title'], SCRAPING_ID))
            if itemDropID != str(NOT_FOUND):
                print("Scraping information for ID " + itemDropID + ".")
            else:
                print("ERROR: Check log file for more information.")
                logFile.write("ERROR: ID for item '" + cols[dropTableHead["Item"]].a['title'] + "' not found in the database.\n")
                logFile.write("\tACTION: Item ID replaced with -1 (NOT_FOUND).\n\n")

            # I have no fucking idea, it works
            if len(cols) > 1:
                if not cols[dropTableHead["Item"]+1].find("span", class_="chance"):
                    if not re.search("%", cols[dropTableHead["Item"]+1].text):
                        quantityValue = cols[dropTableHead["Quantity"]].text.strip().replace("\u2013", "-")
                        if len(cols) > 2:
                            if cols[dropTableHead["Chance"]].find("span", class_="chance"):
                                if cols[dropTableHead["Chance"]].find("s"):
                                    dropChance = cols[dropTableHead["Chance"]].s.text.strip()
                                else:
                                    dropChance = cols[dropTableHead["Chance"]].find("span", class_="chance").contents[0]
                            else:
                                dropChance = cols[dropTableHead["Chance"]].text.strip()
                    else:
                        dropChance = cols[dropTableHead["Chance"]-1].text.strip()
                else:
                    dropChance = cols[dropTableHead["Chance"]-1].s.text.strip()

            dropDict[BAG_DROP_RESULT] = itemDropID
            dropDict[BAG_DROP_QUANTITY] = quantityValue
            dropDict[BAG_DROP_PROBABILITY] = dropChance[:-1:] + "%"
            dropDict[BAG_ID] = bagID

            feedWriteStructure(dropDict, writeStructure, itemList)
            dropList.append(dropDict)
            IDcounter += 1

        writeOnJSONFiles(writeStructure, logFile)
        writeOnBagFile(writeStructure, bagID)

def treasureBagDropScrap(dropList, urlSuffix, bagHash, itemHash, logFile, itemList, IDcounter):
    funcIDcounter = 0

    html = requests.get(MAIN_URL + urlSuffix)
    soup = BeautifulSoup(html.content, 'html.parser')
    bagTables = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)[0:20]

    for table in bagTables:
        writeStructure = {}
        bagName = "Treasure Bag (" + table['id'].replace("_", " ") + ")"
        bagID = findBagID(bagName, bagHash, logFile)

        if bagID != NOT_FOUND:
            rows = []

            if table.find("table"):
                subtables = table.findAll("table")
                for s_table in subtables:
                    rows.extend(s_table.findAll("tr"))
                dropTableHead = getTableColumns(rows[0].findAll("th"), BAG_DROP_TABLE_HEAD_LABELS)
            else:
                rows = table.findAll("tr")
                dropTableHead = getTableColumns(rows[1].findAll("th"), BAG_DROP_TABLE_HEAD_LABELS)

            if rows[1].find("th", class_="unobtainablehighlight"):
                continue

            for row in rows:
                if row.find("th"):
                    continue
                cols = row.findAll("td")
                dropDict = {
                    BAG_DROP_ID: "",
                    BAG_DROP_RESULT: "",
                    BAG_DROP_QUANTITY: "",
                    BAG_DROP_PROBABILITY: "",
                    BAG_ID: ""
                }
                dropDict[BAG_DROP_ID] = str(IDcounter + funcIDcounter)

                itemDrop = cols[dropTableHead["Item"]].find("img")
                itemDropID = itemHash.search(itemDrop['alt'], SCRAPING_ID)
                if itemDropID != NOT_FOUND:
                    print("Scraping information for ID " + itemDropID + ".")
                    dropDict[BAG_DROP_RESULT] = str(itemDropID)
                else:
                    print("ERROR: Check log file for more information.")
                    logFile.write("ERROR: ID for item '" + drop['alt'] + "' not found in the database.\n")
                    logFile.write("\tACTION: Item ID replaced with -1 (NOT_FOUND).\n\n")

                dropDict[BAG_DROP_QUANTITY] = cols[dropTableHead["Amount"]].text.strip()
                dropDict[BAG_DROP_PROBABILITY] = cols[dropTableHead["Chance"]].contents[0].strip()
                dropDict[BAG_ID] = str(bagID)

                feedWriteStructure(dropDict, writeStructure, itemList)
                dropList.append(dropDict)
                funcIDcounter += 1

            writeOnJSONFiles(writeStructure, logFile)
            writeOnBagFile(writeStructure, bagID)

def main():
    itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
    bagList = LoadJSONFile (BAGS_FILE_PATH)
    itemHash, bagHash = initializeHashTables(itemList, bagList)
    IDcounter = 1
    dropList = []

    suffixesList = getURLSuffixes()
    for urlSuffix in suffixesList:
        # Initial setup
        logFilename = "bag_" + urlSuffix[1::].replace(" ", "_").lower()
        logFile = createLogFile(logFilename)

        bagName = urlSuffix[1::].replace("_", " ")
        bagID = findBagID(bagName, bagHash, logFile)

        # Initialization messages
        if bagID != NOT_FOUND:
            logFile.write("Bag ID found (" + str(bagID) + ").\n")
        print("Starting getting information from '" + MAIN_URL + urlSuffix + "'...")

        # Scrap block
        if urlSuffix == "/Treasure_Bag":
            treasureBagDropScrap(dropList, urlSuffix, bagHash, itemHash, logFile, itemList, IDcounter)
        elif bagID != NOT_FOUND:
            scrapDropInformation(itemHash, urlSuffix, logFile, IDcounter, bagID, dropList, itemList)
        IDcounter = len(dropList)+1

        # Exit block
        closeLogFile(logFile)
        print("\n")

    SaveJSONFile(BAGS_DROP_PATH, dropList)
    print("Exiting returning value 0.")

if __name__ == "__main__":
    main()
