#!/usr/bin/env python
# -*- coding: utf-8; -*-


import os
import sys
import time
import paramiko

def remote_cmd(ip, cmd, para):
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
            stdin, stdout, stderr = ssh.exec_command(
                '%s %s' % (cmd, para))
            time.sleep(2)
            v = stdout.read()
        except:
            ssh.close()
            continue

        ssh.close()
        break
    return v

def remote_scp(ip, mode):
    if (mode == 'receive'):
        os.system("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s:/etc/config/cgminer ./result-%s/cgminer" % (ip, ip))
    elif (mode == 'send'):
        os.system("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ./result-%s/cgminer root@%s:/etc/config/" % (ip, ip))
    else:
        return False

    return True
