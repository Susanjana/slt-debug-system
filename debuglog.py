#!/usr/bin/env python


import datetime
import sys
import config
import os
import logging
import remote
import time

# Config logging level
logging.basicConfig(level=logging.DEBUG)

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

'''
    cat $i | sed 's/] /\]\n/g' | grep GHSmm | sed 's/GHSmm\[//g' | sed 's/\]//g' > $i.GHSmm
    cat $i | sed 's/] /\]\n/g' | grep Temp  | sed 's/Temp\[//g'  | sed 's/\]//g' > $i.Temp
    cat $i | sed 's/] /\]\n/g' | grep TMax  | sed 's/TMax\[//g'  | sed 's/\]//g' > $i.TMax
    cat $i | sed 's/] /\]\n/g' | grep WU    | sed 's/WU\[//g'    | sed 's/\]//g' > $i.WU
    cat $i | sed 's/] /\]\n/g' | grep DH    | sed 's/DH\[//g'    | sed 's/\]//g' > $i.DH
    cat $i | sed 's/] /\]\n/g' | grep Power | sed 's/Power\[//g' | sed 's/\]//g' > $i.Power
    cat $i | sed 's/] /\]\n/g' | grep "Iout\["    | sed 's/Iout\[//g'    | sed 's/\]//g' > $i.Iout
    cat $i | sed 's/] /\]\n/g' | grep V0 | awk '{ print $3 }' > $i.V0

    # According to WU value, calculate GHSav.
    # Formula: ghsav = WU / 60 * 2^32 / 10^9
    cat $i.WU | awk '{printf ("%.2f\n", ($1/60*2^32/10^9))}' > $i.GHSav

    # Power / GHSav
    paste $i.GHSav $i.Power | awk '{printf ("%.3f\n", ($2/$1))}' > ph.log

    Result=Results_$dirname

    paste -d, freq.log voltage.log $i.GHSmm $i.Temp $i.TMax $i.WU $i.GHSav $i.DH $i.Iout $i.V0 $i.Power ph.log options.log > ${Result#.log}.csv
'''
