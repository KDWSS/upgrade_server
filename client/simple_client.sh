#!/bin/sh

# 1 - 10.10.10.3:8000
# 2 - file name

if [ $# -ne 2 ]; then
    echo "Usage: simple_client.sh <dest_ip>:<port> <path_to_sw_file>"
    exit 255
fi

if [ ! -f $2 ]; then
    echo "the provide file $2 doesn't exists"
    exit 255
fi

# upload the file to the board

echo "Upload file to the board"

#curl -F "file=@$1" -X POST http://$3/upload

status_code=$(curl -F "file=@$2"  -X POST http://$1/api/v1/device/update-package )

echo "========== $status_code"
# check that file downloaded:
file_name=$(echo $status_code | sed 's/^Uploaded \[\(.*\)\].*/\1/g')

if [ "$file_name" != "$(basename $2)" ]; then
    echo "Upload error"
    exit 1
fi

echo "========== ACTIVATE "
apply_status_code=$(curl -X PUT http://$1/api/v1/device/update-package/apply)
echo "========== $apply_status_code"
# check status:
if [ "$apply_status_code" != "{\"status\":\"OK\"}" ]; then
    echo "Activation error"
    exit 1
fi


state="installing"
while [ "$state" != "installed" ]; do
rc=$(curl --silent  http://$1/api/v1/device/update-package)
message=$(echo $rc | sed 's/^.*\:"\(.*\)".*/\1/g')

echo "Current state: $message"

if [ "upgrSuccefull" = "$message" ]; then 
    state="UPGRADE SUCCESFULL"
    break
fi

if [ "upgrFailed" = "$message" ]; then
    state="failed"
    echo "UPGRADE FAILED"
    exit 1
fi

echo "$rc"
sleep 1
done

while true; do
    read -p "Do you want to activate sw by reboot? y/n" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

rc=$(curl --silent  -X PUT http://$1/api/v1/device/reboot)
echo $rc
