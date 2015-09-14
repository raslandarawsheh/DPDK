#!/usr/bin/python

import os
from datetime import datetime
import sys

def usage():
    print "./get_master_rc_per.py -- auto compile dpdk_rc for performance run "

if len(sys.argv) > 1 :
    usage()
    sys.exit(1)

os.system("echo '111'  >> /tmp/new_out.log")

date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
directory = '/tmp/' + date

print "Move last cloned DPDK"
os.system("mv  /downloud/dpdk/ %s" %directory)
os.system("mv /download/dpdk/ /%s >> /tmp/new_out.log" %directory)

print "Cloninig DPDK into '/download/dpdk/'"
os.system("cd /download/; git clone git://dpdk.org/dpdk ")
os.system("echo 'dpdk cloned ...' >> /tmp/new_out.log")

os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=4/c\CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=1' '/download/dpdk/config/common_linuxapp'")
os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
os.system('cd /download/dpdk; make install T=x86_64-native-linuxapp-gcc')

os.system("echo 'dpdk options enabled and compiled' >> /tmp/new_out.log")

print "dpdk compiled"
os.system("echo 'dpdk compiled' >> /tmp/new_out.log")
