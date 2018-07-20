#!/usr/bin/env python

from __future__ import print_function
import telnetlib
import sys
import time
import paramiko

def ssh_read_power(ip):
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
                'python /usr/bin/readpower')
            time.sleep(2)
            v = stdout.read()
        except:
            ssh.close()
            continue

        ssh.close()
        break
    return v


def remote_scp(flag, ip):
    ssh_port = 22
    try:
        conn = paramiko.Transport((ip, ssh_port))
        conn.connect(username="root", password=1)
        sftp = paramiko.SFTPClient.from_transport(conn)
        print("2")
        if (flag == 0):
            if not local_path:
                conn.close()
                return False
            sftp.get("/root/test", "./")
    except Exception:
        print("except")
        return False

    conn.close()
    return True

if __name__ == '__main__':
    ip = sys.argv[1]

    remote_scp(0, ip)
