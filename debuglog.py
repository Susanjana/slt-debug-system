#!/usr/bin/env python
# -*- coding: utf-8; -*-


import datetime
import sys
import config
import os
import remote
import time
import re

_patterns = {
    'ghsmm': "GHSmm\[[0-9]{1,6}\.[0-9]{1,2}\]",
    'temp': "Temp\[[0-9]{1,6}\]",
    'tmax': "TMax\[[0-9]{1,6}\]",
    'wu': "WU\[[0-9]{1,6}\.[0-9]{1,2}\]",
    'iout': "Iout\[[0-9]{1,3}\.[0-9]{1,3}\]",
    'power': "Power\[[0-9]{1,3}\.[0-9]{1,3}\]",
    'dh': "DH\[[0-9]{1,3}\.[0-9]{1,3}\%\]",
}

_patternd = {
    'ghsmm': "[0-9]{1,6}\.[0-9]{1,2}",
    'temp': "[0-9]{1,6}",
    'tmax': "[0-9]{1,6}",
    'wu': "[0-9]{1,6}\.[0-9]{1,2}",
    'iout': "[0-9]{1,3}\.[0-9]{1,3}",
    'power': "[0-9]{1,3}\.[0-9]{1,3}",
    'dh': "[0-9]{1,3}\.[0-9]{1,3}",
}

def debuglog_files(ip):
    datas = remote.remote_cmd(ip, 0)
    with open('estats.log', 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

    datas = remote.remote_cmd(ip, 1)
    with open('edevs.log', 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

    datas = remote.remote_cmd(ip, 2)
    with open('summary.log', 'w+') as f:
        f.write(str(datas))
    time.sleep(1)

def handle_debuglog(ip, freq, volt_level):
    global subdirs

    date = datetime.datetime.now().strftime('%Y.%m%d.%H%M%S')
    subdirs = ip + '-' + date + '-' + freq + '-' + volt_level
    os.mkdir('%s' % subdirs)

    # Grep debuglog datas
    os.system('cat estats.log | grep "\[MM ID" > ./%s/CGMiner_Debug.log' % subdirs)
    os.system('cat edevs.log | grep -v Reply  > ./%s/CGMiner_Edevs.log' % subdirs)
    os.system('cat summary.log | grep -v Reply  > ./%s/CGMiner_Summary.log' % subdirs)

def read_debuglog(opt):
    with open(subdirs + '/' + 'CGMiner_Debug.log', 'r') as f:
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

def power_ghsav(ip_dirs):
    with open(ip_dirs + '/' + 'power.log') as f1, open(ip_dirs + '/' + 'ghsav.log') as f2:
            power = f1.read()
            ghsav = f2.read()

    length = len(power.strip().split())
    with open('pg.log', 'a') as f:
        for i in range(length):
            f.write(str(round(float(power.strip().split()[i]) / float(ghsav.strip().split()[i]), 3)))
            f.write('\n')

def result_files():
    os.system("paste -d, ghsmm.log temp.log tmax.log wu.log ghsav.log iout.log power.log dh.log >> result-miner.csv")
    os.system("rm ghsmm.log temp.log tmax.log wu.log ghsav.log iout.log power.log dh.log ")
    os.system("echo '\n' >> result-miner.csv")
