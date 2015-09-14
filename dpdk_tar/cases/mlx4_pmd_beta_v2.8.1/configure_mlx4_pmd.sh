#!/bin/bash

usage()
{
	echo "./configure_mlx4_pmd.sh -s kvm/nosriov [-p <PAGE_SIZE>] [-n <HUGE PAGES NUM>] [-o <enable optimized steering mode>]"
} 

if [ $# -eq 0 ]
then
	usage 
	exit
fi

SYS="NULL"
PAGE_SIZE=`cat /proc/meminfo | grep Hugepagesize | awk '{ print $2 }'`
PAGE_NUM=0
PROMISC_OPT=0

while getopts ":hs:p:n:o" OPTION
do
	case $OPTION in
	h)
		usage
		exit 1
		;;
	s)
		SYS=$OPTARG
		if [ "$SYS" != "kvm" ] &&  [ "$SYS" != "nosriov" ] 
		then
			usage
        		exit 1
		fi
		;;	
	p)	
		PAGE_SIZE=$OPTARG	
		;;
	n)
		PAGE_NUM=$OPTARG
		;;
	o)
		PROMISC_OPT=1
		;;
	?)
		echo "Invalid option"
		usage
                exit 1
		;;
	esac
done

shift $(($OPTIND - 1))

if [ "$SYS" == "NULL" ]
then
	usage
	exit 1
fi

if [ "$SYS" == "kvm" ]
then 
	numa_nodes=1
elif [ $SYS == "nosriov" ]
then
	numa_nodes=2
fi

# Enable hugepages if needed
if [ $PAGE_NUM -eq 0 ]
then
	let "PAGE_NUM = (2048*2048)/$((PAGE_SIZE))"
fi


for (( N=0; N<$((numa_nodes)); N++ ))
do
        NR_HP=$(cat /sys/devices/system/node/node$N/hugepages/hugepages-"$PAGE_SIZE"kB/nr_hugepages)
        if [ $NR_HP -lt $PAGE_NUM ]; then
		echo "$PAGE_NUM pages with size $PAGE_SIZE will be configured"
                echo $PAGE_NUM > /sys/devices/system/node/node$N/hugepages/hugepages-"$PAGE_SIZE"kB/nr_hugepages
        fi
done
mkdir -p /mnt/huge
HTLB_MOUNTED=$( mount | grep "type hugetlbfs" | wc -l)
if [ $HTLB_MOUNTED -eq 0 ]; then
        mount -t hugetlbfs hugetlb /mnt/huge
fi

OFED_VERSION=`ofed_info -s`

# Enable flow steering
if [ "$OFED_VERSION" != "MLNX_OFED_LINUX-2.3-1.0.1:" ] && [ "$OFED_VERSION" != "MLNX_OFED_LINUX-2.3-2.0.0:" ] && [ "$OFED_VERSION" != "MLNX_OFED_LINUX-2.4-1.0.0:" ]
then
	echo "Installed OFED version is not 2.4-1.0.0. Please reinstall OFED version "
    exit
fi

FS=`grep "options mlx4_core log_num_mgm_entry_size" "/etc/modprobe.d/mlnx.conf" | wc -l`
if [ $FS -ne 0 ]; then
	FS=`grep "options mlx4_core log_num_mgm_entry_size" "/etc/modprobe.d/mlnx.conf" | awk -F= '{ print $2 }'`
fi

color='\e[0;34m'
NC='\e[0m'

if [ $PROMISC_OPT -eq 0 ]; then
	if [ $FS -eq -1 ]; then
		exit
	fi

	if [ $FS -eq 0 ]; then #Flow steering is not defined
		echo options mlx4_core log_num_mgm_entry_size=-1 >> /etc/modprobe.d/mlnx.conf
	elif [ $FS -eq "-7" ]; then #A0 Flow steering is defined
		echo -e "${color}Promiscuous optimization is disabled${NC}" 
	 	sed -i '/options mlx4_core log_num_mgm_entry_size=-7/c\options mlx4_core log_num_mgm_entry_size=-1' "/etc/modprobe.d/mlnx.conf";
	fi

	echo -e "${color}Please run /etc/init.d/openibd restart${NC}"

else  #promisciouse optimization is needed
	if [ $FS -eq -7 ]; then
                exit
	fi

	if [ $FS -eq 0 ]; then #Flow steering is not defined
                echo options mlx4_core log_num_mgm_entry_size=-7 >> /etc/modprobe.d/mlnx.conf
     	elif [ $FS -eq "-1" ]; then #B0 Flow steering is defined
		sed -i '/options mlx4_core log_num_mgm_entry_size=-1/c\options mlx4_core log_num_mgm_entry_size=-7' "/etc/modprobe.d/mlnx.conf";
     	fi

	echo  -e "${color}Promiscuous optimization will be enabled" 
	echo  -e "In this mode, traffic to the specific port MAC will not be recived."
        echo  -e "For more information please refer to RN"
        echo  -e "Please run /etc/init.d/openibd restart${NC}"
fi

