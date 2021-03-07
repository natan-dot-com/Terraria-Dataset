import threading
import math
from .log_manager import *
from pathlib import Path

LOG_FILE_NAME = "multithreading"
log = createLogFile(LOG_FILE_NAME)

class myThread (threading.Thread):
    def __init__(self, threadID, func, init, fin):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.init = init
        self.fin = fin
        self.func = func
    def run(self):
        print ("Starting Thread " + str(self.threadID) + " on indexes " + str(self.init) + " to " + str(self.fin))
        self.func(self.init, self.fin, self.threadID)
        log.write("Exiting Thread ({})\n".format(str(self.threadID)))
        print ("Exiting Thread " + str(self.threadID))

def start_threads_decorator(*args, **kwargs):

   def start_threads(func):
      indexes = []
      indexes.append(0)
      threads = []
      threads_number = int(kwargs["threads_number"])
      size = int(kwargs["size"])

      #Start Threads
      for i in range(threads_number):
         if i < threads_number-1:
            index = (i+1) * math.floor(size/threads_number)
         else:
            index = size
         indexes.append(index)
         threads.append(myThread((i+1), func, indexes[-2], indexes[-1]))
         threads[-1].start()
      
      #Join Threads
      for i in range(threads_number):
         threads[i].join()
         
      closeLogFile(log)
      return
   
   return start_threads
   
