#!/usr/bin/env python3

import os
import socket
import subprocess
import time
import logging
import psutil
import shutil

from multiprocessing import Process, Queue

#HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
#PORT = 8099        # Port to listen on (non-privileged ports are > 1023)
worker = None

def ShutFastboot():
    shutdown = 0
    batal = 0
    temp = None
    while 1:
        try:
           # print("CEK ME")
            with open('/var/fastbooter') as usrname:
                username = usrname.read()
            cek = subprocess.Popen([f'loginctl user-status {username} | grep "\State\:" | cut -d ":" -f 2 | cut -d " " -f 2'], shell=True, stdout=subprocess.PIPE).communicate()
            ada = 0

            while ada == 0:
                for proc in psutil.process_iter():
                    try:
                        if 'sddm'.lower() in proc.name().lower():
                            ada = 1
                            print("SDDM SHOWN, TERMINATING USER...")
                            subprocess.Popen([f'loginctl terminate-user {username}'], shell=True, stdout=subprocess.PIPE)
                            break
                        else:
                            print("SDDM Gk ada")
                    except:
                        print("PROSES DIGAGALKAN EKSEPSI")
           # print(cek)
            if len(cek) >=1:
                temp = cek[0].decode().strip()

            if 'online' not in str(temp).lower():
                if 'active' not in str(temp).lower():
                    #time.sleep(5)
                    limiter = 0
                    ada = 0
                    while ada == 0:
                        for proc in psutil.process_iter():
                            try:
                                if 'sddm'.lower() in proc.name().lower():
                                    ada = 1
                                    print("SDDM ADA")
                                    time.sleep(5)
                                    print("CHVT2")
                                    subprocess.Popen(['swapoff -a'], shell=True)
                                    subprocess.Popen(['chvt 2'], shell=True)
                                    swap_relieve = subprocess.Popen(['swapon', '/dev/sda3'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                                    break
                                else:
                                    print("SDDM Gk ada")
                            except:
                                print("PROSES DIGAGALKAN EKSEPSI")
                    while ada == 1:
                        if isinstance(swap_relieve, tuple):
                            if len(swap_relieve[1]) > 0:
                                swap_relieve = subprocess.Popen(['swapon', '/dev/sda3'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                                print('Output: ', swap_relieve[0].decode())
                                print('Error: ', swap_relieve[1].decode())
                            elif len(swap_relieve[1]) <= 0:
                                ada = 2
                        limiter += 1
                        time.sleep(3)
                    shutdown = 1
                    break
            #time.sleep(1)
        except Exception as e:
            print(e)
            print("client disconnect")
            break

    if batal == 0 and shutdown == 1:
        print("MATI")
        batal = 0
        shutdown = 0
        time.sleep(5)
        subprocess.Popen(['chvt 2'], shell=True)
        #shutil.copyfile("/etc/systemd/logind.conf.default", "/etc/systemd/logind.conf")
        subprocess.Popen(['systemctl hibernate & >/dev/null 2>&1 &'], shell=True)

print("SYSTEM STARTED...")
if os.path.exists("/var/fastbooter.s"):
    os.remove("/var/fastbooter.s")

with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind("/var/fastbooter.s")
    os.chmod("/var/fastbooter.s", 0o777)
    s.listen()
    while 1:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    conn.send(data)
                    cmds = data.decode().split("|")
                    if len(cmds) > 1:
                        if cmds[0] == 'fastbootmodes':
                            print("YEAH")
                            with open("/var/fastbooter", 'w') as f:
                                f.write(cmds[1])

                            #shutil.copyfile("/etc/systemd/logind.conf.fastboot", "/etc/systemd/logind.conf")
                            #subprocess.Popen(['systemctl restart systemd-logind & >/dev/null 2>&1 &'], shell=True)
                            worker = Process(target=ShutFastboot)
                            worker.daemon = True
                            worker.start()
                            conn.send(b"begin fastboot")

                    if data.decode() == 'batals':
                        os.remove('/var/fastbooter')
                        worker.terminate()
                        #shutil.copyfile("/etc/systemd/logind.conf.default", "/etc/systemd/logind.conf")
                        #subprocess.Popen(['systemctl restart systemd-logind & >/dev/null 2>&1 &'], shell=True)
                        #conn.send(b"bataled")
                        #conn.close()
                        #break
                except Exception as e:
                    print(e)
