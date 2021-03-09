import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
from scraping_tools import *
from json_manager import *
import os
from bs4 import BeautifulSoup
import requests 

IMG_OUTPUT_PATH = "fishing_catches/{}.png"

URL = "https://terraria.gamepedia.com/"
itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)

newUrl = URL + "Angler/Quests"
page = requests.get(newUrl)
soup = BeautifulSoup(page.content, 'html.parser')

fishTable = soup.find("table").find_all("tr")

for row in fishTable[1:]:
    imgPath = IMG_OUTPUT_PATH.format(row.find("td", class_="il1c").find("img")["alt"].replace(" ", "_").replace("/", "_"))
    imgSrc = row.find("td", class_="il1c").find("img")["src"]
    print("Generating {}".format(imgPath))
    if writeImage(imgSrc, imgPath) == NOT_FOUND:
        print("Erro")
