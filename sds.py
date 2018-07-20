#!/usr/bin/env python

import subprocess
import logging
import time
import os

logging.basicConfig(level=logging.DEBUG)

# Create result.csv
#subprocess.call("echo 'Freq,Voltage,GHSmm,Temp,TMax,WU,GHSav,DH,Iout,Vo,Power,Power/GHSav,Options' > miner-result.csv", shell=True)

# Get ip
path = 'slt-options.conf'
with open(path, 'r') as f:
    tmp = list(f.readlines())
    tmp = tmp[2].split()
    ip = tmp[1]
logging.debug('ip = %s', ip)

# Get time
with open(path, 'r') as f:
    tmp = list(f.readlines())
    tmp = tmp[0].split()
    time = tmp[1]
logging.debug('time = %s', time)

# Remote getting cgminer file
'''
./scp-login.exp $IP 0 > /dev/null
time.sleep(3)
'''

# Create directory
dirip = "result" + "-" + ip
logging.debug('dir = %s', dirip)
os.makedirs(dirip)

'''
# Config /etc/config/cgminer and restart cgminer, Get Miner debug logs
cat slt-options.conf | grep avalon |  while read tmp
do
    more_options=`cat cgminer | grep more_options`
    if [ "$more_options" == "" ]; then
        echo "option more_options" >> cgminer
    fi

    more_options=`cat cgminer | grep more_options`
    sed -i "s/$more_options/	option more_options '$tmp'/g" cgminer

    # Cp cgminer to /etc/config
    ./scp-login.exp $IP 1
    sleep 3

    # CGMiner restart
    ./ssh-login.exp $IP /etc/init.d/cgminer restart > /dev/null
    sleep $TIME

    ./ssh-login.exp $IP cgminer-api debug debug.log > /dev/null
    debug=`cat debug.log | grep '\[Debug\] => true' | wc -l`
    if [ $debug -eq 0 ]; then
        # SSH no password
        ./ssh-login.exp $IP cgminer-api "debug\|D" > /dev/null
    fi

    sleep 1
    ./ssh-login.exp $IP cgminer-api estats estats.log > /dev/null
    ./ssh-login.exp $IP cgminer-api edevs edevs.log > /dev/null
    ./ssh-login.exp $IP cgminer-api summary summary.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $tmp
done

# Remove cgminer file
rm cgminer
rm debug.log

echo -e "\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m"
echo -e "\033[1;32m++++++++++++++++++++++++++++++  Done   ++++++++++++++++++++++++++++++\033[0m"
echo -e "\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m"
'''
