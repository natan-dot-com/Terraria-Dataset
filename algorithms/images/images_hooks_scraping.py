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

IMG_OUTPUT_PATH = "img/{}.png"

URL = "https://terraria.gamepedia.com/"
itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)

newUrl = URL + "Hooks"
page = requests.get(newUrl)
soup = BeautifulSoup(page.content, 'html.parser')

hookTables = soup.find_all("table")
print(len(hookTables))

for hookTable in hookTables[1:]:
    hookTrs = hookTable.find_all("tr")
    for hookTr in hookTrs[1:]:
        imgPath = IMG_OUTPUT_PATH.format(hookTr.find("td", class_="il1c").find("img")["alt"].replace(" ", "_").replace("/", "_"))
        imgSrc = hookTr.find("td", class_="il1c").find("img")["src"]
        print("Generating {}".format(imgPath))
        if writeImage(imgSrc, imgPath) == NOT_FOUND:
            print("Erro")
