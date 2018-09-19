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
    ''' Show process Done'''

    print("\033[1;32m\n+++++++++++++++++++++++++++++++++++++++++++++  %s Done  +++++++++++++++++++++++++++++++++++++++++\n\033[0m" % ip)


def modify_cgminer(ip_dirs, option):
    ''' Modify cgminer more_options '''

    flag = 0
    path = ip_dirs + '/cgminer'

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
    ''' Get debuglog function '''

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
        modify_cgminer(ip_dirs, option)
        time.sleep(5)

        # Send cgminer file to remote
        remote.remote_scp(ip, 'send')
        time.sleep(3)

        # Restart cgminer
        remote.remote_cmd(ip, '/etc/init.d/cgminer', 'restart')
        time.sleep(int(times))

        # Debuglog messages
        debuglog.debuglog_files(ip_dirs, ip)
        freq = option.split()[1]
        volt_level = option.split()[3]
        date = datetime.datetime.now().strftime('%Y.%m%d.%H%M%S')
        subdirs = ip + '-' + date + '-' + freq + '-' + volt_level
        os.mkdir('./%s/%s' % (ip_dirs, subdirs))

        # Freq, Volt_level and more_options
        os.system("echo %s > ./%s/freq.log" % (freq, ip_dirs))
        os.system("echo %s > ./%s/volt.log" % (volt_level, ip_dirs))
        os.system("echo %s > ./%s/options.log" % (option.strip("'"), ip_dirs))
        # Grep debuglog datas
        os.system("cat ./%s/estats.log | grep '\[MM ID' > ./%s/%s/CGMiner_Debug.log" % (ip_dirs, ip_dirs, subdirs))
        os.system("cat ./%s/edevs.log | grep -v Reply  > ./%s/%s/CGMiner_Edevs.log" % (ip_dirs, ip_dirs, subdirs))
        os.system("cat ./%s/summary.log | grep -v Reply  > ./%s/%s/CGMiner_Summary.log" % (ip_dirs, ip_dirs, subdirs))

        # Write csv files
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
    ''' Read times, ips, options form slt-options.conf '''

    ips = []
    options = []

    path = 'slt-options.conf'
    option_flag = 0

    try:
        with open(path) as f:
            for line in f:
                if line == '\n':
                    continue

                tmp = re.search('^\s*#', line)
                if tmp:
                    option_flag += 1
                    continue

                if option_flag == 1:
                    times = line.strip()
                elif option_flag == 2:
                    ips.append(line.strip())
                elif option_flag == 3:
                    options.append(line.strip())
    except:
        sys.exit()

    return times, ips, options


if __name__ == '__main__':
    threads = []
    global options
    global times

    # Read Config file
    times, ips, options = read_config()
    logging.debug("times: %s", times)
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
