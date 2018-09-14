#!/usr/bin/env python
# -*- coding: utf-8; -*-


import os
import re
import sys
import time
import datetime
import threading

import remote
import debuglog


def show_done(ip):
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++  %s Done  ++++++++++++++++++++++++++++++++++++++++++++\033[0m" % ip)
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")


def modify_cgminer(path, option):
    flag = 0

    with open(path, 'r') as f:
        lines = f.readlines()

    with open(path, 'w') as f:
        for line in lines:
            if 'more_options' in line:
                line = line.replace(line, '\t' + option + '\n')
                f.write(line)
                flag = 1
            else:
                f.write(line)

    if (flag == 0):
        with open(path, 'a') as f:
            f.write('\t' + option + '\n')


def setup(ip):
    ip_dirs = "result" + "-" + ip
    os.mkdir(ip_dirs)

    times = config.config['time']
    print('Times: %s' % times)

    options = config.config['options']
    print('Options: %s' % options)

    # Remote get cgminer file
    remote.remote_scp(ip, 'receive')
    time.sleep(3)

    # Create csv file
    os.system("echo Freq, Volt_level, GHSmm, Temp, TMax, WU, GHsav, Iout, Power, DH, Power/GHsav, DNA, Options >> ./%s/result-miner.csv" % ip_dirs)
    index = 0

    for tmp in options:
        # Modify cgminer file
        tmp = "'%s'" % tmp
        if not os.system('cat ./%s/cgminer | grep more_options' % ip_dirs):
            os.system('more_options=`cat ./%s/cgminer | grep more_options`; sed -i "s/$more_options/        option more_options     %s/g" ./%s/cgminer' % (ip_dirs, tmp, ip_dirs))
        else:
            os.system("echo '       option more_options %s' >> ./%s/cgminer" % (tmp, ip_dirs))
        time.sleep(5)

        # Send cgminer file to remote
        remote.remote_scp(ip, 'send')
        time.sleep(3)

        # Restart cgminer
        remote.remote_cmd(ip, '/etc/init.d/cgminer', 'restart')
        time.sleep(times)

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
        index += 1

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

    global time
    global ips
    option = []

    path = 'slt-options.conf'
    line_cnt = 1

    with open(path) as f:
        for line in f:
            tmp = re.search('^\s*#', line)
            if tmp or line == '\n':
                continue

            if line_cnt == 1:
                time = line.strip()
            elif line_cnt == 2:
                ip = line.strip()
            elif line_cnt >= 3:
                option.append(line.strip())
            line_cnt += 1

    print("time: %s" % time)
    print("ip: %s" % ip)
    print(option)

    return option


if __name__ == '__main__':
    threads = []

    read_config()

    # According to ip number, creating threads
    ips = list(config.config['ip'])
    for line in ips:
        thr = threading.Thread(target=setup, args=(line,))
        thr.start()
        threads.append(thr)

    for thr in threads:
        thr.join()

    os.system("rm *.pyc")
