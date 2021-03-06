#!/usr/bin/python
import os
from datetime import datetime
import sys

def usage():
    print "./get_master_dpdk.py --compile_method <dynamic or static> --flag <default, debug, or sg1>"

if len(sys.argv) < 3:
    usage()
    sys.exit(1)

compile_method = sys.argv[1]
flag = sys.argv[2]

os.system("echo '111'  >> /tmp/new_out.log")

date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
directory = '/tmp/' + date

print "Move last cloned DPDK"
os.system("mv  /downloud/dpdk/ %s" %directory)
os.system("mv /download/dpdk/ /%s >> /tmp/new_out.log" %directory)

print "Cloninig DPDK into '/download/dpdk/'"
os.system("cd /download/; git clone git://dpdk.org/dpdk ")
os.system("echo 'dpdk cloned ...' >> /tmp/new_out.log")


if compile_method == 'dynamic' and flag == 'default':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.default')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.default' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'dynamic' and flag == 'debug':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.debug')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.debug' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_DEBUG=n/c\CONFIG_RTE_LIBRTE_MLX4_DEBUG=y' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
    os.system('cd /download/dpdk; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'dynamic' and flag == 'sg1':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.sg1')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.sg1' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=4/c\CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=1' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
    os.system('cd /download/dpdk; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'static' and flag == 'default':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_static.default')
#    os.system("echo 'dpdk copied to dpdk_master_static.default' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
    os.environ["EXTRA_CFLAGS"] = "-I/download/libs/install/usr/local/include"
    os.environ["EXTRA_LDFLAGS"] = "-L/download/libs/install/usr/local/lib"
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
    os.system('cd /download/dpdk; make install T=x86_64-native-linuxapp-gcc')
os.system("echo 'dpdk options enabled and compiled' >> /tmp/new_out.log")


os.system("echo 'dpdk compiled' >> /tmp/new_out.log")
