from .scraping_tools import *
import json

NOT_FOUND = -1

GLOBAL_JSON_PATH = "json/"

# Loads a structure inside a JSON file
def LoadJSONFile(JSONPath):
    try:
        with open(JSONPath) as JSONFile:
            print("File '" + JSONPath + "' found.")
            JSONData = json.load(JSONFile)        
    except IOError:
        print("Requested file '" + JSONPath + "' not found.")
        JSONData = []
    return JSONData

# Saves a structure in a JSON file
def SaveJSONFile(JSONPath, Structure):
    with open(JSONPath, "w") as newJSONFile:
        json.dump(Structure, newJSONFile, indent=4)
        
# Finds the item's dictionary in respect of its name
def searchByName(JSONData, name):
    for JSONInstance in JSONData:
        if JSONInstance["Name"].lower() == name.lower():
            return JSONInstance
    return NOT_FOUND
    
# Finds the ID in respect of an item in items.json
def searchForID(itemName, itemList):
    for itemInstance in itemList:
        if itemName == itemInstance[SCRAPING_NAME]:
            return itemInstance[SCRAPING_ID]
