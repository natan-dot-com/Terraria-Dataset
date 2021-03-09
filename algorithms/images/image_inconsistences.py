import json
import bs4
from bs4 import BeautifulSoup
import requests

DIR_PREFIX = "img_lanterns/"
URL = "https://terraria.gamepedia.com/Lanterns"
SUCCESS = 200

pageRequest = requests.get(URL)
if pageRequest.status_code == SUCCESS:
    soup = BeautifulSoup(pageRequest.content, 'html.parser')
    itemImage = soup.findAll("table", class_="terraria")   
    for imageInstance in itemImage:
        imgTag = imageInstance.findAll('tr')
        for imgSrc in imgTag:
            if imgSrc.find('td'):
                src = (imgSrc.find('img'))['src']
                imgPath = DIR_PREFIX + (imgSrc.find('img'))['alt'].replace("placed", "").rstrip().replace(" ", "_") + '.png'
                print(imgPath)
                imgOutput = requests.get(src, stream=True)
                if imgOutput.ok:
                    with open(imgPath, 'wb') as handler:
                        for block in imgOutput.iter_content(1024):
                            if not block:
                                break
                            handler.write(block)

