#!/usr/bin/env python


import subprocess
import logging
import time
import os
import config
import remote

logging.basicConfig(level=logging.DEBUG)

def make_ip_dirs():
    global ip_dirs

    ip_dirs = "result" + "-" + config.config['ip']
    logging.debug('ip dir = %s', ip_dirs)
    os.makedirs(ip_dirs)

def get_time():
    return config.config['time']

def get_ip():
    return config.config['ip']

def get_options():
    return config.config['options']

def get_debuglog():
    datas = remote.remote_cmd(ip, 0)
    path = '%s/estats.log' % ip_dirs
    estats = open(path, 'w+')
    estats.write(str(datas))
    estats.close()
    time.sleep(1)

    datas = remote.remote_cmd(ip, 1)
    path = '%s/edevs.log' % ip_dirs
    edevs = open(path, 'w+')
    edevs.write(str(datas))
    edevs.close()

    datas = remote.remote_cmd(ip, 2)
    path = '%s/summary.log' % ip_dirs
    summary = open(path, 'w+')
    summary.write(str(datas))
    summary.close()

if __name__ == '__main__':
    make_ip_dirs()

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

        # Restart cgminer
        remote.remote_cmd(ip, 4)
        time.sleep(times)

        # Get debuglog messages
        get_debuglog()

    # Remove cgminer file
    os.system("rm ./cgminer")

    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++  Done  ++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
