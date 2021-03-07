# Still wip: Need to get the items that each npc sells

#Load 3-level parent directories
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
import bs4
import requests

SELL_LIST_PATH = GLOBAL_JSON_PATH + DIR_ID_REFERENCES + SELLING_LIST_NAME_FILE + JSON_EXT
TOWN_NPC_PATH = GLOBAL_JSON_PATH + DIR_NPC_DATA + NPC_TOWN_NAME_FILE + JSON_EXT
MAIN_URL = "https://terraria.gamepedia.com"
TOWN_NPC_SUFFIX = "/NPCs"
tableHeadLabels = ["NPC", "Description", "Spawn requirement"]
tableHeadLabels2 = ["Item", "Cost", "Availability"]

def initializeHashTables(itemList):
    npcList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_NPC_DATA + NPC_NAME_FILE + JSON_EXT)
    npcHash = hashTable(NPC_HASH_SIZE, SCRAPING_NAME)
    for npcInstance in npcList:
        npcHash.add(npcInstance[SCRAPING_NAME], npcInstance)

    itemHash = hashTable(ITEMS_HASH_SIZE, SCRAPING_NAME)
    for itemInstance in itemList:
        itemHash.add(itemInstance[SCRAPING_NAME], itemInstance)

    return npcHash, itemHash

# Gets every basic information about each town NPC
def scrapGeneralInformation(townList, npcHash):
    html = requests.get(MAIN_URL + TOWN_NPC_SUFFIX)
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    tableList = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)
    for table in tableList[:4:]:
        if tableList.index(table) == 2:
            continue

        rowList = table.findAll("tr")
        tableHead = getTableColumns(rowList[0].findAll("th"), tableHeadLabels)
        for row in rowList[1::]:
            colList = row.findAll("td")
            townDict = {
                NPC_ID: "",
                SCRAPING_DESCRIPTION: "",
                SCRAPING_SPAWN_REQUIREMENT: "",
                NPC_SELL_LIST: []
            }
            npcName = colList[tableHead["NPC"]].img['alt']
            print("Getting information from '" + npcName + "'.")
            townDict[NPC_ID] = str(npcHash.search(npcName, NPC_ID))
            townDict[SCRAPING_DESCRIPTION] = colList[tableHead["Description"]+1].text.strip()

            spawnReqString = colList[tableHead["Spawn requirement"]+1].text.replace("\u2009", "").replace("\u00a0","").replace("\u2013","-")
            townDict[SCRAPING_SPAWN_REQUIREMENT] = spawnReqString.strip().replace("  ", " ")
            townList.append(townDict)

def feedWriteStructure(itemList, sellDict, writeStructure):
    itemIndex = int(sellDict[NPC_SELL_ITEM])-1
    itemType = itemList[itemIndex][SCRAPING_TYPE]
    if itemType not in writeStructure:
        writeStructure[itemType] = {}
    if itemIndex+1 not in writeStructure[itemType]:
        writeStructure[itemType][itemIndex+1]  = []
    writeStructure[itemType][itemIndex+1].append(sellDict[NPC_SELL_ID])

# Refering every selling structure into the respective's item SOURCE_NPC list
def writeOnJSONFiles(writeStructure):
    print("Initiating writing proccess...")
    for itemType in writeStructure.keys():
        filename = DIR_ITEMS_DATA  + MAIN_ITEM_SUBFILE_PREFIX + itemType.lower().replace(" ", "_") + JSON_EXT
        filePath = GLOBAL_JSON_PATH + filename
        typeList = LoadJSONFile(filePath)

        if not typeList:
            print("WRITING ERROR: Can't reach file " + filePath + ". No such file or directory.")
            print("\tACTION: Writing process for type " + itemType + " aborted.")
            continue

        for itemID in writeStructure[itemType].keys():
            for itemInstance in typeList:
                if int(itemID) == int(itemInstance[SCRAPING_ITEM_ID]):
                    for sellID in writeStructure[itemType][itemID]:
                        if sellID not in itemInstance[SCRAPING_SOURCE][SOURCE_NPC]:
                            itemInstance[SCRAPING_SOURCE][SOURCE_NPC].append(sellID)
                        else:
                            print("Selling structure with ID " + str(sellID) + " is already on file. Aborting writing proccess.")
                    break
            SaveJSONFile(filePath, typeList)

def getSellingList(urlSuffix, townList, npcHash, itemHash, IDcounter, sellingList, itemList):
    writeStructure = {}

    html = requests.get(MAIN_URL + urlSuffix)
    soup = bs4.BeautifulSoup(html.content, 'html.parser')
    table = soup.find("table", class_=TERRARIA_TABLE_CLASS)

    # Checking if there's a selling table in the page
    if table.find("caption"):
        if table.caption.text.strip() == "Inventory":
            print("Selling table detected in '" + urlSuffix + "'.")
            rows = table.findAll("tr")
            tableHead = getTableColumns(rows[0].findAll("th"), tableHeadLabels2)
            npcName = urlSuffix[1::].replace("_", " ")

            for row in rows[1::]:
                cols = row.findAll("td")
                sellDict = {
                    NPC_SELL_ID: "",
                    NPC_ID: "",
                    NPC_SELL_ITEM: "",
                    NPC_ITEM_COST: "",
                    NPC_SELL_CONDITION: ""
                }
                sellDict[NPC_SELL_ID] = str(IDcounter)
                sellDict[NPC_ID] = str(npcHash.search(npcName, NPC_ID))

                # Checking if the selling row is PC-excluded
                imageList = cols[tableHead["Item"]].findAll("img")
                pcExcluded = True
                if len(imageList) > 1:
                    for imageInstance in imageList[1::]:
                        if re.search("Desktop", imageInstance['alt'], re.IGNORECASE):
                            pcExcluded = False
                            break
                else:
                    pcExcluded = False

                # If it's PC-excluded, we can skip it
                if pcExcluded:
                    print("\tItem selling data for '" + imageList[0]['alt'] + "' is PC-excluded. Skipping it.")
                    continue

                # Getting which item it's being sold
                print("\tStarting getting information for '" + imageList[0]['alt'] + "' in " + urlSuffix + ".")
                itemID = str(itemHash.search(imageList[0]['alt'], SCRAPING_ID))
                if int(itemID) == NOT_FOUND:
                    if imageList[0]['alt'] in nameSubstitutes.keys():
                        itemName = nameSubstitutes[imageList[0]['alt']]
                        sellDict[NPC_SELL_ITEM] = str(itemHash.search(itemName, SCRAPING_ID))
                    else:
                        sellDict[NPC_SELL_ITEM] = str(NOT_FOUND)
                        print("\t\tItem '" + imageList[0]['alt'] + "' not found in database. Replaced with NOT_FOUND.")
                else:
                    sellDict[NPC_SELL_ITEM] = itemID

                sellDict[NPC_ITEM_COST] = cols[tableHead["Cost"]].span['title']

                # Really awkward string manipulation to done things right while getting Selling Condition
                conditionChilden = list(cols[tableHead["Availability"]].children)
                if cols[tableHead["Availability"]].find("br") in conditionChilden:
                    conditionChilden = conditionChilden[:conditionChilden.index(cols[tableHead["Availability"]].find("br")):]
                    filtredTag = ""
                    for tagInstance in conditionChilden:
                        if not isinstance(tagInstance, bs4.element.NavigableString):
                            filtredTag += tagInstance.text
                        else:
                            filtredTag += tagInstance
                    sellDict[NPC_SELL_CONDITION] = filtredTag.strip()
                else:
                    sellDict[NPC_SELL_CONDITION] = cols[tableHead["Availability"]].text.strip().replace("\u2013", "-")\
                    .replace("\u00a0", "").replace("()", "").replace(" .", "").strip(".") + " "
                    if sellDict[NPC_ID] != "425":
                        conditionImages = cols[tableHead["Availability"]].findAll("img")
                        moonPhase = False
                        for imageInstance in conditionImages:
                            if re.search("Moon", imageInstance['alt'], re.IGNORECASE):
                                moonPhase = True
                                sellDict[NPC_SELL_CONDITION] += re.search("\(([^)]+)\)", imageInstance['alt']).group()[1:-1:] + ", "
                        if moonPhase:
                            sellDict[NPC_SELL_CONDITION] = sellDict[NPC_SELL_CONDITION][:-2:]
                    sellDict[NPC_SELL_CONDITION].strip()

                IDcounter += 1
                sellingList.append(sellDict)

                # Writing the selling structure ID in respective NPC selling list
                for npcInstance in townList:
                    if npcInstance[NPC_ID] == sellDict[NPC_ID]:
                        npcInstance[NPC_SELL_LIST].append(sellDict[NPC_SELL_ID])
                        break

                if int(sellDict[NPC_SELL_ITEM]) != NOT_FOUND:
                    feedWriteStructure(itemList, sellDict, writeStructure)

            # Refering every selling structure into the respective's item SOURCE_NPC list
            writeOnJSONFiles(writeStructure)
            print("\tSuccessful writing proccess. Exiting with value 0.")

def main():
    townList = []
    sellingList = []
    IDcounter = 1

    # Getting the base information for each NPC
    itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
    npcHash, itemHash = initializeHashTables(itemList)
    scrapGeneralInformation(townList, npcHash)

    # Getting each selling table for every NPC that sells something
    linkList = LoadJSONFile("town_linkdict.json")
    for linkInstance in linkList.values():
        getSellingList(linkInstance, townList, npcHash, itemHash, IDcounter, sellingList, itemList)
        IDcounter = len(sellingList)+1

    SaveJSONFile(SELL_LIST_PATH, sellingList)
    SaveJSONFile(TOWN_NPC_PATH, townList)

if __name__ == "__main__":
    main()
