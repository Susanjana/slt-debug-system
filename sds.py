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

# Create directory
#dirip = "result" + "-" + ip
#logging.debug('dir = %s', dirip)
#os.makedirs(dirip)

def get_time():
    return config.config['time']

def get_ip():
    return config.config['ip']

def get_options():
    return config.config['options']

if __name__ == '__main__':
    times = get_time()
    logging.debug('times = %s', times)

    ip = get_ip()
    logging.debug('ip = %s', ip)

    options = get_options()
    logging.debug(options)

    # Remote getting cgminer file
    remote.remote_scp(ip, 0)
    time.sleep(3)

    for tmp in options:
        if (not os.system('cat cgminer | grep more_option')):
            os.system('more_options=`cat cgminer | grep more_options`; sed -i "s/$more_options/        option more_options     %s/g" cgminer' % tmp)
        else:
            os.system("echo '       option more_options %s' >> cgminer" % tmp)
        time.sleep(5)

        # Send cgminer file to remote
        remote.remote_scp(ip, 1)
        time.sleep(3)

'''
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
#os.system("rm ./cgminer")

print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
print("\033[1;32m++++++++++++++++++++++++++++++  Done   ++++++++++++++++++++++++++++++\033[0m")
print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
