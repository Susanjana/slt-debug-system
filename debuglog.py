#!/usr/bin/env python


import datetime
import sys
import config
import os
import logging
import remote
import time
import re

# Config logging level
logging.basicConfig(level=logging.DEBUG)

_patterns = {
    'ghsmm': "GHSmm\[[0-9]{1,6}\.[0-9]{1,2}\]",
    'temp': "Temp\[[0-9]{1,6}\]",
    'tmax': "TMax\[[0-9]{1,6}\]",
    'wu': "WU\[[0-9]{1,6}\.[0-9]{1,2}\]",
    'dh': "DH\[[0-9]{1,3}\.[0-9]{1,3}\%\]",
    'power': "Power\[[0-9]{1,3}\.[0-9]{1,3}\]",
    'iout': "Iout\[[0-9]{1,3}\.[0-9]{1,3}\]",
}

_patternd = {
    'ghsmm': "[0-9]{1,6}\.[0-9]{1,2}",
    'temp': "[0-9]{1,6}",
    'tmax': "[0-9]{1,6}",
    'wu': "[0-9]{1,6}\.[0-9]{1,2}",
    'dh': "[0-9]{1,3}\.[0-9]{1,3}",
    'power': "[0-9]{1,3}\.[0-9]{1,3}",
    'iout': "[0-9]{1,3}\.[0-9]{1,3}",
}

def read_debuglog(opt):
    with open('debug.log', 'r') as f:
        for lines in f:
            tmp = str(re.findall(_patternd[opt], str(re.findall(_patterns[opt], lines)))).strip("[']")
            with open(opt + '.log', 'a') as f:
                f.write(tmp + '\n')

def gen_ghsav():
    with open('wu.log', 'r') as f:
        for line in f:
            tmp = round(float(line.strip()) / 60 * 2**32 / 10**9, 3)
            with open('ghsav.log', 'a') as f:
                f.write(str(tmp) + '\n')

def power_rate():
    os.system("paste $i.GHSav $i.Power | awk '{printf ('%.3f\n', ($2 / $1))}' > ph.log")

def debuglog_files(ip_dirs):
    datas = remote.remote_cmd(ip, 0)
    path = '%s/estats.log' % ip_dirs
    with open(path, 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

    datas = remote.remote_cmd(ip, 1)
    path = '%s/edevs.log' % ip_dirs
    with open(path, 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

    datas = remote.remote_cmd(ip, 2)
    path = '%s/summary.log' % ip_dirs
    with open(path, 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

def handle_debuglog(ip_dirs, ip, freq, volt_level):
    date = datetime.datetime.now().strftime('%Y.%m%d.%H%M%S')
    subdirs = ip + '-' + date + '-' + freq + '-' + volt_level
    logging.debug("Create sub dirs name: %s", subdirs)
    os.makedirs('%s/%s' % (ip_dirs, subdirs))

    # Grep debuglog datas
    os.system('cat %s/estats.log | grep "\[MM ID" > ./%s/%s/CGMiner_Debug.log' % (ip_dirs, ip_dirs, subdirs))
    os.system('cat %s/edevs.log | grep -v Reply  > ./%s/%s/CGMiner_Edevs.log' % (ip_dirs, ip_dirs, subdirs))
    os.system('cat %s/summary.log | grep -v Reply  > ./%s/%s/CGMiner_Summary.log' % (ip_dirs, ip_dirs, subdirs))

if __name__ == '__main__':
    ip = sys.argv[1]
    freq = sys.argv[2]
    volt_level = sys.argv[3]

    ip_dirs = "result" + "-" + ip
    logging.debug("debuglog create dirs: %s", ip_dirs)
    os.makedirs(ip_dirs)

    debuglog_files(ip_dirs)
    handle_debuglog(ip_dirs, ip, freq, volt_level)

    read_debuglog('ghsmm')
    read_debuglog('temp')
    read_debuglog('tmax')
    read_debuglog('wu')
    read_debuglog('dh')
    read_debuglog('power')
    read_debuglog('iout')
    gen_ghsav()
    power_rate()

    os.system("paste -d, ghsmm.log temp.log tmax.log wu.log dh.log power.log iout.log ghsav.log >> result-miner.csv")
    os.system("rm ghsmm.log temp.log tmax.log wu.log dh.log power.log iout.log ghsav.log")
