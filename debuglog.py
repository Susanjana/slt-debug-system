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
    'dh': "DH\[[0-9]{1,3}\.[0-9]{1,3}\%\]",
    'iout': "Iout\[[0-9]{1,3}\.[0-9]{1,3}\]",
    'power': "Power\[[0-9]{1,3}\.[0-9]{1,3}\]",
}

_patternd = {
    'ghsmm': "[0-9]{1,6}\.[0-9]{1,2}",
    'temp': "[0-9]{1,6}",
    'tmax': "[0-9]{1,6}",
    'wu': "[0-9]{1,6}\.[0-9]{1,2}",
    'dh': "[0-9]{1,3}\.[0-9]{1,3}",
    'iout': "[0-9]{1,3}\.[0-9]{1,3}",
    'power': "[0-9]{1,3}\.[0-9]{1,3}",
}

def debuglog_files(ip_dirs, ip):
    datas = remote.remote_cmd(ip, 'cgminer-api', 'estats')
    with open(ip_dirs + '/' + 'estats.log', 'w') as f:
        f.write(str(datas))

    datas = remote.remote_cmd(ip, 'cgminer-api', 'edevs')
    with open(ip_dirs + '/' + 'edevs.log', 'w') as f:
        f.write(str(datas))

    datas = remote.remote_cmd(ip, 'cgminer-api', 'summary')
    with open(ip_dirs + '/' + 'summary.log', 'w') as f:
        f.write(str(datas))

def handle_debuglog(ip_dirs, ip, freq, volt_level):
    global subdirs

    date = datetime.datetime.now().strftime('%Y.%m%d.%H%M%S')
    subdirs = ip + '-' + date + '-' + freq + '-' + volt_level
    os.mkdir('%s' % subdirs)

    # Grep debuglog datas
    os.system('cat ./%s/estats.log | grep "\[MM ID" > ./%s/%s/CGMiner_Debug.log' % (ip_dirs, ip_dirs, subdirs))
    os.system('cat ./%s/edevs.log | grep -v Reply  > ./%s/%s/CGMiner_Edevs.log' % (ip_dirs, ip_dirs, subdirs))
    os.system('cat ./%s/summary.log | grep -v Reply  > ./%s/%s/CGMiner_Summary.log' % (ip_dirs, ip_dirs, subdirs))

def read_debuglog(ip_dirs, opt):
    with open(ip_dirs + '/' + subdirs + '/' + 'CGMiner_Debug.log', 'r') as f:
        for lines in f:
            tmp = str(re.findall(_patternd[opt], str(re.findall(_patterns[opt], lines)))).strip("[']")
            with open(ip_dirs + '/' + opt + '.log', 'a') as f:
                f.write(tmp + '\n')

def gen_ghsav(ip_dirs):
    with open(ip_dirs + '/' + 'wu.log', 'r') as f:
        for line in f:
            tmp = round(float(line.strip()) / 60 * 2**32 / 10**9, 3)
            with open(ip_dirs + '/' + 'ghsav.log', 'a') as f:
                f.write(str(tmp) + '\n')

def power_ghsav(ip_dirs):
    with open(ip_dirs + '/' + 'power.log') as f1, open(ip_dirs + '/' + 'ghsav.log') as f2:
            power = f1.read()
            ghsav = f2.read()

    l = len(power.strip().split())
    with open(ip_dirs + '/' + 'pg.log', 'a') as f:
        for i in range(l):
            f.write(str(round(float(power.split()[i]) / float(ghsav.split()[i]), 3)) + '\n')

def result_files(ip_dirs):
    os.system("paste -d, ./%s/ghsmm.log ./%s/temp.log ./%s/tmax.log ./%s/wu.log ./%s/ghsav.log ./%s/dh.log ./%s/iout.log ./%s/power.log ./%s/pg.log >> ./%s/result-miner.csv" \
                % (ip_dirs, ip_dirs, ip_dirs, ip_dirs, ip_dirs, ip_dirs, ip_dirs, ip_dirs, ip_dirs))
    os.system("rm ./%s/*log" % ip_dirs)
    os.system("echo '\n' >> ./%s/result-miner.csv" % ip_dirs)
