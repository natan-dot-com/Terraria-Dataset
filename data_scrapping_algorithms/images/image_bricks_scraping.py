#Everything seems to work.

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir) 
from scraping_tools import *
from json_manager import *
from bs4 import BeautifulSoup
import requests

URL = "https://terraria.gamepedia.com/"
BRICKS_IMAGE_PATH = "bricks/{}.png"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)
brickList = LoadJSONFile(GLOBAL_JSON_PATH + BRICK_NAME_FILE + JSON_EXT)

for itemInstance in itemList:
    if itemInstance[SCRAPING_TYPE] == "Brick":
        newURL = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
        page = requests.get(newURL)
        soup = BeautifulSoup(page.content, "html.parser")
        print("processing {}".format(newURL))

        tableBoxes = soup.find_all("div", class_="infobox item")
        tableBox = tableBoxes[0]
        for tableBoxTmp in tableBoxes:
            if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                tableBox = tableBoxTmp
            
        #Get Brick Appearance
        imageBrick = tableBox.find("ul", class_="infobox-inline").find_all("li")[-1].img["src"]
        imageBrickName = tableBox.find("ul", class_="infobox-inline").find_all("li")[-1].img["alt"].replace(" ", "_")
        imageBrickPath = BRICKS_IMAGE_PATH.format(imageBrickName)
        print("Saving {}".format(imageBrickPath))
        writeImage(imageBrick, GLOBAL_JSON_PATH  + imageBrickPath)

        for brickInstance in brickList:
            if tableBox.find("ul", class_="infobox-inline").find_all("li")[-1].img["alt"].replace(" placed", "") == brickInstance[SCRAPING_NAME]:
                brickInstance[IMAGE_BRICK] = imageBrickPath

SaveJSONFile(GLOBAL_JSON_PATH + BRICK_NAME_FILE + JSON_EXT, brickList)