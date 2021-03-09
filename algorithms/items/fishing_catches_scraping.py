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

FISHING_CATCHES_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + FISHING_CATCHES_NAME_FILE + JSON_EXT
URL = "https://terraria.gamepedia.com/"
FISH_URL = "Fishing_catches"
JUNK_LIST = ["Old Shoe", "Seaweed", "Tin Can"]

itemList = LoadJSONFile(GLOBAL_JSON_PATH + DIR_ID_REFERENCES + MAIN_NAME_FILE + JSON_EXT)
fishesList = []
newURL = URL + FISH_URL
pageFish = requests.get(newURL)
soupFish = BeautifulSoup(pageFish.content, "html.parser")

fishTable = soupFish.find("table", class_=TERRARIA_TABLE_CLASS)
fishRows = fishTable.find_all("tr")

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Fishing catches":
        if not itemInstance[SCRAPING_NAME] in JUNK_LIST:
            newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
            page = requests.get(newURL)
            soup = BeautifulSoup(page.content, "html.parser")
            print("processing {}".format(newURL))

            tableBoxes = soup.find_all("div", class_="infobox item")
            tableBox = tableBoxes[0]
            for tableBoxTmp in tableBoxes:
                if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                    tableBox = tableBoxTmp
            fishDict = get_statistics(tableBox, itemInstance=itemInstance)

            for fishRow in fishRows[1:]:
                if fishRow.find("td", class_="il2c").find("a").text == itemInstance[SCRAPING_NAME]:
                    fishDict.pop(SCRAPING_SOURCE, None)
                    fishDict[SCRAPING_HEIGHT] = fishRow.find_all("td")[4].text.encode("ascii", "ignore").decode().rstrip()

                    textBiome = ""
                    if fishRow.find_all("td")[5].find("span", class_="eico"):
                        textBiome = fishRow.find_all("td")[5].contents[0].rstrip()
                        if re.search("\(", textBiome) and not re.search("\)", textBiome):
                            textBiome += ")"
                    else:
                        textBiome = fishRow.find_all("td")[5].text.encode("ascii", "ignore").decode().replace(" )", ")").rstrip()
                    if re.search("\[\d]", textBiome):
                        fishDict[SCRAPING_BIOME] = textBiome.replace(re.search("\[\d]", textBiome).group(), "")
                    else:
                        fishDict[SCRAPING_BIOME] = textBiome

                    textCatch = ""
                    if fishRow.find_all("td")[5].find("span", class_="eico"):
                        textCatch = fishRow.find_all("td")[6].contents[0].rstrip()
                        if re.search("\(", textCatch) and not re.search("\)", textCatch):
                            textCatch += ")"
                    else:
                        textCatch = fishRow.find_all("td")[6].text.encode("ascii", "ignore").decode().replace(" )", ")").rstrip()
                    if re.search("\[\d]", textCatch):
                        fishDict[SCRAPING_CATCH_QUALITY] = textCatch.replace(re.search("\[\d]", textCatch).group(), "")
                    else:
                        fishDict[SCRAPING_CATCH_QUALITY] = textCatch
                    fishDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
                    fishesList.append(fishDict)
                    break 
        else:
            fishDict = {
                SCRAPING_ITEM_ID: itemInstance[SCRAPING_ID],
                SCRAPING_NAME: itemInstance[SCRAPING_ID],
                SCRAPING_RARITY: "-1",
                SCRAPING_HEIGHT: "Any",
                SCRAPING_BIOME: "Any",
                SCRAPING_SOURCE: SOURCE_SOURCES_DICT
            }
            fishesList.append(fishDict)

SaveJSONFile(FISHING_CATCHES_PATH, fishesList)
