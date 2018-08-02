#!/usr/bin/env python

from __future__ import print_function
import telnetlib
import sys
import time
import paramiko
import os

global ip
global flag

def remote_cmd():
    v = None
    retry = 3
    for i in range(0, retry):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for k in range(0, retry):
            try:
                ssh.connect(ip, 22, 'root')
                break
            except:
                ssh.close()
                if k == retry - 1:
                    return None
        try:
            if (flag == 0):
                stdin, stdout, stderr = ssh.exec_command(
                    'cgminer-api estats')
            elif (flag == 1):
                stdin, stdout, stderr = ssh.exec_command(
                    'cgminer-api edevs')
            elif (flag == 2):
                stdin, stdout, stderr = ssh.exec_command(
                    'cgminer-api summary')
            else:
                return None
            time.sleep(2)
            v = stdout.read()
        except:
            ssh.close()
            continue

        ssh.close()
        break
    return v

def remote_scp():
    if (flag == 0):
        os.system("scp root@%s:/etc/config/cgminer ./" % ip)
    elif (flag == 1):
        os.system("scp ./hash-wu.md root@%s:/etc/config/" % ip)
    else:
        return False

    return True

if __name__ == '__main__':
    ip = sys.argv[1]
    flag = int(sys.argv[2])

    if (remote_scp() == True):
        sys.exit(1)

    sys.exit(1)
    datas = remote_cmd()
    if datas is None:
        print("Get datas failed.")
        sys.exit(1)

    if (flag == 0):
        estats = open('estats.log', 'w+')
        estats.write(str(datas))
        estats.close()
    elif (flag == 1):
        estats = open('edevs.log', 'w+')
        estats.write(str(datas))
        estats.close()
    elif (flag == 2):
        estats = open('summary.log', 'w+')
        estats.write(str(datas))
        estats.close()
    else:
        print("Flag value error.")
        sys.exit(1)
