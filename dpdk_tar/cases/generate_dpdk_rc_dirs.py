#!/usr/bin/python
import os
import sys
from datetime import datetime


def usage():
    print "./generate_dpdk_rc_dirs.py --tar_file <tar_file> --compile_method <dynamic or static> --flag <default, debug, or sg1>"

if len(sys.argv) < 4:
    usage()
    sys.exit(1)

tar_file = sys.argv[1]
compile_method = sys.argv[2]
flag = sys.argv[3]

date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
directory = '/download/' + date
print "Log File is %s" %directory

os.system('cd /download; tar xvf %s' %tar_file)
os.system("echo 'tar file extracted to /download' > %s" %(directory))
os.system("rm -rf /download/dpdk_master")
os.system('cd /download; cp -r /download/dpdk-2.0.0 /download/dpdk_master')

if compile_method == 'dynamic' and flag == 'default':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.default')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.default' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'dynamic' and flag == 'debug':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.debug')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.debug' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_DEBUG=n/c\CONFIG_RTE_LIBRTE_MLX4_DEBUG=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'dynamic' and flag == 'sg1':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.sg1')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.sg1' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=4/c\CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=1' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'static' and flag == 'default':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_static.default')
#    os.system("echo 'dpdk copied to dpdk_master_static.default' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.environ["EXTRA_CFLAGS"] = "-I/download/libs/install/usr/local/include"
    os.environ["EXTRA_LDFLAGS"] = "-L/download/libs/install/usr/local/lib"
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'static' and flag == 'debug':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_static.debug')
#    os.system("echo 'dpdk copied to dpdk_master_static.debug' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_DEBUG=n/c\CONFIG_RTE_LIBRTE_MLX4_DEBUG=y' '/download/dpdk_master/config/common_linuxapp'")
    os.environ["EXTRA_CFLAGS"] = "-I/download/libs/install/usr/local/include"
    os.environ["EXTRA_LDFLAGS"] = "-L/download/libs/install/usr/local/lib"
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

elif compile_method == 'static' and flag == 'sg1':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_static.sg1')
#    os.system("echo 'dpdk copied to dpdk_master_static.sg1' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk_master/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=4/c\CONFIG_RTE_LIBRTE_MLX4_SGE_WR_N=1' '/download/dpdk_master/config/common_linuxapp'")
    os.environ["EXTRA_CFLAGS"] = "-I/download/libs/install/usr/local/include"
    os.environ["EXTRA_LDFLAGS"] = "-L/download/libs/install/usr/local/lib"
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk_master/config/common_linuxapp'")
    os.system('cd /download/dpdk_master; make install T=x86_64-native-linuxapp-gcc')

else:
    print "Not valid prameters"
    sys.exit(1)
print "Log File is %s *******************************************************" %directory
