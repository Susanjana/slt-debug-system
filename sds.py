#!/usr/bin/env python

import subprocess
import logging
import time
import os
import config
import remote

logging.basicConfig(level=logging.DEBUG)

# Create result.csv
#subprocess.call("echo 'Freq,Voltage,GHSmm,Temp,TMax,WU,GHSav,DH,Iout,Vo,Power,Power/GHSav,Options' > miner-result.csv", shell=True)

# Get time
times = config.config['time']
logging.debug('times = %s', times)

# Get ip
ip = config.config['ip']
logging.debug('ip = %s', ip)

# Get options
options = config.config['options']
logging.debug(options)

# Create directory
dirip = "result" + "-" + ip
logging.debug('dir = %s', dirip)
#os.makedirs(dirip)

# Remote getting cgminer file
remote.remote_scp(ip, 0)
time.sleep(3)

# Config /etc/config/cgminer and restart cgminer, Get Miner debug logs
for i in options:
    print(i)

'''
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
    rm debug.log

    sleep 1
    ./ssh-login.exp $IP cgminer-api estats estats.log > /dev/null
    ./ssh-login.exp $IP cgminer-api edevs edevs.log > /dev/null
    ./ssh-login.exp $IP cgminer-api summary summary.log > /dev/null

    # Read CGMiner Log
    ./debuglog.sh $tmp
done
'''

# Remove cgminer file
os.system("rm ./cgminer")

print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
print("\033[1;32m++++++++++++++++++++++++++++++  Done   ++++++++++++++++++++++++++++++\033[0m")
print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
