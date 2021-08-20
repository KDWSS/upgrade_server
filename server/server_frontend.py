#!/usr/bin/python3 -u
import os
import upgrade_services
from upgrade_services import CommonUpdater

from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Response
from flask import jsonify

updEntity = CommonUpdater()

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['raucb', 'swu'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#GET api/v1/device - get device info
#POST api/v1/device/update-package - upload an artifact to device
#POST api/v1/device/update-package/apply
#GET  api/v1/device/update-package - get an artifact's metadata (upload status, etc)
#POST api/v1/device/reboot - reboot a device

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
           
@app.route('/api/v1/device')
def get_device_information():
    device_cfg = {
            'upgrade_type' : str(updEntity.getUpgradeSystemType())
        }
    #return "Hello"
    return jsonify(device_cfg)

@app.route('/api/v1/device/update-package', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if not allowed_file(file.filename):
            print("------------- FILE is not allowed")
            status_code = Response(status=406)
            return status_code
        
        if file and allowed_file(file.filename):
            print("------------- FILE is allowed")
            filename = secure_filename(file.filename)
            file_name_full = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_name_full)
            updEntity.storeBundleFileName(file_name_full)
            # updEntity.installBundle(file_name_full)
            str = "Uploaded [{}]".format(filename)
            
            #return filename
            return str
        
    status = {
        'state' : updEntity.getState(),
    }
    return jsonify(status)    
#        
#    return '''
#    <!doctype html>
#    <title>Upload new File</title>
#    <h1>Upload new File</h1>
#    <form action="" method=post enctype=multipart/form-data>
#      <p><input type=file name=file>
#        <input type=submit value=Upload>
#    </form>
#    '''

@app.route('/api/v1/device/update-package/apply', methods=['PUT'])
def install_upgrade_package():
    status = updEntity.installBundle()
    print (status)
    if status["status"] == 'OK' :
        return jsonify(status)
    else:
        return Response(status=404)
        

@app.route('/api/v1/device/reboot', methods=['PUT'])
def sw_activation():
    updEntity.rebootBoard()
    return str("Board will be rebooted")

#import netifaces as ni
#ni.ifaddresses('eth0')
#ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
#print ("Run server on ", ip)  

import socket
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

app.run(host=str(get_ip()))
