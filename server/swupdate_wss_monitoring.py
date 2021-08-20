import websocket
import threading
from threading import Thread
try:
    import thread
except ImportError:
    import _thread as thread
import time

class swUpdateWssMonitoring():
    def __init__(self, main_on_message):
        #Thread.__init__(self)
        # websocket.enableTrace(True)
        self.running = False
        self.main_on_message = main_on_message
        
        print("+++++ Create web socket towards server")
        self.ws = websocket.WebSocketApp("ws://localhost:8080",
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)
        
        self.ws.on_open = self.on_open
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()
        
    def on_message(self, message):
        #print("----------------xxxxxxxxxxxxxxxx----------------------")
        #print("WSS MESSAGE", message)
        self.main_on_message(message)

    def on_error(self, error):
        print("WSS ERRRR", error)

    def on_close(self):
        print("### closed ###")
    
    def on_open(self):
        def run(*args):
           # for i in range(3):
           #     time.sleep(1)
           #     ws.send("Hello %d" % i)
            while True:
                pass
            print("swUpdateWssMonitoring terminating...")
            
        thread.start_new_thread(run, ())
