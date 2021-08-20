import os

import threading
from threading import Thread
try:
    import thread
except ImportError:
    import _thread as thread
import time

class swUpdateClientWrapper():
    def __init__(self, file_name, main_on_finish):
        self.file = file_name     
        self.on_finish = main_on_finish
        self.wst = threading.Thread(target=self.run)
        self.wst.daemon = False
        self.wst.start()
        
    def run(self):
        str_fn = "swupdate-client " + self.file
        var = os.system(str_fn)
        self.on_finish(var)
        
        