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
PYLON_IMAGE_PATH = "img/{}.png"
PYLON_OTHERS_IMAGE_PATH = "data_scraping/pylon_img/{}.png"

newURL = URL + "Pylons"
page = requests.get(newURL)
soup = BeautifulSoup(page.content, "html.parser")

pylonTable = soup.find("table", class_="terraria").find_all("tr")
for pylonRow in pylonTable[1:]:
    imgPylonSrc = pylonRow.find("td", class_="il1c").img["src"]
    imgPylonName = pylonRow.find("td", class_="il1c").img["alt"].replace(" ", "_")
    print("Saving {}".format(imgPylonName))
    writeImage(imgPylonSrc, PYLON_IMAGE_PATH.format(imgPylonName))

    imgPlacedSrc = pylonRow.find_all("td")[2].img["src"]
    imgPylonName = pylonRow.find_all("td")[2].img["alt"].replace(" ", "_")
    print("Saving {}".format(imgPylonName))
    writeImage(imgPlacedSrc, PYLON_OTHERS_IMAGE_PATH.format(imgPylonName))

    imgMapSrc = pylonRow.find_all("td")[4].img["src"]
    imgMapName = pylonRow.find_all("td")[4].img["alt"].replace(" ", "_").split(".png")[0]
    print("Saving {}".format(imgMapName))
    writeImage(imgMapSrc, PYLON_OTHERS_IMAGE_PATH.format(imgMapName))

