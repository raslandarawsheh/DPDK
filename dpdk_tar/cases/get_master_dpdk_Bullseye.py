#!/usr/bin/python

import os
from datetime import datetime
import sys
import time

def usage():
    print "./get_master_dpdk_Bullseye.py --compile_method <dynamic or static> --flag <default, debug, or sg1>"

if len(sys.argv) < 3:
    usage()
    sys.exit(1)

compile_method = sys.argv[1]
flag = sys.argv[2]

os.system("echo '111'  >> /tmp/new_out.log")

date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
directory = '/tmp/' + date
os.system("export PATH=/download/BullseyeCoverage/bin:$PATH")
os.environ["PATH"] = '/download/BullseyeCoverage/bin'+os.pathsep + os.environ["PATH"]
os.environ["COVFILE"] = '/download/clean.cov'
os.system("echo 'Path is : '.$PATH")
#os.system("export COVFILE=/download/clean.cov")
os.system("echo COVFILE is  :      $COVFILE")
print "Move last cloned DPDK"
#need to check this with Feras
os.system("mv  /downloud/MLNX_DPDK-2.1-1.0/ %s" %directory)
os.system("mv /download/MLNX_DPDK-2.1-1.0/ /%s >> /tmp/new_out.log" %directory)


print "Cloninig DPDK into '/download/MLNX_DPDK-2.1-1.0/'"
os.system("cd /download/; tar xvf MLNX_DPDK-2.1-1.0.tar.gz ")
os.system("echo 'dpdk cloned ...' >> /tmp/new_out.log")


if compile_method == 'dynamic' and flag == 'default':
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_PMD=n/c\CONFIG_RTE_LIBRTE_MLX5_PMD=y' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=1/c\CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=4' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
   # os.environ["COVFILE"] = '/download/clean.cov'
    os.system('echo $COVFILE > /tmp/covfile')
    os.system("cov01 -1 &> /tmp/cov")
    time.sleep(1)
    print "Befor compiling "
    os.system('cd /download/MLNX_DPDK-2.1-1.0; make install T=x86_64-native-linuxapp-gcc')
    os.system("cov01 -0")
    os.system("echo $COVFILE")
    print "After compiling "


elif compile_method == 'dynamic' and flag == 'debug':
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_PMD=n/c\CONFIG_RTE_LIBRTE_MLX5_PMD=y' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_DEBUG=n/c\CONFIG_RTE_LIBRTE_MLX5_DEBUG=y' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=1/c\CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=4' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    #os.environ["COVFILE"] = '/download/clean.cov'
    os.system('echo $COVFILE > /tmp/covfile')
    os.system("cov01 -1 ")
    print "Befor compiling "
    time.sleep(1)
    os.system('cd /download/MLNX_DPDK-2.1-1.0; make install T=x86_64-native-linuxapp-gcc')
    os.system("cov01 -0")
    print "After compiling "

elif compile_method == 'dynamic' and flag == 'sg1':
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_PMD=n/c\CONFIG_RTE_LIBRTE_MLX5_PMD=y' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=4/c\CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=1' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    #os.environ["COVFILE"] = '/download/clean.cov'
    os.system('echo $COVFILE > /tmp/covfile')
    os.system("cov01 -1 ")
    os.system('cd /download/MLNX_DPDK-2.1-1.0; make install T=x86_64-native-linuxapp-gcc')
    os.system("cov01 -0")

elif compile_method == 'static' and flag == 'default':
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_PMD=n/c\CONFIG_RTE_LIBRTE_MLX5_PMD=y' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=1/c\CONFIG_RTE_LIBRTE_MLX5_SGE_WR_N=4' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    os.environ["EXTRA_CFLAGS"] = "-I/download/libs/install/usr/local/include"
    os.environ["EXTRA_LDFLAGS"] = "-L/download/libs/install/usr/local/lib"
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/MLNX_DPDK-2.1-1.0/config/common_linuxapp'")
    #os.environ["COVFILE"] = '/download/clean.cov'
    os.system('echo $COVFILE > /tmp/covfile')
    os.system("cov01 -1 ")
    os.system('cd /download/MLNX_DPDK-2.1-1.0; make install T=x86_64-native-linuxapp-gcc')
    os.system("cov01 -0")
else : 
    print "Error "
os.system("echo 'dpdk options enabled and compiled' >> /tmp/new_out.log")

print "dpdk compiled"
os.system("echo 'dpdk compiled' >> /tmp/new_out.log")
