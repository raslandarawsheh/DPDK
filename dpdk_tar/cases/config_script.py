#!/usr/bin/python

import os
import sys
from datetime import datetime
import time

def usage():
    print "./config_script.py --dmfs_mod <A0 or B0> "

if len(sys.argv) < 2:
    usage()
    sys.exit(1)

if sys.argv[1] == 'A0':
    # os.system("/download/configure_mlx4_pmd.sh -s nosriov -o") #-n 4096 to restore every thing 
    os.system("/download/configure_mlx4_pmd.sh -s nosriov -n 4096  -o")
    os.system("/etc/init.d/openibd restart")
else:
    os.system("/download/configure_mlx4_pmd.sh -s nosriov -n 4096 ")
    os.system("/etc/init.d/openibd restart")

time.sleep(20)

os.system("ifconfig ens4 11.4.3.5 netmask 255.255.255.0 mtu 1500 up")
os.system("ifconfig ens4d1 12.4.3.5 netmask 255.255.255.0 mtu 1500 up")
os.system("ifconfig ens1f1 22.4.3.5 netmask 255.255.255.0 mtu 1500 up")
os.system("ifconfig ens1f0 21.4.3.5 netmask 255.255.255.0 mtu 1500 up")

