import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
from scraping_tools import *
from json_manager import *

def searchByName(JSONData, name):
    for JSONInstance in JSONData:
        if JSONInstance[SCRAPING_NAME].lower().replace(" ", "_").replace("/", "_") == name.lower():
            return JSONInstance
    return NOT_FOUND

IMG_PATH = "img/{}.png"

itemList = LoadJSONFile(GLOBAL_JSON_PATH + MAIN_NAME_FILE + JSON_EXT)

for itemInstance in itemList:
    if not os.path.isfile(IMG_PATH.format(itemInstance[SCRAPING_NAME].replace(" ", "_").replace("/", "_"))):
        print("{} not found on img path".format(itemInstance[SCRAPING_NAME]))

directory = "img/"
for filename in os.listdir(directory):
    if filename.endswith(".png"):
        newFilename = os.path.join(filename).split(".png")[0]
        if searchByName(itemList, newFilename) == NOT_FOUND:
            print("{} not found on item json".format(newFilename))
    else:
        continue