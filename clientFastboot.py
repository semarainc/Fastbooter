#!/usr/bin/env python3

import sys
import socket
import getpass
import subprocess

import gi.repository.GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop

#HOST = '127.0.0.1'  # The server's hostname or IP address
#PORT = 8099        # The port used by the server
mainloop = None

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect("/var/fastbooter.s")

def notifications(bus, message):
    global s, mainloop
    # do your magic
    print(bus, " --:-- ", message)

    msg = message.get_args_list()
    print(msg[0])
    print(msg[4])

    if msg[0] == 'Plasma Workspace' and "Logout canceled" in msg[4]:
        s.send(b'batals')
        while 1:
            data = s.recv(1024)
            print(data)
            break
            if not data:
                break
        mainloop.quit()
        #sys.exit(0)

username = getpass.getuser()
argumens = f"fastbootmodes|{username}".encode('utf-8')
s.send(argumens)
#print("logout")
subprocess.Popen(["qdbus org.kde.ksmserver /KSMServer logout 0 0 0"], shell=True)
while 1:
    data = s.recv(1024)
    print(data)
    print('Received', repr(data))

    break

print("RUN PLEA")
DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
bus.add_message_filter(notifications)

mainloop = gi.repository.GLib.MainLoop()
mainloop.run()
sys.exit(0)
