# Run this to get all scraping data from wiki (might take a long time)

import os
import re
# Load 3-level parent directories
from importlib import import_module
import path_manager
if __name__ == '__main__' and __package__ == None:
    __package__ = path_manager.importParents(level=3)
    import_module(__package__)

# Setting the root directory as working directory for Linux systems
from platform import system
from pathlib import Path
import logging
import os
systemOS = system()
if systemOS == "Linux":
    os.chdir("../../")

from ..package.log_manager import *

logging.basicConfig(format='%(asctime)s: %(message)s', filename=LOG_PATH + "running_errors.log", encoding='utf-8')

CRAFTING_RECIPES_SCRAPING_NAME = "crafting_recipes_scraping.py"
ITEMS_DIR = "algorithms/items/"
NPC_DIR = "algorithms/npc/"

# Runs all items scraping
for file in os.listdir(ITEMS_DIR):
    if re.search("scraping", file) and file != CRAFTING_RECIPES_SCRAPING_NAME:
        try:
            logging.info("Starting to scrap data on '{}'...".format(file))
            os.system("python " + ITEMS_DIR + file)
        except:
            logging.exception("ERROR: There was an error when we tried to scrap data on '{}' file.".format(file))

# Runs all npcs scraping
for file in os.listdir(NPC_DIR):
    if re.search("scraping", file):
        try:
            logging.info("Starting to scrap data on '{}'...".format(file))
            os.system("python " + NPC_DIR + file)
        except:
            logging.exception("ERROR: There was an error when we tried to scrap data on '{}' file.".format(file))

# Get all crafting recipes
os.system("python " + ITEMS_DIR + CRAFTING_RECIPES_SCRAPING_NAME)

