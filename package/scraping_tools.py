import requests
import re
from bs4 import BeautifulSoup
import operator
import os

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
    "Any Bug": "Buggy",
    "Any Duck": "Duck",
    "Any Firefly": "Firefly",
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
    "Conveyor Belt": "Conveyor Belt (Clockwise)",
    "Logic Gates": "Logic Gate (AND)"
}

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

#função do urso
#get statistics for every table with infobox class
def get_statistics(tableBox, itemInstance = {}, usedIn = "", isArmor = False):

    jsonDict = {}
    #Check if optional parameter was given
    if itemInstance:
        jsonDict[SCRAPING_ITEM_ID] = itemInstance[SCRAPING_ID]
        jsonDict[SCRAPING_NAME] = itemInstance[SCRAPING_NAME]
    else:
        jsonDict[SCRAPING_ITEM_ID] = tableBox.find("div", class_="section ids").find("li").b.text
        jsonDict[SCRAPING_NAME] = tableBox.find("div", class_="title").text

    statistics = tableBox.find("div", class_="section statistics").find_all("tr")
    for statistic in statistics:
        if statistic.th.text == SCRAPING_USE_TIME:
            jsonDict[SCRAPING_USE_TIME] = statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_RARITY:
            if statistic.td.span:
                if (re.search("-*\d+", statistic.td.span.a["title"])):
                    jsonDict[SCRAPING_RARITY] = (re.search("-*\d+", statistic.td.span.a["title"])).group()
                else:
                    jsonDict[SCRAPING_RARITY] = RARITY_TIER[statistic.td.span.a["title"].split(": ")[-1]]
            else:
                jsonDict[SCRAPING_RARITY] = statistic.td.text.rstrip()
        elif statistic.th.text == SCRAPING_PLACEABLE:
            if statistic.td.span["class"][0] == "t-yes":
                jsonDict[SCRAPING_PLACEABLE] = "Yes"
            elif statistic.td.span["class"][0] == "t-no":
                jsonDict[SCRAPING_PLACEABLE] = "No"
        elif statistic.th.text == SCRAPING_MAX_LIFE:
            jsonDict[SCRAPING_MAX_LIFE] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.rstrip()
        elif statistic.th.text == SCRAPING_RESEARCH:
            jsonDict[SCRAPING_RESEARCH] = statistic.td.text.rstrip()
        elif statistic.th.text == SCRAPING_TOOL_SPEED:
            jsonDict[SCRAPING_TOOL_SPEED] = statistic.td.text.split(" ", 1)[0]
        elif statistic.th.text == SCRAPING_DAMAGE:
            jsonDict[SCRAPING_DAMAGE] = statistic.td.text.split(' ')[0].rstrip()
        elif statistic.th.text == SCRAPING_VELOCITY:
            jsonDict[SCRAPING_VELOCITY] = statistic.td.text.split(' ')[0].rstrip()
        elif statistic.th.text == SCRAPING_KNOCKBACK:
            jsonDict[SCRAPING_KNOCKBACK] = statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_AVAILABLE:
            jsonDict[SCRAPING_AVAILABLE] = (statistic.td.text.rstrip()).replace("  ", " ")
        elif statistic.th.text == SCRAPING_EFFECT:
            jsonDict[SCRAPING_EFFECT] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.rstrip()
        elif statistic.th.text == SCRAPING_TOOLTIP:
            if isArmor:
                jsonDict[SCRAPING_TOOLTIP] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.split("/")[0].rstrip()
            else:
                jsonDict[SCRAPING_TOOLTIP] = BeautifulSoup(str(statistic.td).replace("<br/>", ". "), 'html.parser').text.encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_SELL:
            jsonDict[SCRAPING_SELL] = statistic.td.span["title"]
        elif statistic.th.text == SCRAPING_BASE_VELOCITY:
            jsonDict[SCRAPING_BASE_VELOCITY] = statistic.td.text.rstrip()
        elif statistic.th.text == SCRAPING_VELOCITY_MULTIPLIER:
            jsonDict[SCRAPING_VELOCITY_MULTIPLIER] = statistic.td.text.encode("ascii", "ignore").decode().rstrip() + "x"
        elif statistic.th.text == SCRAPING_MANA:
            jsonDict[SCRAPING_MANA] = statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_CRITICAL_CHANCE:
            jsonDict[SCRAPING_CRITICAL_CHANCE] = statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_DEFENSE:
            jsonDict[SCRAPING_DEFENSE] = statistic.td.text.split(" ")[0]
        elif statistic.th.text == SCRAPING_BODY_SLOT:
            jsonDict[SCRAPING_BODY_SLOT] = statistic.td.text
        elif statistic.th.text == SCRAPING_BONUS:
            jsonDict[SCRAPING_BONUS] = statistic.td.text
        elif statistic.th.text == SCRAPING_MAX_STACK:
            jsonDict[SCRAPING_MAX_STACK] = statistic.td.text.split("/")[0].encode("ascii", "ignore").decode().rstrip()
        elif statistic.th.text == SCRAPING_CONSUMABLE:
            if statistic.td.span["class"] == "t-yes":
                jsonDict[SCRAPING_CONSUMABLE] = "Yes"
            elif statistic.td.span["class"] == "t-no":
                jsonDict[SCRAPING_CONSUMABLE] = "No"

    #get toolpower for tools json
    toolPower = tableBox.find("ul", class_="toolpower")
    if toolPower:
        powerList = toolPower.find_all("li")
        for powerType in powerList:
            if(powerType["title"] == SCRAPING_PICKAXE_POWER):
                jsonDict[SCRAPING_PICKAXE_POWER] = powerType.text[1:].split(" ", 1)[0]
            elif(powerType["title"] == SCRAPING_HAMMER_POWER):
                jsonDict[SCRAPING_HAMMER_POWER] = powerType.text[1:].split(" ", 1)[0]
            elif(powerType["title"] == SCRAPING_AXE_POWER):
                jsonDict[SCRAPING_AXE_POWER] = powerType.text[1:].split(" ", 1)[0]
    #get buffs
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
    #get debuffs
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
    #Check if optional parameter was given
    if usedIn:
        jsonDict[SCRAPING_USED_IN] = usedIn
    if isArmor and itemInstance:
        jsonDict[SCRAPING_SET_ID] = itemInstance[SCRAPING_SET_ID]
    jsonDict[SCRAPING_SOURCE] = SOURCE_SOURCES_DICT
    return jsonDict
