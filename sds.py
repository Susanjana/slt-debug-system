#!/usr/bin/env python
# -*- coding: utf-8; -*-


import time
import os
import config
import remote
import debuglog
import threading
import sys

def show_done(ip):
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++  %s Done  ++++++++++++++++++++++++++++++++++++++++++++\033[0m" % ip)
    print("\033[1;32m+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\033[0m")


def get_datas_handle(ip):
    ip_dirs = "result" + "-" + ip
    os.mkdir(ip_dirs)

    times = config.config['time']
    print('Times: %s' % times)

    options = config.config['options']
    print('Options: %s' % options)

    # Remote get cgminer file
    remote.remote_scp(ip, 0)
    time.sleep(3)

    # Create csv file
    os.system("echo GHSmm, Temp, TMax, WU, GHsav, Iout, Power, DH >> result-miner.csv")
    index = 0

    for tmp in options:
        tmp = "'%s'" % tmp
        if not os.system('cat cgminer | grep more_options'):
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
        debuglog.debuglog_files(ip)
        freq = list(config.config['options'])[index].split()[1]
        volt = list(config.config['options'])[index].split()[3]
        debuglog.handle_debuglog(ip, freq, volt)
        index += 1

        debuglog.read_debuglog(ip_dirs, 'ghsmm')
        debuglog.read_debuglog(ip_dirs, 'temp')
        debuglog.read_debuglog(ip_dirs, 'tmax')
        debuglog.read_debuglog(ip_dirs, 'wu')
        debuglog.read_debuglog(ip_dirs, 'dh')
        debuglog.read_debuglog(ip_dirs, 'power')
        debuglog.read_debuglog(ip_dirs, 'iout')
        debuglog.gen_ghsav(ip_dirs)
        debuglog.result_files(ip_dirs)

    # Remove cgminer file
    os.system("rm result-%s/cgminer" % ip)
    show_done(ip)

if __name__ == '__main__':
    threads = []

    ips = list(config.config['ip'])
    for line in ips:
        thr = threading.Thread(target=get_datas_handle, args=(line,))
        thr.start()
        threads.append(thr)

    for thr in threads:
        thr.join()
