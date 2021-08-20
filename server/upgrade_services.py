# SwUpdate/RAUC
import dbus
import os
import threading
import json

import swupdate_wss_monitoring
from swupdate_wss_monitoring import swUpdateWssMonitoring
from swupdate_client_wrapper import swUpdateClientWrapper

upgrader_types = ['RAUC', 'swupdate', 'none']
 
class CommonUpdater:
    def __init__(self):
        self.rauc = RaucUpdater()
        self.swu = SwUpdateUpdater()
        self.upd_type ='none'
        self.sw_bundle = None
        
        if self.rauc.getState() != 'notSupported':
            print ("RAUC is supported")
            self.upd_type = 'RAUC'
        elif self.swu.getState() != 'notSupported':
            self.upd_type = 'swupdate'
        else:
            print("There is no update system ar available on the board")
            
    def storeBundleFileName(self, filename):
        if self.sw_bundle is not None:
            print("WARNING. The file with upgrade is not empty.", self.sw_bundle, " will be owewritten by new one", filename)
        self.sw_bundle = filename
        
        if self.upd_type == 'RAUC':
            return self.rauc.onFileUploaded()
        elif self.upd_type == 'swupdate':
            return self.swu.onFileUploaded()
        else:
            return "not supported"
        return "not supported"
        
    def installBundle(self):
        if self.sw_bundle is None:
            return {'status' : 'NotFound'}
        
        file_exists = os.path.exists(self.sw_bundle)
        if file_exists:
            self.installBundleImpl(self.sw_bundle)
            return {'status' : 'OK'}
        else:
            return {'status' : 'NotFound'}
                        
    def installBundleImpl(self, filename):
        if self.upd_type == 'RAUC':
            self.rauc.dbus_InstallBundle(filename)
        elif self.upd_type == 'swupdate':
            self.swu.installBundle(filename)
        else:
            str = "No suported upgrade type {}".format(self.upd_type)
            print(str)
        
    def getState(self):
        print("===================== CommonUpdater getState ")
        if self.upd_type == 'RAUC':
            return self.rauc.getState()
        elif self.upd_type == 'swupdate':
            # do nothing at the moment
            return self.swu.getState()
        else:
            str = "No suported upgrade type {}".format(self.upd_type)
            print(str)
            return "Incorrect request"
    
    def rebootBoard(self):
        if self.upd_type == 'RAUC':
            self.rauc.rebootBoard()
        elif self.upd_type == 'swupdate':
            self.swu.rebootBoard()
        else:
            return "Incorrect request"
        
    def getOperation(self):
        if self.upd_type == 'RAUC':
            return self.rauc.dbus_getOperation()
        return "not supported"
            
    def getLastError(self):
        if self.upd_type == 'RAUC':
            return self.dbus_getLastError()
        elif self.upd_type == 'swupdate':
            return self.swu.getLastError()
        else:
            return "not supported"
        return "not supported"
    
    def getUpgradeSystemType(self):
        return self.upd_type
    
    
        
class UpgradeToolType:

    states = ['initial', 'active', 'upgrFileUploaded', 'upgrInStarted', 'upgrSuccefull', 'upgrInProgress', 'upgrFailed', 'notSupported']
    
    def __init__(self, type):
        self.type = type
        self.state = 'initial'
        
    def getState(self):
        return self.state
    
    def isSupported(self):
        return self.state != 'notSupported'
        

class SwUpdateUpdater(UpgradeToolType):
    
    def __init__(self):
        UpgradeToolType('swupdate')
        rc = self.checkSwUpdate()
        if rc:
            self.state = 'active'
            #self.ws = swUpdateWssMonitoring(self.onWssMessage)
            self._lock = threading.Lock()
            self.last_error = None
        else:
            self.state = 'notSupported'
            
        self.file_name = None
       
    def onFileUploaded(self):
        self.state = 'upgrFileUploaded'
              
    def onWssMessage(self, msg):
        return True
    
        # NO used at the moments
        '''
        json_data = json.loads(msg)
        str = json_data["text"]
        print('================888888888888888')
        print(msg)    
       # with self._lock:
        update_started_str = "Software Update started !"
        incorrect_image = "Image invalid or corrupted"
        upgrade_in_progress = "Installation in progress"
        upgrade_finished = "SWUPDATE successful !"
        
        if str.startswith( update_started_str ):
            self.state = 'upgrInStarted'
            self.last_error = None
        elif str.startswith( incorrect_image ):
            self.state  = 'upgrFailed'
            self.last_error = str
        elif  str.startswith( upgrade_in_progress):
            self.state  = 'upgrInProgress'
            self.last_error = str
        elif  str.startswith( upgrade_finished):
            self.state  = 'upgrSuccefull'
            self.last_error = str
        else:
             print(" ================ Not supported message", str)
             '''
        
    def checkSwUpdate(self):        
        # from whichcraft import which
        from shutil import which

        return which('swupdate') is not None
    
    def getLastError(self):
        return self.last_error
    
    def getState(self):
        print("SWUPDATED self state -------------------------")
        with self._lock:
            return self.state
    
    def installBundle(self, file_name):
        self.state  = 'upgrInProgress'
        
        self.file_name = file_name
        swUpdateClientWrapper(self.file_name, self.onInstallationFinish)
        #str_fn = "swupdate-client " + self.file_name
        #output = os.popen(str_fn).read()
        #print("------------------- +++++++++++++")
        #print(output)
        #print("------------------- +++++++++++++")
        
        #(' ' + w + ' ') in (' ' + s + ' ')
        
    def onInstallationFinish(self, var):
        #var = os.system(str_fn)
        print("------------------- +++++++++++++")
        print(var)
        print("------------------- +++++++++++++")
        if var == 0 :
            print("Upgrade is succesfull")
            self.state  = 'upgrSuccefull'
        else:
            print("Upgrade is failed")
            self.state  = 'upgrFailed'
            
    def rebootBoard(self):
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported'
        # TODO check that activatetion is possible
        os.system("shutdown -r")
        return "the board will be rebooted in 1 minute"    

# https://rauc.readthedocs.io/en/latest/reference.html#gdbus-method-de-pengutronix-rauc-installer-installbundle
class RaucUpdater(UpgradeToolType):

    dbus_ap = "de.pengutronix.rauc"

    def __init__(self):
        UpgradeToolType('RAUC')
        self.debug = 0
        self.bus = dbus.SystemBus()
        
#        print "Debug flag is " + str(self.debug)
        
        if not self.debug:
            try:
                self.object = self.bus.get_object('de.pengutronix.rauc', '/')
                self.state = 'active'
            except dbus.DBusException as e:
                str_tmp = "Exception created {}".format(str(e))
                print(str_tmp)
                self.state = 'notSupported'
                return
                
                
            self.properties_interface = dbus.Interface( self.object , dbus_interface="org.freedesktop.DBus.Properties" )
            self.rauc_intf_name = 'de.pengutronix.rauc.Installer';
            self.function_interface = dbus.Interface( self.object, dbus_interface = self.rauc_intf_name)
    
    def onFileUploaded(self):
        self.state = 'upgrFileUploaded'
        
    def notSupportedMessage(self):
        print("RAUC is not supported on the board. no actions")
        
    def rauc_getProperty(self , property_name):   
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported';
        return self.properties_interface.Get(self.rauc_intf_name, property_name)

    # file name - full path to the file location
    def  dbus_InstallBundle(self, file_name):
        if self.state == 'notSupported':
            notSupportedMessage()
            return 'notsupported';
        
        print("-------------FILE:", file_name)
        self.function_interface.InstallBundle(str(file_name), dbus.Dictionary({dbus.String("ignore-compatible") : dbus.Boolean(0)}))
        self.state  = 'upgrInProgress'

    def getState(self):
        rc = self.dbus_getProgress()
        print("progress status:++++++++++ : ", rc)
        
        if rc.startswith("Installing failed"):
            self.state  = 'upgrFailed'
        elif rc.startswith("Installing done"):
            self.state  = 'upgrSuccefull'   
            
        return self.state        
        
    def dbus_getProgress(self):
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported';
        rc = self.rauc_getProperty("Progress")
        #(percentage, message, nesting depth)
        return rc[1]
        #r_str = "Percentage: [{}], meesage: [{}], nesting depth: [{}]".format(str(rc[0]), str(rc[1]), str(rc[2]))
        
        return r_str
    
    def dbus_getOperation(self):
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported';
        rc = self.rauc_getProperty("Operation")
        r_str = "Current operation: [{}]".format(str(rc))
        return r_str
        
    def dbus_getLastError(self):
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported';
        return "Last error [{}]".format(str(self.rauc_getProperty("LastError")))
    
    def rebootBoard(self):
        if self.state == 'notSupported':
            self.notSupportedMessage()
            return 'notsupported';
        # TODO check that activatetion is possible
        os.system("shutdown -r")
        return "the board will be rebooted in 1 minute"
    
    def activateSwOnSlot(self, slot):
        # add set for particular slot
        self.activated = True
        
        
