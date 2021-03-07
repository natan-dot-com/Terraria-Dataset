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

import re
import requests
from ...package.scraping_tools import *
from ...package.json_manager import *
from bs4 import BeautifulSoup

AMMUNITION_PATH = GLOBAL_JSON_PATH + DIR_ITEMS_DATA + AMMUNITION_NAME_FILE + JSON_EXT
OTHER_VERSIONS = {"3DS version", "Console Version", "Old-gen console version", "Mobile version"}
DESKTOP_VERSION = {"Desktop"}
AMMOS_TYPES = ["Arrows", "Bullets", "Rockets", "Darts", "Solutions"]
AMMO_EXCEPTIONS = [
    ["Gel", "Flamethrower, Elf Melter"], ["Coins", "Coin Gun"], ["Fallen Star", "Star Cannon, Super Star Shooter"],
    ["Seed", "Blowpipe, Blowgun, Dart Pistol, Dart Rifle"], ["Cannonball", "Cannon"],
    ["Snowball", "Snowball Cannon, Snowball Launcher"], ["Stynger Bolt", "Stynger"],
    ["Explosive Bunny", "Bunny Cannon"], ["Confetti", "Confetti Gun"], ["Candy Corn", "Candy Corn Rifle"],
    ["Explosive Jack 'O Lantern", "Jack 'O Lantern Launcher"], ["Stake", "Stake Launcher"],
    ["Nail", "Nail Gun"], ["Flare", "Flare Gun"]
]

WIKI_URL = "https://terraria.gamepedia.com/"
ammoList = []

for pageName in AMMOS_TYPES:
    newURL = WIKI_URL + pageName
    page = requests.get(newURL)
    soup = BeautifulSoup(page.content, 'html.parser')

    #for Arrows, Bullets and Darts pages
    if pageName == "Arrows" or pageName == "Bullets" or pageName == "Darts":

        items = soup.find("table", class_=TERRARIA_TABLE_CLASS).find_all("tr")

        for item in items[1:]:
            if item.find_all("td")[1].find("img", alt=OTHER_VERSIONS) and not item.find_all("td")[1].find("img", alt=DESKTOP_VERSION):
                print("item {} isn't desktop".format(item.img['alt']))
                continue

            newURL = WIKI_URL + item.img['alt'].replace(" ", "_")
            page2 = requests.get(newURL)
            soup2 = BeautifulSoup(page2.content, 'html.parser')
            print("Processing {}".format(newURL))

            tableBox = soup2.find("div", class_="infobox item")
            status = {
                SCRAPING_ID: tableBox.find("div", class_="section ids").find("li").b.text,
                SCRAPING_NAME: tableBox.find("div", class_="title").text
            }
            usedIn = ""
            if pageName == "Arrows":
                usedIn = "Any Bow or Repeater."
            elif pageName == "Bullets":
                usedIn = "Any Gun"
            elif pageName == "Darts":
                usedIn = "Blowgun, Blowpipe, Dart Pistol and Dart Rifle"

            ammoList.append(get_statistics(tableBox, usedIn=usedIn))

    #for Rockets page
    elif pageName == "Rockets":

        items = soup.find("table", class_=TERRARIA_TABLE_CLASS).find_all("tr")

        for item in items[1:]:
            if item.find_all("td")[0].find("img", alt=OTHER_VERSIONS) and not item.find_all("td")[1].find("img", alt=DESKTOP_VERSION):
                print("item {} isn't desktop".format(item.img['alt']))
                continue

            ammoDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_DAMAGE: "",
                SCRAPING_AVAILABILITY: "",
                SCRAPING_RADIUS: "",
                SCRAPING_DESTROY_TILES: "",
                SCRAPING_RARITY: "",
                SCRAPING_USED_IN: "",
                SCRAPING_SOURCE: SOURCE_SOURCES_DICT
            }
            tdTags = item.find_all("td")

            id = item.find("div", class_="id")      
            ammoDict[SCRAPING_ITEM_ID] = (re.search("\d+", id.text)).group()
            ammoDict[SCRAPING_NAME] = item.img['alt']
            ammoDict['Used In'] = "Launcher"
            ammoDict[SCRAPING_DAMAGE] = tdTags[1].text.split(' ')[0].rstrip()
            ammoDict[SCRAPING_AVAILABILITY] = tdTags[2].text.rstrip().replace("or", "or ")
            ammoDict[SCRAPING_RARITY] = tdTags[3].a['title'].split(' ')[-1]
            ammoDict[SCRAPING_RADIUS] = tdTags[5].text.rstrip()
            ammoDict[SCRAPING_DESTROY_TILES] = tdTags[6].img['alt']
            ammoList.append(ammoDict)

    #for Solutions page
    elif pageName == "Solutions":

        items = soup.find("table", class_=TERRARIA_TABLE_CLASS).find_all("tr")
        for item in items[1:]:
            if item.find_all("td")[0].find("img", alt=OTHER_VERSIONS) and not item.find_all("td")[1].find("img", alt=DESKTOP_VERSION):
                print("item {} isn't desktop".format(item.img['alt']))
                continue

            ammoDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_AVAILABLE: "",
                SCRAPING_EFFECT: "",
                SCRAPING_RARITY: "",
                SCRAPING_TOOLTIP: "",
                SCRAPING_USED_IN: "",
                SCRAPING_SOURCE: SOURCE_SOURCES_DICT
            }
            tdTags = item.find_all("td")
            id = item.find("div", class_="id")      
            ammoDict[SCRAPING_ITEM_ID] = (re.search("\d+", id.text)).group()
            ammoDict[SCRAPING_NAME] = item.img['alt']
            ammoDict[SCRAPING_AVAILABLE] = " ".join((tdTags[1].text.rstrip()).split("  "))
            ammoDict[SCRAPING_EFFECT] = BeautifulSoup(str(tdTags[2]).replace("<br/>", ". "), 'html.parser').text.rstrip()
            ammoDict[SCRAPING_RARITY] = "3"
            ammoDict[SCRAPING_TOOLTIP] = BeautifulSoup(str(tdTags[3]).replace("<br/>", ". "), 'html.parser').text.rstrip()
            ammoDict[SCRAPING_USED_IN] = "Clentaminator"
            ammoList.append(ammoDict)

#untyped ammos
for ammo in AMMO_EXCEPTIONS:
    print("Processing {}".format(ammo[0]))
    newURL = WIKI_URL + ammo[0].replace(" ", "_")
    page = requests.get(newURL)
    soup = BeautifulSoup(page.content, 'html.parser')

    #Coins ammo
    if ammo[0] == "Coins":
        tableCoins = soup.find("table", class_=TERRARIA_TABLE_CLASS).tbody.find_all("tr")
        for tableCoin in tableCoins[1:]:
            ammoDict = {
                SCRAPING_ITEM_ID: "",
                SCRAPING_NAME: "",
                SCRAPING_DAMAGE: "",
                SCRAPING_VELOCITY: "",
                SCRAPING_RARITY: "",
                SCRAPING_RESEARCH: "",
                SCRAPING_USED_IN: "",
                SCRAPING_SOURCE: SOURCE_SOURCES_DICT
            }
            id = tableCoin.find("div", class_="id")
            tdTags = tableCoin.find_all("td")
            ammoDict[SCRAPING_ITEM_ID] = (re.search("\d+", id.text)).group()
            ammoDict[SCRAPING_NAME] = tdTags[1].span.span.span.text
            ammoDict[SCRAPING_USED_IN] = ammo[1]
            ammoDict[SCRAPING_DAMAGE] = tdTags[4].text.rstrip()
            ammoDict[SCRAPING_VELOCITY] = tdTags[5].text.rstrip()
            ammoDict[SCRAPING_RARITY] = soup.find("div", class_="infobox item").find("span", class_="rarity").a['title'].split(' ')[-1]
            ammoDict[SCRAPING_RESEARCH] = soup.find("div", class_="infobox item").find("a", title="Journey mode").parent.parent.td.text.rstrip()
            ammoList.append(ammoDict)

    #Flare ammos
    elif ammo[0] == "Flare":
        tableBoxes = soup.find_all("div", class_="infobox item")
        for tableBox in tableBoxes[1:]:
            status = {
                SCRAPING_ID: tableBox.find("div", class_="section ids").find("li").b.text,
                SCRAPING_NAME: tableBox.find("div", class_="title").text
            }
            usedIn = ammo[1]
            ammoList.append(get_statistics(tableBox, usedIn=usedIn))

    #everything else
    else:
        tableBox = soup.find("div", class_="infobox item")
        usedIn = ammo[1]
        ammoList.append(get_statistics(tableBox, usedIn=usedIn))

SaveJSONFile(AMMUNITION_PATH, sortListOfDictsByKey(ammoList, SCRAPING_ITEM_ID))
