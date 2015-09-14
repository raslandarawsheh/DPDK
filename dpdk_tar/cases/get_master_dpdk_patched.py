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
#os.system("echo 'patching dpdk.org' ")
#os.system("cd /download/dpdk;patch -p1 <  /download/patchset_v2/0001-eal-fix-cpu_feature_table-compilation-with-pedantic.patch;patch -p1 <  /download/patchset_v2/0002-mlx4-fix-possible-crash-on-scattered-mbuf-allocation.patch;patch -p1 </download/patchset_v2/0003-mlx4-add-MOFED-3.0-compatibility-to-interfaces-names.patch;patch -p1 <  /download/patchset_v2/0004-mlx4-make-sure-experimental-device-query-function-is.patch;patch -p1 <  /download/patchset_v2/0005-mlx4-avoid-looking-up-WR-ID-to-improve-RX-performanc.patch;patch -p1 <  /download/patchset_v2/0006-mlx4-merge-RX-queue-setup-functions.patch;patch -p1 <  /download/patchset_v2/0007-mlx4-allow-applications-to-partially-use-fork.patch;patch -p1 <  /download/patchset_v2/0008-mlx4-improve-accuracy-of-link-status-information.patch;patch -p1 <  /download/patchset_v2/0009-mlx4-use-MOFED-3.0-extended-flow-steering-API.patch;patch -p1 <  /download/patchset_v2/0010-mlx4-fix-error-message-for-invalid-number-of-descrip.patch;patch -p1 <  /download/patchset_v2/0011-mlx4-remove-provision-for-flow-creation-failure-in-D.patch;patch -p1 <  /download/patchset_v2/0012-mlx4-fix-support-for-multiple-VLAN-filters.patch;patch -p1 <  /download/patchset_v2/0013-mlx4-query-netdevice-to-get-initial-MAC-address.patch;patch -p1 <  /download/patchset_v2/0014-mlx4-use-MOFED-3.0-fast-verbs-interface-for-RX-opera.patch;patch -p1 <  /download/patchset_v2/0015-mlx4-improve-performance-by-requesting-TX-completion.patch;patch -p1 <  /download/patchset_v2/0016-mlx4-use-MOFED-3.0-fast-verbs-interface-for-TX-opera.patch;patch -p1 <  /download/patchset_v2/0017-mlx4-move-scattered-TX-processing-to-helper-function.patch;patch -p1 <  /download/patchset_v2/0018-mlx4-shrink-TX-queue-elements-for-better-performance.patch;patch -p1 <  /download/patchset_v2/0019-mlx4-prefetch-completed-TX-mbufs-before-releasing-th.patch;patch -p1 <  /download/patchset_v2/0020-mlx4-add-L3-and-L4-checksum-offload-support.patch;patch -p1 <  /download/patchset_v2/0021-mlx4-add-L2-tunnel-VXLAN-checksum-offload-support.patch;patch -p1 <  /download/patchset_v2/0022-mlx4-associate-resource-domain-with-CQs-and-QPs-to-e.patch;patch -p1 <  /download/patchset_v2/0002-doc-update-mlx4-documentation-following-MOFED-3.0-ch.patch;patch -p1 <  /download/patchset_v2/0001-mlx4-disable-multicast-echo-when-device-is-not-VF.patch")

if compile_method == 'dynamic' and flag == 'default':
#    os.system('cd /download; cp -r dpdk-2.0.0 dpdk_master_dynamic.default')
#    os.system("echo 'dpdk copied to dpdk_master_dynamic.default' >> %s" %(directory))
    os.system("sed -i '/CONFIG_RTE_LIBRTE_MLX4_PMD=n/c\CONFIG_RTE_LIBRTE_MLX4_PMD=y' '/download/dpdk/config/common_linuxapp'")
    os.system("sed -i '/CONFIG_RTE_LIBRTE_VIRTIO_PMD=y/c\CONFIG_RTE_LIBRTE_VIRTIO_PMD=n' '/download/dpdk/config/common_linuxapp'")
    os.system('cd /download/dpdk; make install T=x86_64-native-linuxapp-gcc')

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

print "dpdk compiled"
os.system("echo 'dpdk compiled' >> /tmp/new_out.log")
