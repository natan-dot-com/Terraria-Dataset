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
from bs4 import BeautifulSoup
import requests

# Execution commands
GET_NPC_PAGE_LINK = True
GET_NPC_IMAGES = True

# Constant values
ENEMIES_DIV_SKIP = [15, 16, 17, 18, 19, 20, 21]
BOSSES_STATIC_IMG = ["Lepus", "Moon Lord", "Skeletron",
                     "Queen Slime", "Solar Pillar", "Nebula Pillar",
                     "Vortex Pillar", "Stardust Pillar", "Turkor The Ungrateful",
                     "Eater of Worlds", "The Destroyer"]

MAIN_NPC_FILE_PATH = GLOBAL_JSON_PATH + DIR_NPC_DATA + NPC_NAME_FILE + JSON_EXT
MAIN_URL = "https://terraria.gamepedia.com"
URL_CATEGORY_SUFFIXES = {
    "Enemies": '/Enemies',
    "Critters": '/Critters',
    "NPCs": '/NPCs',
    "Bosses": '/Bosses'
}

def scrapEnemiesPage(npcList, IDcounter):
    if GET_NPC_PAGE_LINK:
        linkDict = {}

    html = requests.get(MAIN_URL + URL_CATEGORY_SUFFIXES["Enemies"])
    soup = BeautifulSoup(html.content, 'html.parser')
    divList = soup.findAll("div", class_="itemlist")
    if divList:
        for divInstance in divList[:-2:]:
            # Skipping bosses division (it'll be made later on)
            if divList.index(divInstance) in ENEMIES_DIV_SKIP:
                continue

            liList = divInstance.findAll("li")
            for liInstance in liList:
                npcTableDict = {
                    NPC_ID: "",
                    SCRAPING_NAME: "",
                    SCRAPING_TYPE: ""
                }
                npcImage = liInstance.a.img
                npcTableDict[NPC_ID] = str(IDcounter)
                npcTableDict[SCRAPING_NAME] = npcImage['alt']
                npcTableDict[SCRAPING_TYPE] = "Enemy"
                print("\tScrapped information from '" + npcTableDict[SCRAPING_NAME] + "'.")

                if GET_NPC_PAGE_LINK:
                    linkDict[npcTableDict[NPC_ID]] = npcImage.parent['href']

                if GET_NPC_IMAGES:
                    filePath = GLOBAL_JSON_PATH + IMAGE_DIR_NPC + npcTableDict[SCRAPING_NAME].lower().replace(" ", "_") + \
                    STATIC_IMAGE_EXT
                    try:
                        with open(filePath, "r") as imageFile:
                            print("\tImage file '" + imageFile.name + "' already exists. Writing proccess aborted.")
                            imageFile.close()
                    except IOError:
                        print("\tWriting image for '" + npcTableDict[SCRAPING_NAME] + "'.")
                        writeImage(npcImage['src'], filePath)

                npcList.append(npcTableDict)
                IDcounter += 1

        if GET_NPC_PAGE_LINK:
            SaveJSONFile("enemy_linkdict.json", linkDict)

def scrapCrittersPage(npcList, IDcounter):
    if GET_NPC_PAGE_LINK:
        linkDict = {}

    html = requests.get(MAIN_URL + URL_CATEGORY_SUFFIXES["Critters"])
    soup = BeautifulSoup(html.content, 'html.parser')
    tableList = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)
    for tableInstance in tableList:
        rows = tableInstance.findAll("tr")
        for row in rows[1::]:
            npcImage = row.img
            npcTableDict = {
                NPC_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_TYPE: ""
            }
            npcTableDict[NPC_ID] = IDcounter
            npcTableDict[SCRAPING_NAME] = npcImage['alt']
            npcTableDict[SCRAPING_TYPE] = "Critter"
            print("\tScrapped information from '" + npcTableDict[SCRAPING_NAME] + "'.")

            if GET_NPC_PAGE_LINK:
                linkDict[npcTableDict[NPC_ID]] = npcImage.parent['href']

            if GET_NPC_IMAGES:
                filePath = GLOBAL_JSON_PATH + IMAGE_DIR_NPC + npcTableDict[SCRAPING_NAME].lower().replace(" ", "_") + \
                STATIC_IMAGE_EXT
                try:
                    with open(filePath, "r") as imageFile:
                        print("\tImage file '" + imageFile.name + "' already exists. Writing proccess aborted.")
                        imageFile.close()
                except IOError:
                    print("\tWriting image for '" + npcTableDict[SCRAPING_NAME] + "'.")
                    writeImage(npcImage['src'], filePath)

            npcList.append(npcTableDict)
            IDcounter += 1

    if GET_NPC_PAGE_LINK:
        SaveJSONFile("critter_linkdict.json", linkDict)

def scrapTownNPCPage(npcList, IDcounter):
    if GET_NPC_PAGE_LINK:
        linkDict = {}

    html = requests.get(MAIN_URL + URL_CATEGORY_SUFFIXES["NPCs"])
    soup = BeautifulSoup(html.content, 'html.parser')
    tableList = soup.findAll("table", class_=TERRARIA_TABLE_CLASS)
    for tableInstance in tableList[:4:]:
        rows = tableInstance.findAll("tr")
        for row in rows[1::]:
            npcImage = row.img
            npcTableDict = {
                NPC_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_TYPE: ""
            }
            npcTableDict[NPC_ID] = IDcounter
            npcTableDict[SCRAPING_NAME] = npcImage['alt']
            npcTableDict[SCRAPING_TYPE] = "Town NPC"
            print("\tScrapped information from '" + npcTableDict[SCRAPING_NAME] + "'.")

            if GET_NPC_PAGE_LINK:
                linkDict[npcTableDict[NPC_ID]] = npcImage.parent['href']

            if GET_NPC_IMAGES:
                filePath = GLOBAL_JSON_PATH + DIR_NPC_DATA + IMAGE_DIR_NPC + npcTableDict[SCRAPING_NAME].lower().replace(" ", "_") + \
                STATIC_IMAGE_EXT
                try:
                    with open(filePath, "r") as imageFile:
                        print("\tImage file '" + imageFile.name + "' already exists. Writing proccess aborted.")
                        imageFile.close()
                except IOError:
                    print("\tWriting image for '" + npcTableDict[SCRAPING_NAME] + "'.")
                    writeImage(npcImage['src'], filePath)

            npcList.append(npcTableDict)
            IDcounter += 1

    if GET_NPC_PAGE_LINK:
        SaveJSONFile("town_linkdict.json", linkDict)

def scrapBossesPage(npcList, IDcounter):
    if GET_NPC_PAGE_LINK:
        linkDict = {}

    html = requests.get(MAIN_URL + URL_CATEGORY_SUFFIXES["Bosses"])
    soup = BeautifulSoup(html.content, 'html.parser')
    divList = soup.findAll("div", class_="infocard")
    for divInstance in divList:
        npcTableDict = {
            NPC_ID: "",
            SCRAPING_NAME: "",
            SCRAPING_TYPE: ""
        }
        npcTableDict[NPC_ID] = IDcounter
        npcTableDict[SCRAPING_NAME] = divInstance.find("div", class_="hgroup").find("div", class_="main").text.strip()
        npcTableDict[SCRAPING_TYPE] = "Boss"
        print("\tScrapped information from '" + npcTableDict[SCRAPING_NAME] + "'.")

        if GET_NPC_PAGE_LINK:
            linkDict[npcTableDict[NPC_ID]] = divInstance.a['href']

        if GET_NPC_IMAGES:
            filePath = GLOBAL_JSON_PATH + DIR_NPC_DATA + IMAGE_DIR_NPC + npcTableDict[SCRAPING_NAME].lower().replace(" ", "_")
            if npcTableDict[SCRAPING_NAME] not in BOSSES_STATIC_IMG:
                filePath += DYNAMIC_IMAGE_EXT
            else:
                filePath += STATIC_IMAGE_EXT

            try:
                with open(filePath, "r") as imageFile:
                    print("\tImage file '" + imageFile.name + "' already exists. Writing proccess aborted.")
                    imageFile.close()
            except IOError:
                print("\tWriting image for '" + npcTableDict[SCRAPING_NAME] + "'.")
                writeImage(divInstance.img['src'], filePath)

        npcList.append(npcTableDict)
        IDcounter += 1

    if GET_NPC_PAGE_LINK:
        SaveJSONFile("boss_linkdict.json", linkDict)

def main():
    if GET_NPC_PAGE_LINK:
        print("GET_NPC_PAGE_LINK set to 'True'. Several files gonna be created in src folder.")
    if GET_NPC_IMAGES:
        print("GET_NPC_IMAGES set to 'True'. Creating main image folder on '" + GLOBAL_JSON_PATH + DIR_NPC_DATA + IMAGE_DIR_NPC + "'.")
        if not os.path.exists(GLOBAL_JSON_PATH + DIR_NPC_DATA + IMAGE_DIR_NPC):
            Path(GLOBAL_JSON_PATH + DIR_NPC_DATA + IMAGE_DIR_NPC).mkdir(parents=True, exist_ok=True)

    npcList = []
    functionList = [
        scrapEnemiesPage,
        scrapCrittersPage,
        scrapTownNPCPage,
        scrapBossesPage
    ]

    IDcounter = 1
    for functionInstance, categoryInstance in zip(functionList, URL_CATEGORY_SUFFIXES):
        print("Starting getting information from " + categoryInstance + "...")
        functionInstance(npcList, IDcounter)
        IDcounter = len(npcList)+1
    print("Successful operation. Exiting with value 0.")
    SaveJSONFile(MAIN_NPC_FILE_PATH, npcList)

if __name__ == '__main__':
    main()
