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
import threading
import math

sucessful = 200
IMG_OUTPUT_PATH = "img/{}.png"

URL = "https://terraria.gamepedia.com/"
logFile = 'img_log.txt'
logThread = "thread_log.txt"
exitFlag = 0
itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)

class myThread (threading.Thread):
   def __init__(self, threadID, init, fin):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.init = init
      self.fin = fin
   def run(self):
      print ("Starting Thread " + str(self.threadID))
      imgSearch(self.init, self.fin)
      with open(logThread, "a") as log:
            log.write("Exiting Thread " + str(self.threadID) + "\n")
      print ("Exiting Thread " + str(self.threadID))

def imgSearch(init, fin):
    for itemInstance in itemList[init:fin]:
        imgPath = IMG_OUTPUT_PATH.format(itemInstance[SCRAPING_NAME].replace(" ", "_").replace("/", "_"))
        if not os.path.isfile(imgPath):
            newUrl = URL + itemInstance[SCRAPING_NAME].replace(" ", "_")
            print("processing {} with ID {}".format(newUrl, itemInstance[SCRAPING_ID]))
            page = requests.get(newUrl)
            if page.status_code == sucessful:         
                soup = BeautifulSoup(page.content, 'html.parser')
                tableBoxes = soup.find_all("div", class_="infobox item")
                if tableBoxes:
                    soup = tableBoxes[0]
                    for tableBoxTmp in tableBoxes:
                        if tableBoxTmp.find("div", class_="title").text == itemInstance[SCRAPING_NAME]:
                            soup = tableBoxTmp
                tableBoxImage = soup.find("div", class_="section images")
                
                if tableBoxImage:
                    imgSrc = tableBoxImage.find("img")["src"]
                    if writeImage(imgSrc, imgPath) == NOT_FOUND:
                        with open(logFile, "a") as log:
                            log.write("Failed to write image" + str(itemInstance[SCRAPING_ID]) + "\n")
                else:
                    with open(logFile, "a") as log:
                        log.write("Image not found with link " + newUrl + " and ID " + str(itemInstance[SCRAPING_ID]) + "\n")



if os.path.exists(logFile):
  os.remove(logFile)

#Four threads
'''firstQuarter = math.floor(len(itemList)/4)
secondQuarter = math.floor(len(itemList)/2)
thirdQuarter = 3*math.floor((len(itemList)/4))
fouthQuarter = math.floor(len(itemList))

thread1 = myThread(1, 0, firstQuarter)
thread2 = myThread(2, firstQuarter, secondQuarter)
thread3 = myThread(3, secondQuarter, thirdQuarter)
thread4 = myThread(4, thirdQuarter, fouthQuarter)'''

#Eight threads
firstOctave = math.floor(len(itemList)/8)
secondOctave = 2*math.floor(len(itemList)/8)
thirdOctave = 3*math.floor(len(itemList)/8)
fourthOctave = 4*math.floor(len(itemList)/8)
fifthOctave = 5*math.floor(len(itemList)/8)
sixthOctave = 6*math.floor(len(itemList)/8)
seventOctave = 7*math.floor(len(itemList)/8)
eighthOctave = 8*math.floor(len(itemList)/8)

thread1 = myThread(1, 0, firstOctave)
thread2 = myThread(2, firstOctave, secondOctave)
thread3 = myThread(3, secondOctave, thirdOctave)
thread4 = myThread(4, thirdOctave, fourthOctave)
thread5 = myThread(5, fourthOctave, fifthOctave)
thread6 = myThread(6, fifthOctave, sixthOctave)
thread7 = myThread(7, sixthOctave, seventOctave)
thread8 = myThread(8, seventOctave, eighthOctave)

#Start Eight Threads
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()
thread7.start()
thread8.start()

#Join eight Threads
thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()
thread6.join()
thread7.join()
thread8.join()
