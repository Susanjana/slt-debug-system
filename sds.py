#!/usr/bin/env python
# -*- coding: utf-8; -*-


import os
import re
import sys
import time
import datetime
import threading
import logging

import remote
import debuglog

# Setting logging level
logging.basicConfig(level=logging.INFO)


def show_done(ip):
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++  %s Done  ++++++++++++++++++++++++++++++++++++++++++++\033[0m" % ip)
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")


def modify_cgminer(option):
    flag = 0
    path = 'cgminer'

    with open(path, 'r') as f:
        lines = f.readlines()

    with open(path, 'w') as f:
        for line in lines:
            if 'more_options' in line:
                tmp = list(line.split('\''))[1]
                line = line.replace(tmp, option)
                f.write(line)
                flag = 1
            elif line == '\n':
                continue
            else:
                f.write(line)

    if (flag == 0):
        with open(path, 'a') as f:
            f.write('\t' + 'option more_options ' + '\''+ option + '\'' + '\n')


def setup(ip):
    ip_dirs = "result" + "-" + ip
    os.mkdir(ip_dirs)

    # Remote get cgminer file
    remote.remote_scp(ip, 'receive')
    time.sleep(3)

    # Create csv file
    os.system("echo Freq, Volt_level, GHSmm, Temp, TMax, WU, GHsav, Iout, Power, DH, Power/GHsav, DNA, Options \
                >> ./%s/result-miner.csv" % ip_dirs)

    # Get debuglog
    for option in options:
        # Modify cgminer file
        modify_cgminer(option)
        time.sleep(5)

        # Send cgminer file to remote
        remote.remote_scp(ip, 'send')
        time.sleep(3)

        # Restart cgminer
        remote.remote_cmd(ip, '/etc/init.d/cgminer', 'restart')
        time.sleep(time)

        # Debuglog messages
        debuglog.debuglog_files(ip_dirs, ip)
        freq = list(config.config['options'])[index].split()[1]
        volt_level = list(config.config['options'])[index].split()[3]
        date = datetime.datetime.now().strftime('%Y.%m%d.%H%M%S')
        subdirs = ip + '-' + date + '-' + freq + '-' + volt_level
        os.mkdir('./%s/%s' % (ip_dirs, subdirs))
        # Freq, Volt_level and more_options
        os.system("echo %s > ./%s/freq.log" % (freq, ip_dirs))
        os.system("echo %s > ./%s/volt.log" % (volt_level, ip_dirs))
        os.system("echo %s > ./%s/options.log" % (tmp.strip("'"), ip_dirs))
        # Grep debuglog datas
        os.system("cat ./%s/estats.log | grep '\[MM ID' > ./%s/%s/CGMiner_Debug.log" % (ip_dirs, ip_dirs, subdirs))
        os.system("cat ./%s/edevs.log | grep -v Reply  > ./%s/%s/CGMiner_Edevs.log" % (ip_dirs, ip_dirs, subdirs))
        os.system("cat ./%s/summary.log | grep -v Reply  > ./%s/%s/CGMiner_Summary.log" % (ip_dirs, ip_dirs, subdirs))

        debuglog.read_debuglog(ip_dirs, subdirs, 'ghsmm')
        debuglog.read_debuglog(ip_dirs, subdirs, 'temp')
        debuglog.read_debuglog(ip_dirs, subdirs, 'tmax')
        debuglog.read_debuglog(ip_dirs, subdirs, 'wu')
        debuglog.read_debuglog(ip_dirs, subdirs, 'dh')
        debuglog.read_debuglog(ip_dirs, subdirs, 'power')
        debuglog.read_debuglog(ip_dirs, subdirs, 'iout')
        debuglog.read_dna(ip_dirs, subdirs)
        debuglog.gen_ghsav(ip_dirs)
        debuglog.power_ghsav(ip_dirs)
        debuglog.result_files(ip_dirs)

    # Remove cgminer file
    os.system("rm ./%s/cgminer" % ip_dirs)
    show_done(ip)


def read_config():
    ''' Read time, ip, options form slt-options.conf '''

    ips = []
    options = []

    path = 'slt-options.conf'
    option_flag = 0

    with open(path) as f:
        for line in f:
            if line == '\n':
                continue

            tmp = re.search('^\s*#', line)
            if tmp:
                option_flag += 1
                continue

            if option_flag == 1:
                time = line.strip()
            elif option_flag == 2:
                ips.append(line.strip())
            elif option_flag == 3:
                options.append(line.strip())

    return time, ips, options


if __name__ == '__main__':
    threads = []
    global options
    global time

    # Read Config file
    time, ips, options = read_config()
    logging.debug("time: %s", time)
    logging.debug("ips: %s", str(ips))
    logging.debug("options: %s", str(options))

    # According to ip number, creating threads
    for line in ips:
        thr = threading.Thread(target=setup, args=(line,))
        thr.start()
        threads.append(thr)

    for thr in threads:
        thr.join()

    os.system("rm *.pyc")
