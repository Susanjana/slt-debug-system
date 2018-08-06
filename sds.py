#!/usr/bin/env python


import logging
import time
import os
import config
import remote
import debuglog

# Config logging level
logging.basicConfig(level=logging.DEBUG)

def make_ip_dirs():
    ip_dirs = "result" + "-" + config.config['ip']
    logging.debug('ip dir = %s', ip_dirs)
    os.mkdirs(ip_dirs)

if __name__ == '__main__':
    make_ip_dirs()

    times = config.config['time']
    logging.debug('times = %s', times)

    ip = config.config['ip']
    logging.debug('ip = %s', ip)

    options = config.config['options']
    logging.debug('options = %s', options)

    # Remote getting cgminer file
    remote.remote_scp(ip, 0)
    time.sleep(3)

    for tmp in options:
        tmp = "'%s'" % tmp
        if (not os.system('cat cgminer | grep more_options')):
            os.system('more_options=`cat cgminer | grep more_options`; sed -i "s/$more_options/        option more_options     %s/g" cgminer' % tmp)
        else:
            os.system("echo '       option more_options %s' >> cgminer" % tmp)
        time.sleep(5)

        # Send cgminer file to remote
        remote.remote_scp(ip, 1)
        time.sleep(3)

        # Restart cgminer
        remote.remote_cmd(ip, 4)
        time.sleep(times)

        # Debuglog messages
        debuglog.debuglog_files()

    # Remove cgminer file
    os.system("rm ./cgminer")

    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++  Done  ++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
