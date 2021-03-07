from pathlib import Path
from io import IOBase
import os

# Log file informations
LOG_PATH = "data_scrapping_algorithms/logs/"
LOG_EXT = ".log"

LOG_FILE_FAILED = -1
LOG_FILE_NOT_OPEN = -2

def createLogFile(logName: str):
    if not os.path.exists(LOG_PATH):
        Path(LOG_PATH).mkdir(parents=True, exist_ok=True)
    logFilePath = LOG_PATH + logName.replace(" ", "_").lower() + LOG_EXT
    logFile = open(logFilePath, "w+")
    if logFile:
        print("Creating new log file for '" + logName + LOG_EXT + "' (" + logFile.name + ").")
        print("Log file is open. Be sure to close it using 'closeLogFile(logFile)' at the end of the execution.")
        logFile.write("Starting log file for '" + logName + LOG_EXT + "'.\n")
        return logFile
    else:
        print("Log file creation failed. Exiting with value -1 (LOG_FILE_FAILED).")
        return LOG_FILE_FAILED

def closeLogFile(logFile):
    if isinstance(logFile, IOBase):
        if not logFile.closed:
            print("File '" + logFile.name + "' closed successfully.")
            logFile.write("Exiting with value 0.")
            logFile.close()
            return 0
        else:
            print("File '" + logFile.name + "' not open. Exiting with value -2 (LOG_FILE_NOT_OPEN).")
            return LOG_FILE_NOT_OPEN
    else:
        print("Existing variable is not file object. Exiting with value -1 (LOG_FILE_FAILED).")
        return LOG_FILE_FAILED
