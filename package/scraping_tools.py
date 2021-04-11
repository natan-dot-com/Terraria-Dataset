from io import StringIO
from typing import Any
import requests
import re
from bs4 import BeautifulSoup
import operator
from .log_manager import LOG_PATH
import logging

# Put the number of threads you want to use on scraping process
THREADS_SIZE = 8

NOT_FOUND = -1
FOUND = 1

# Table HTML classes
TERRARIA_TABLE_CLASS = "terraria"
SORTABLE_TABLE_CLASS = "sortable"
STAT_TABLE_CLASS = "stat"

# ID labels
SCRAPING_ID = "ID"
SCRAPING_ITEM_ID = "Item ID"
SCRAPING_SET_ID = "Set ID"
SCRAPING_RARITY_ID = "Rarity ID"

# General labels
SCRAPING_TYPE = "Type"
SCRAPING_NAME = "Name"
SCRAPING_RARITY = "Rarity"
SCRAPING_USE_TIME = "Use time"
SCRAPING_VELOCITY = "Velocity"
SCRAPING_TOOL_SPEED = "Tool speed"
SCRAPING_PICKAXE_POWER = "Pickaxe power"
SCRAPING_HAMMER_POWER = "Hammer power"
SCRAPING_AXE_POWER = "Axe power"
SCRAPING_FISHING_POWER = "Fishing Power"
SCRAPING_DEFENSE = "Defense"
SCRAPING_BODY_SLOT = "Body slot"
SCRAPING_TOOLTIP = "Tooltip"
SCRAPING_RESEARCH = "Research"
SCRAPING_USED_IN = "Used In"
SCRAPING_DAMAGE = "Damage"
SCRAPING_MULTIPLIER = "Multiplier"
SCRAPING_KNOCKBACK = "Knockback"
SCRAPING_AVAILABLE = "Available"
SCRAPING_AVAILABILITY = "Availability"
SCRAPING_EFFECT = "Effect"
SCRAPING_SOURCE = "Source"
SCRAPING_RADIUS = "Radius"
SCRAPING_DESTROY_TILES = "Destroy Tiles"
SCRAPING_PLACEABLE = "Placeable"
SCRAPING_SET_PIECES = "Set Pieces"
SCRAPING_SET_NAME = "Set Name"
SCRAPING_SET_BONUS = "Set Bonus"
SCRAPING_MANA = "Mana"
SCRAPING_CRITICAL_CHANCE = "Critical chance"
SCRAPING_REACH = "Reach"
SCRAPING_HOOKS = "Hooks"
SCRAPING_LATCHING = "Latching"
SCRAPING_ORE_TIER = "Ore Tier"
SCRAPING_MINIMUM_PICKAXE_POWER = "Minimum Pickaxe Power"
SCRAPING_CONSUMED = "Is Consumed"
SCRAPING_ANGLER_QUOTE = "Angler Quote"
SCRAPING_HEIGHT = "Height"
SCRAPING_BIOME = "Biome"
SCRAPING_SOURCE = "Sources"
SCRAPING_RARITY_TIER = "Rarity Tier"
SCRAPING_RARITY_DESC = "Rarity Description"
SCRAPING_MAX_LIFE = "Max Life"
SCRAPING_BUY = "Buy"
SCRAPING_SELL = "Sell"
SCRAPING_BASE_VELOCITY = "Base Velocity"
SCRAPING_VELOCITY_MULTIPLIER = "Velocity Multiplier"
SCRAPING_LIGHT_PET = "Light Pet"
SCRAPING_BRIGHTNESS = "Brightness"
SCRAPING_NOTES = "Notes"
SCRAPING_BUFF_IMAGE = "Buff Image"
SCRAPING_PET_IMAGE = "Light Pet Image"
SCRAPING_MASTER_MODE = "Master Mode Exclusive:"
SCRAPING_DESCRIPTION = "Description"
SCRAPING_TOOLTIP = "Tooltip"
SCRAPING_DESTROYED_BY_EXPLOSIVES = "Destroyed by Explosives"
SCRAPING_BONUS = "Bonus"
SCRAPING_USABLE = "Usable"
SCRAPING_MAX_STACK = "Max stack"
SCRAPING_CREATES = "Creates"
SCRAPING_PLANTED_IN = "Planted In"
SCRAPING_CATCH_QUALITY = "Catch Quality"
SCRAPING_EVENT = "Event"
SCRAPING_BAIT_POWER = "Bait Power"
SCRAPING_SUMMONS = "Summons"
SCRAPING_HOUSE = "House"
SCRAPING_MECHANISM = "Mechanism"
SCRAPING_WATERPROOF = "Waterproof"
SCRAPING_BAG_DROPS = "Bag Drops"
SCRAPING_SPAWN_REQUIREMENT = "Spawn Requirement"
SCRAPING_DURATION = "Duration"
SCRAPING_BUFF = "Buff"
SCRAPING_BUFF_TOOLTIP = "Buff tooltip"
SCRAPING_CONSUMABLE = "Consumable"
SCRAPING_DEBUFF = "Debuff"
SCRAPING_DEBUFF_TOOLTIP = "Debuff tooltip"
SCRAPING_ENVIRONMENT = "Environment"
SCRAPING_AI_TYPE = "AI Type"
SCRAPING_PICKAXE_POWER_REQUIRED = "Pickaxe power required"

# Image data
IMAGE_BRICK = "Brick Image"
IMAGE_IN_STONE = "In Stone"
IMAGE_PLACED = "Placed"
IMAGE_RARITY = "Rarity Image Path"

# Source dict labels ('SCRAPING_SOURCE')
SOURCE_RECIPES = "Crafting Recipes"
SOURCE_NPC = "NPC"
SOURCE_DROP = "Drop"
SOURCE_GRAB_BAG = "Grab Bag"
SOURCE_OTHER = "Other"
SOURCE_SOURCES_DICT = {
    SOURCE_RECIPES: [],
    SOURCE_NPC: [],
    SOURCE_DROP: [],
    SOURCE_GRAB_BAG: [],
    SOURCE_OTHER: "",
}

# Drop dict labels ('SCRAPING_SOURCE' subdict)
# About Drop Dict:
    # DROP_ID: ID identifier for each structure
    # DROP_ITEM: Which item can be dropped
    # DROP_PROBABILITY: Probability value to drop
    # DROP_QUANTITY: How many does it drop
    # DROP_NPC: From which NPC it can be dropped
DROP_ID = "Drop ID"
DROP_NPC = "NPC"
DROP_ITEM = "Item Dropped"
DROP_PROBABILITY = "Probability"
DROP_QUANTITY = "Quantity"
DROP_DROPS_DICT = {
    DROP_ID: "",
    DROP_PROBABILITY: "",
    DROP_QUANTITY: "",
    DROP_NPC: ""
}

# Crafting recipe labels ('SCRAPING_SOURCE' subdict)
# From tables.json
TABLE_RECIPES_LIST = "Table Recipes List"

# From recipes.json
# About Recipe Crafting Dict:
    # RECIPE_CRAFT_ID: ID identifier for each structure
    # RECIPE_RESULT Which item is crafted
    # RECIPE_RESULT_QUANTITY: How many it's crafted
    # RECIPE_TABLE: In which table it can be crafted
    # RECIPE_IDENTITY: Every ingredient from that recipe,
    #  containing a list of ingredient dictionaries (as it
    #  can be seen below)
RECIPE_CRAFT_ID = "Craft ID"
RECIPE_RESULT = "Result ID"
RECIPE_RESULT_QUANTITY = "Result Quantity"
RECIPE_TABLE = "Table ID"
RECIPE_IDENTITY = "Recipe"
RECIPE_CRAFTING_DICT = {
    RECIPE_CRAFT_ID: "",
    RECIPE_RESULT: "",
    RECIPE_RESULT_QUANTITY: "",
    RECIPE_TABLE: "",
    RECIPE_IDENTITY: []
}

# Recipe ingredient labels ('RECIPE_IDENTITY' subdict)
INGREDIENT_NAME = "Ingredient ID"
INGREDIENT_QUANTITY = "Quantity"
INGREDIENT_DICT = {
    INGREDIENT_NAME: "",
    INGREDIENT_QUANTITY: ""
}

# Grab bag dict labels ('SCRAPING_SOURCE' subdict)
# From grab_bags.json
GRAB_BAGS_LOOT_LIST = "Grab Bag Loot List"

# From bag_drops.json
# About Bag Drops Dict:
    # BAG_DROP_ID: ID identifier for each structure
    # BAG_DROP_RESULT: Which item is dropped
    # BAG_DROP_PROBABILITY: Probability value to drop
    # BAG_DROP_QUANTITY: How much it can drop
    # BAG_ID: From which bag it can be dropped
BAG_DROP_ID = "Bag Drop ID"
BAG_ID = "Bag ID"
BAG_DROP_RESULT = "Drop Result"
BAG_DROP_PROBABILITY = "Probability"
BAG_DROP_QUANTITY = "Quantity"
BAG_DROPS_DICT = {
    BAG_DROP_ID: "",
    BAG_DROP_RESULT: "",
    BAG_DROP_PROBABILITY: "",
    BAG_DROP_QUANTITY: "",
    BAG_ID: ""
}

# Rarity labels
RARITY_GRAY = "Gray"
RARITY_AMBER = "Quest"
RARITY_RAINBOW = "Rainbow"
RARITY_FIERY_RED = "Fiery red"
RARITY_TIER = {
    RARITY_GRAY: "-1",
    RARITY_AMBER: "-11",
    RARITY_RAINBOW: "-12",
    RARITY_FIERY_RED: "-13"
}

# NPC related labels
NPC_SELL_LIST = "Selling List"

# ABout Sell Structure:
    # NPC_SELL_ID: ID identifier for each structure
    # NPC_ID: Which NPC sells
    # NPC_SELL_ITEM: Which item it sells
    # NPC_ITEM_COST: How much does it cost
    # NPC_SELL_CONDITION: In what condition does that NPC sell
NPC_SELL_ID = "Sell ID"
NPC_ID = "NPC ID"
NPC_SELL_ITEM = "Selling Item"
NPC_ITEM_COST = "Item Cost"
NPC_SELL_CONDITION = "Sell Condition"
SELL_STRUCTURE = {
    NPC_SELL_ID: "",
    NPC_ID: "",
    NPC_SELL_ITEM: "",
    NPC_ITEM_COST: "",
    NPC_SELL_CONDITION: ""
}

# Files extensions labels
STATIC_IMAGE_EXT = ".png"
DYNAMIC_IMAGE_EXT = ".gif"
JSON_EXT = ".json"

# 'json/' labels
DIR_ID_REFERENCES = "id_references/"
DIR_ITEMS_DATA = "items_data/"
DIR_NPC_DATA = "npc_data/"

# ID references files labels
TABLE_NAME_FILE = "crafting_stations"
RECIPE_NAME_FILE = "recipes"
MAIN_NAME_FILE = "items"
BAGS_NAME_FILE = "grab_bags"
BAGS_DROP_NAME_FILE = "grab_bags_drops"
NPC_NAME_FILE = "npc"
SELLING_LIST_NAME_FILE = "selling_list"
SET_NAME_FILE = "set"

# Items subfiles labels
MAIN_ITEM_SUBFILE_PREFIX = "items_"
ACCESSORY_NAME_FILE = "items_accessory"
AMMUNITION_NAME_FILE = "items_ammunition"
ARMOR_NAME_FILE = "items_armor"
BACKGROUND_NAME_FILE = "items_background"
BAIT_NAME_FILE = "items_bait"
BLOCK_NAME_FILE = "items_block"
BOSS_SUMMON_NAME_FILE = "items_boss_summon"
BRICK_NAME_FILE = "items_brick"
CONSUMABLE_NAME_FILE = "items_consumable"
CRAFTING_MATERIAL_NAME_FILE = "items_crafting_material"
CRITTER_NAME_FILE = "items_critter"
DYE_NAME_FILE = "items_dye"
EVENT_SUMMON_NAME_FILE = "items_event_summon"
FISHING_CATCHES_NAME_FILE = "items_fishing_catches"
FURNITURE_NAME_FILE = "items_furniture"
FOOD_NAME_FILE = "items_food"
GEM_NAME_FILE = "items_gem"
GRAB_BAG_NAME_FILE = "items_grab_bag"
HOOK_NAME_FILE = "items_hook"
KEY_NAME_FILE = "items_key"
LIGHT_PET_NAME_FILE = "items_light_pet"
LIGHT_SOURCE_NAME_FILE = "items_light_source"
ORE_NAME_FILE = "items_ore"
PAINTING_NAME_FILE = "items_painting"
POTION_NAME_FILE = "items_potion"
PYLON_NAME_FILE = "items_pylon"
QUEST_FISH_NAME_FILE = "items_quest_fish"
SEEDS_NAME_FILE = "items_seeds"
SET_NAME_FILE = "set"
SHIELD_NAME_FILE = "items_shield"
STORAGE_NAME_FILE = "items_storage"
TOOL_NAME_FILE = "items_tool"
VANITY_NAME_FILE = "items_vanity"
WEAPON_NAME_FILE = "items_weapon"

# NPC subfiles labels
MAIN_NPC_SUBFILE_PREFIX = "npc_"
NPC_ENEMIES_NAME_FILE = "npc_enemy"
NPC_CRITTERS_NAME_FILE = "npc_critter"
NPC_TOWN_NAME_FILE = "npc_town"
NPC_BOSSES_NAME_FILE = "npc_boss"

# Image directories labels
IMAGE_DIR_BRICKS = "bricks_sprites/"
IMAGE_DIR_GEMS = "gems_sprites/"
IMAGE_DIR_LIGHT_PETS = "light_pets_sprites/"
IMAGE_DIR_ORES = "ores_sprites/"
IMAGE_DIR_PAINTINGS = "paintings_sprites/"
IMAGE_DIR_PYLON = "pylon_sprites/"
IMAGE_DIR_RARITY = "rarity_sprites/"
IMAGE_DIR_NPC = "npc_sprites/"

# Universal aliases for generalized items
nameSubstitutes = {
    "Any Wood": "Wood",
    "Any Iron Bar": "Iron Bar",
    "Any Pressure Plate": "Brown Pressure Plate",
    "Any Bird": "Bird",
    "Any Butterfly": "Julia Butterfly",
    "Any Jungle Bug": "Buggy",
    "Any Duck": "Duck",
    "Any Firefly": "Firefly",
    "Any Dragonfly": "Blue Dragonfly",
    "Any Scorpion": "Scorpion",
    "Any Snail": "Snail",
    "Any Sand": "Sand Block",
    "Any Squirrel": "Squirrel",
    "Green Jellyfish (bait)": "Green Jellyfish",
    "Blue Jellyfish (bait)": "Blue Jellyfish",
    "Pink Jellyfish (bait)": "Pink Jellyfish",
    "Any Fruit": "Apple",
    "Any Turtle": "Turtle",
    "Any Pylon": "Forest Pylon",
    "Princess Dress (Clothier)": "Princess Dress",
    "Bee Hive (item)": "Bee Hive",
    "Conveyor Belt": "Conveyor Belt (Clockwise)",
    "Logic Gates": "Logic Gate (AND)"
}

logging.basicConfig(format='%(asctime)s: %(message)s', filename=LOG_PATH + "scraping_errors.log", encoding='utf-8', level=logging.ERROR)

# Write/saves an image from a HTML scrap
def writeImage(imageSource, imagePath):
    imgOutput = requests.get(imageSource, stream=True)
    if imgOutput.ok:
        with open(imagePath, "wb+") as handler:
            for block in imgOutput.iter_content(1024):
                if not block:
                    break
                handler.write(block)
        return FOUND
    else:
        return NOT_FOUND

# Removes every null field inside a dict
def removeEmptyFields(dataDict):
    dictEmptyKeys = []
    for key in dataDict.keys():
        if dataDict[key] == "":
            dictEmptyKeys.append(key)
    for key in dictEmptyKeys:
        del(dataDict[key])
    return dataDict

def sortListOfDictsByKey(dataList, key):
    return sorted(dataList, key=lambda x: int(operator.itemgetter(key)(x)))

# Finds every column index of a table based on a list with each column label.
def getTableColumns(tableHeadRow, scrappingData):
    indexDict = {}
    for data in scrappingData:
        indexDict[data] = NOT_FOUND
        for column in tableHeadRow:
            if re.search("^" + data, column.text):
                indexDict[data] = int(tableHeadRow.index(column))
    return indexDict

# Get only the desktop info from a row that also contains other versions infos
def get_desktop_text_linear(row):
    eicos = row.find_all("span", class_="eico")
    if eicos:
        count = 0
        countReturn = 0
        for eico in eicos:
            if re.search("Desktop", eico.find("img")["alt"]):
                countReturn = count
                break
            count += 1
        return row.td.text.split("/")[countReturn].rstrip()
    else:
        return row.td.text

# First case for scraping data
def scraping_case_1(statistic):
    try:
        return statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
    except:
        return None

# Second case for scraping data
def scraping_case_2(statistic):
    try:
        return BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.rstrip()
    except:
        return None

# Third case for scraping data
def scraping_case_3(statistic):
    try:
        return statistic.td.text.rstrip().replace("  ", " ")
    except:
        return None

# Fourth case for scraping data
def scraping_case_4(statistic):
    try:
        return statistic.td.text.split(" ")[0].rstrip()
    except:
        return None

# Fifth case for scraping data
def scraping_case_5(statistic):
    try:
        return statistic.td.span["title"]
    except:
        return None

# Rarity case for scraping data
def scraping_rarity(statistic):
    try:
        if statistic.td.span:
            if (re.search("-*\d+", statistic.td.span.a["title"])):
                return (re.search("-*\d+", statistic.td.span.a["title"])).group()
            else:
                return RARITY_TIER[statistic.td.span.a["title"].split(": ")[-1]]
        else:
            return statistic.td.text.rstrip()
    except:
        return None

# Returns "Yes" or "No" info from infobox
def scraping_yes_no(statistic):
    try:
        if statistic.td.span["class"][0] == "t-yes":
            return "Yes"
        elif statistic.td.span["class"][0] == "t-no":
            return  "No"
        else:
            return None
    except:
        return None

def scraping_get_desktop(statistic):
    try:
        return get_desktop_text_linear(statistic).encode("ascii", "replace").decode().replace("?", " ").rstrip()
    except:
        return None

def scraping_power(statistic):
    try:
        return statistic.text[1:].split(" ", 1)[0]
    except:
        return None

# Dict with functions to get all general attributes on any infobox
GET_STATISTIC = {
    SCRAPING_USE_TIME: lambda statistic: scraping_case_1(statistic),
    SCRAPING_RARITY: lambda statistic: scraping_rarity(statistic),
    SCRAPING_PLACEABLE: lambda statistic: scraping_yes_no(statistic),
    SCRAPING_MAX_LIFE: lambda statistic: scraping_case_2(statistic),
    SCRAPING_RESEARCH: lambda statistic: scraping_case_3(statistic),
    SCRAPING_TOOL_SPEED: lambda statistic: scraping_case_4(statistic),
    SCRAPING_DAMAGE: lambda statistic: scraping_case_4(statistic),
    SCRAPING_VELOCITY: lambda statistic: scraping_case_4(statistic),
    SCRAPING_KNOCKBACK: lambda statistic: scraping_case_1(statistic),
    SCRAPING_AVAILABLE: lambda statistic: scraping_case_3(statistic),
    SCRAPING_EFFECT: lambda statistic: scraping_case_2(statistic),
    SCRAPING_SELL: lambda statistic: scraping_case_5(statistic),
    SCRAPING_BASE_VELOCITY: lambda statistic: scraping_case_3(statistic),
    SCRAPING_VELOCITY_MULTIPLIER: lambda statistic: scraping_case_1(statistic),
    SCRAPING_MANA: lambda statistic: scraping_case_1(statistic),
    SCRAPING_CRITICAL_CHANCE: lambda statistic: scraping_case_1(statistic),
    SCRAPING_DEFENSE: lambda statistic: scraping_case_4(statistic),
    SCRAPING_BODY_SLOT: lambda statistic: scraping_case_3(statistic),
    SCRAPING_BONUS: lambda statistic: scraping_case_3(statistic),
    SCRAPING_MAX_STACK: lambda statistic: scraping_case_1(statistic),
    SCRAPING_CONSUMABLE: lambda statistic: scraping_yes_no(statistic),
    SCRAPING_PICKAXE_POWER_REQUIRED: lambda statistic: scraping_get_desktop(statistic),
    SCRAPING_PICKAXE_POWER: lambda statistic: scraping_power(statistic),
    SCRAPING_HAMMER_POWER: lambda statistic: scraping_power(statistic),
    SCRAPING_AXE_POWER: lambda statistic: scraping_power(statistic)
}

#get statistics for every table with infobox class
def get_statistics(tableBox: Any, itemInstance: dict = {}, usedIn: str = "", isArmor: bool = False):

    jsonDict = {}

    # Get item id and name
    if itemInstance:
        jsonDict[SCRAPING_ITEM_ID] = itemInstance[SCRAPING_ID]
        jsonDict[SCRAPING_NAME] = itemInstance[SCRAPING_NAME]
    else:
        jsonDict[SCRAPING_ITEM_ID] = tableBox.find("div", class_="section ids").find("li").b.text
        jsonDict[SCRAPING_NAME] = tableBox.find("div", class_="title").text

    statistics = tableBox.find("div", class_="section statistics").find_all("tr")

    #Get all common statistics from infobox
    for statistic in statistics:
        # Get tooltip separated because it depends on a optional parameter
        if statistic.th.text == SCRAPING_TOOLTIP:
            if isArmor:
                jsonDict[SCRAPING_TOOLTIP] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.split("/")[0].rstrip()
            else:
                jsonDict[SCRAPING_TOOLTIP] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.encode("ascii", "ignore").decode().rstrip()
        # Get any other statistic
        else:
            if statistic.th.text in GET_STATISTIC.keys():
                jsonDict[statistic.th.text] = GET_STATISTIC[statistic.th.text](statistic)
                if not jsonDict[statistic.th.text]:
                    logging.exception("ERROR: Couldn't get attribute '{}' on: item '{}'.\n".format(statistic.th.text, jsonDict[SCRAPING_NAME]))

    # Add multiplier text format
    if SCRAPING_VELOCITY_MULTIPLIER in jsonDict.keys():
        jsonDict[SCRAPING_VELOCITY_MULTIPLIER] += "x"

    # Get toolpower for tools json
    toolPower = tableBox.find("ul", class_="toolpower")
    if toolPower:
        powerList = toolPower.find_all("li")
        for powerType in powerList:
            jsonDict[powerType["title"]] = GET_STATISTIC[powerType["title"]](powerType)
            if not jsonDict[powerType["title"]]:
                logging.exception("ERROR: Couldn't get attribute '{}' on: item '{}'.\n".format(powerType["title"], jsonDict[SCRAPING_NAME]))

    # Get buffs from buffable items
    if tableBox.find("div", class_="section buff"):
        tableBuffs = tableBox.find_all("tr")
        for tableBuff in tableBuffs:
            if tableBuff.th.text == SCRAPING_BUFF:
                jsonDict[SCRAPING_BUFF] = tableBuff.find("img")["alt"]
            elif tableBuff.th.text == SCRAPING_BUFF_TOOLTIP:
                if tableBuff.find("a", title="Expert Mode"):
                    BuffsTexts = BeautifulSoup(str(tableBuff.i).replace("<br/>", "."), 'html.parser').text.encode("ascii", "ignore").decode().split(".")
                    jsonDict[SCRAPING_BUFF_TOOLTIP] = BuffsTexts[0].rstrip() + " (Normal Mode). " + BuffsTexts[1].rstrip() + " (Expert Mode)."
                else:
                    jsonDict[SCRAPING_BUFF_TOOLTIP] = tableBuff.i.text
            elif tableBuff.th.text == SCRAPING_DURATION:
                jsonDict[SCRAPING_DURATION] = get_desktop_text_linear(tableBuff).encode("ascii", "replace").decode().replace("?", " ").rstrip()
    
    # Get debuffs from debuffable items
    if tableBox.find("div", class_="section debuff"):
        tableBuffs = tableBox.find_all("tr")
        for tableBuff in tableBuffs:
            if tableBuff.th.text == SCRAPING_DEBUFF:
                jsonDict[SCRAPING_DEBUFF] = tableBuff.find("img")["alt"]
            elif tableBuff.th.text == SCRAPING_DEBUFF_TOOLTIP:
                if tableBuff.find("a", title="Expert Mode"):
                    BuffsTexts = BeautifulSoup(str(tableBuff.i).replace("<br/>", "."), 'html.parser').text.encode("ascii", "ignore").decode().split(".")
                    jsonDict[SCRAPING_DEBUFF_TOOLTIP] = BuffsTexts[0].rstrip() + " (Normal Mode). " + BuffsTexts[1].rstrip() + " (Expert Mode)."
                else:
                    jsonDict[SCRAPING_DEBUFF_TOOLTIP] = tableBuff.i.text
            elif tableBuff.th.text == SCRAPING_DURATION:
                jsonDict[SCRAPING_DURATION] = get_desktop_text_linear(tableBuff).encode("ascii", "replace").decode().replace("?", " ").rstrip()

    # For gun category
    if usedIn:
        jsonDict[SCRAPING_USED_IN] = usedIn
    
    # For armor category
    if isArmor and itemInstance:
        jsonDict[SCRAPING_SET_ID] = itemInstance[SCRAPING_SET_ID]
    
    # Assign void dict to source dict
    jsonDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
    return jsonDict
