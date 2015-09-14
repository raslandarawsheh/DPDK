#!/usr/bin/python
try:
    import os
    import getopt
    import sys
    import socket
    import time
    import subprocess
    import signal
    import datetime
    import random
    import thread
    import threading
    import pexpect
    import re 
    import thread
    from socket import *
    import fcntl
    import struct

except Exception, e:
    print ("-E- can not import file %s" %e)
    sys.exit(1)

os.system("export COVFILE=/tmp/clean.cov")

BUF_LEN          = 5 
INVALID_SOCKET   = 0
accepted_sock    = INVALID_SOCKET
connect_sock     = INVALID_SOCKET
ip_hw = None
mtu_sizes = [1024, 2048, 4096, 9216]
mac_addresses = ["FA:FA:FA:FA:FA:FA", "FA:FA:FA:FA:FA:FB", "FA:FA:FA:FA:FA:FC"] 
ports_status = {}
flag = True
checksum_flags = [False, False, False, False, False] #checksum_flags = [IP, UDP, TCP, VXLAN_IP, VXLAN_TCP]
kvm = False
vmware = False
master_rc = False
offloaded = False
generator_device = None
generator_port = None
testpmd = '/download/dpdk-1.8.0/x86_64-native-linuxapp-gcc/build/app/test-pmd/testpmd'
testpmd_master_rc = '/x86_64-native-linuxapp-gcc/build/app/test-pmd/testpmd'
pmd = '/download/pmd-dev-librte_pmd_mlx4/librte_pmd_mlx4.so'
mtuset_pmd = '/download/pmd-dev-librte_pmd_mlx4.mtuset/librte_pmd_mlx4.so'
checksum_pmd = '/download/pmd-dev-librte_pmd_mlx4.checksum/librte_pmd_mlx4.so'
mtuset_and_checksum_pmd = '/download/pmd-dev-librte_pmd_mlx4.mtuset.checksum/librte_pmd_mlx4.so'
pmd_debug = '/download/pmd-dev-librte_pmd_mlx4.debug/librte_pmd_mlx4.so'
mtuset_pmd_debug = '/download/pmd-dev-librte_pmd_mlx4.mtuset.debug/librte_pmd_mlx4.so'
checksum_pmd_debug = '/download/pmd-dev-librte_pmd_mlx4.checksum.debug/librte_pmd_mlx4.so'
mtuset_and_checksum_pmd_debug = '/download/pmd-dev-librte_pmd_mlx4.mtuset.checksum.debug/librte_pmd_mlx4.so'
recvinline_pmd = '/download/pmd-dev-librte_pmd_mlx4.recvinline/librte_pmd_mlx4.so'
recvinline_pmd_debug = '/download/pmd-dev-librte_pmd_mlx4.recvinline.debug/librte_pmd_mlx4.so'

random_mac = "FA:FA:FA:FA:FA:FA"
class Bcolors:
    """
    Class : Bcolors
    Description : Set terminal color to help the user
    """

    HELP	= '\033[96m'
    HEADER	= '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL	= '\033[91m'
    ENDC	= '\033[0m'
    RESET	= '\033[37m'

def run_tcpdump(interface):
    global ports_status
    global flag
    pid = None
    cmd = "tcpdump -i " + interface + " -vvv "
    process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while pid == None:
        pid = process.pid
    ports_status[interface]=[pid]
    print "process PID for %s is %s" %(interface, pid)
    time.sleep(10)
    out = process.stdout.read()
    err = process.stderr.read()
    
    while(flag == False):
        pass
    flag = False
    ports_status[interface].append(str(err) + str(out))
    flag = True


def run_command (cmd):
    try:
        fd = os.popen(cmd)
        output = fd.read()
        rc = fd.close()
    except Exception, e:
                vl.EXCEPTION("run_command Failed (%s), cmd %s" % (str(e), str(cmd)))
                return (1, None)

    if (rc != None):
                rc = 1
    else:
                rc = 0

    return (rc, output)

def tcp_client(ip, port):
    """
    Function : tcp_client
    Description : Create a TCP client to sync between server and client
    Return value : None
    """
    serverHost = ip 
    serverPort = port
    s = socket(AF_INET, SOCK_STREAM) # create a TCP socket
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.connect((serverHost, serverPort)) # connect to server on the port
    global connect_sock
    connect_sock = s

def tcp_server(ip, port):
    """
    Function : tcp_server
    Description : Create a TCP server to sync between server and client
    Return value : None
    """
    myHost = ip
    myPort = port
    s = socket(AF_INET, SOCK_STREAM) # create a TCP socket
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((myHost, myPort)) # bind it to the server port
    s.listen(5) # allow 5 simultaneous
    # pending connections
    connection, address = s.accept() # connection is a new socket
    global accepted_sock
    accepted_sock = connection
def addMacWithVlanFilter(is_server,child,srcMac,ip,cip_port1):
    """
    Function: addMacWithVlanFilter
    Function : adding mac's with VLAN Filtering
    return value : None
    """
    MAC_A ="FA:FA:FA:FA:FA:FA"
    MAC_B ="FA:FA:FA:FA:FA:F9"
    global accepted_sock
    if is_server:
        print "adding MAC addres A \nadding three VLAN filters 4, 5 and 6 \nadding MAC address B"
        child.sendline("mac_addr add 0 " + MAC_A)  # adding first MAC address
        child.sendline("mac_addr add 1 " + MAC_A)
        child.sendline("rx_vlan add  4 0")                   # adding three VLAN filters    
        child.sendline("rx_vlan add  4 1")
        child.sendline("rx_vlan add  5 0")
        child.sendline("rx_vlan add  5 1")
        child.sendline("rx_vlan add  6 0")
        child.sendline("rx_vlan add  6 1")
        child.sendline("mac_addr add 0 " + MAC_B) #adding MAC address
        child.sendline("mac_addr add 1 " + MAC_B)
        accepted_sock.send("SYNC1")
        old_rx = 0
        old_tx = 0
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 3:
                print "Testpmd did not received packet for vlans with MAC_A :    fail"
                failPrint()
                sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd receivd packets for vlans with MAC_A :    pass "
        old_rx = cur_rx
        old_tx = cur_tx
        accepted_sock.send("SYNC2")
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 3:
                print "Testpmd did not received packet for vlans with MAC_B :    fail"
                failPrint()
                sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd receivd packets for vlans with MAC_B :    pass "
        old_rx = cur_rx
        old_tx = cur_tx
        print "removing vlan 5" 
        child.sendline("rx_vlan rm  5 0") # removing vlan 5 
        child.sendline("rx_vlan rm  5 1")
        accepted_sock.send("SYNC3")
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 0:
                if multicast :
                    pass
                else :
                
                    print "Testpmd received packet for vlan 5  with MAC_A and MAC_B after removing it :    fail"
                    failPrint()
                    sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd didn't receve packets for vlan 5 after removing it with both MACs :    pass "
        accepted_sock.send("SYNC4")
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 4:
                print "Testpmd did not receive packets for vlans 4 and 6 after removing vlan 5  with MAC_A and MAC_B :    fail"
                failPrint()
                sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd received packets for vlan 4 and 6 after removing vlan 5 with MAC_A and MAC_B :    pass "
        print "removing MAC_A"
        child.sendline("mac_addr remove 0 "+ MAC_A) # removing MAC_A
        child.sendline("mac_addr remove 1 "+ MAC_A)
        accepted_sock.send("SYNC5")
        old_rx = cur_rx
        old_tx = cur_tx
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 0:
                if multicast :
                    pass
                else :
                    
                    print "Testpmd  received packets for vlans 4 and 6 with MAC_A after removing vlan 5 and MAC_A :    fail"
                    failPrint()
                    sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd didn't receive packets for MAC_A with any vlan :    pass"
        accepted_sock.send("SYNC6")
        old_rx = cur_rx
        old_tx = cur_tx
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 2:
                print "Testpmd didn't receive packets for vlans 4 and 6 with MAC_B after removing vlan 5 and MAC_A :    fail"
                failPrint()
                sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        print "Testpmd received packets for vlan 4 and 6  with MAC_B after removing vlan 5 and MAC_A :    pass  "
        accepted_sock.send("SYNC7")
        old_rx = cur_rx
        old_tx = cur_tx
        vlan_data = accepted_sock.recv(BUF_LEN)
        if vlan_data:
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 0:
                if multicast :
                    pass
                else :
                    
                    print "Testpmd received packet for vlans 5 with MAC_B after removing vlan 5 and MAC_A :    fail"
                    failPrint()
                    sys.exit(1)
        else:
            print "Sync : Recv error"
            failPrint()
            sys.exit(1)
        passPrint()
        sys.exit(0)
    else:
        vlanFiltering ='4'
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,4)
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,5)
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,6)
        data = connect_sock.recv(BUF_LEN)
        if data != None:
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            time.sleep(1)
        else :
            print "sync Error : MAC_A"
            failPrint()
            sys.exit(1)
        
        connect_sock.send("SYNC1")
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,4)
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,5)
        generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,6)
        data = connect_sock.recv(BUF_LEN)
        if data != None:
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            print "sent 3 packets"
            time.sleep(1)
        else :
            print "sync Error : MAC_A"
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC2")
        data = connect_sock.recv(BUF_LEN)
        if data != None:
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,5)
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
        else :
            print "sync Error : VLAN 5 "
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC3")
        data = connect_sock.recv(BUF_LEN)
        if data != None :
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,4)
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_A, ip, cip_port1,6)
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            time.sleep(1)
        else :
            print "sync Error : VLAN 4 and 6 "
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC4")
        data = connect_sock.recv(BUF_LEN)
        if data != None :
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            time.sleep(1)
        else :
            print "sync Error : after MAC_A removal "
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC5")
        data = connect_sock.recv(BUF_LEN)
        if data != None :
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,4)
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,6)
            cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
            cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
        else :
            print "sync Error : after MAC_A removal "
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC6")
        data = connect_sock.recv(BUF_LEN)
        if data != None :
            generate_vlan_filter_file(vlanFiltering,srcMac, MAC_B, ip, cip_port1,5)
            cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
            os.popen(cmd)
        else :
            print "sync Error : after MAC_A removal "
            failPrint()
            sys.exit(1)
        connect_sock.send("SYNC7")
        passPrint()
        sys.exit(0)

def usage():
    """
    Function : usage
    Description : Usage is a function to print the help menu
    Return value : None
    """
    print Bcolors.HELP + "\thelp		\t| h	: Tool help and exit"
    print Bcolors.HELP + "\tserver		\t| s	: Is server (default No)" 
    print Bcolors.HELP + "\tip		\t	: IP of the server interface"
    print Bcolors.HELP + "\tmip		\t	: IP of mangemet interface"
    print Bcolors.HELP + "\tcip_port1		\t	: IP of the client interface port1"
    print Bcolors.HELP + "\tcip_port2           \t      : IP of the client interface port2"
    print Bcolors.HELP + "\tport		\t	: Port number"
    print Bcolors.HELP + "\tportUpInInit	\t	: The port link is brought up during init"
    print Bcolors.HELP + "\tmtuSet		\t	: Set the mtu for the giving amount for mellanox interface"
    print Bcolors.HELP + "\tvlanFiltering	\t	: Set vlan filter on or off"
    print Bcolors.HELP + "\tmtuSetMultipleTimes \t	: Set MTU multiple times at run time"
    print Bcolors.HELP + "\tautonegotiateEthtool \t	: Set autonegotiate value through Ethtool"
    print Bcolors.HELP + "\trxEthtool 		\t      : Set RX value through Ethtool"
    print Bcolors.HELP + "\ttxEthtool           \t      : Set TX value through Ethtool"
    print Bcolors.HELP + "\tdmfs           \t      :  Select the mode, A0 or B0"
    print Bcolors.HELP + "\tVXLAN           \t      UC: Send UC VXLAN Traffic via Scapy"
    print Bcolors.HELP + "\t	           \t       MC: Send MC VXLAN Traffic via Scapy"
    print Bcolors.HELP + "\tm           \t          PMd compiled with -m"
    print Bcolors.HELP + "\tset_flow_control_at_once	\t Set flow control parameters rx/tx at once"
    print Bcolors.HELP + "\tchecksum    \t Takes list of options (IP,UDP,TCP, VXLAN) to set bad checksum, like 'IP' or 'IP,UDP' or 'IP,TCP' or 'UDP' or 'TCP' ov VXLAN"
    print Bcolors.HELP + "\tkvm           \t          KVM machine"
    print Bcolors.HELP + "\tadd_mac	\t		Add invalid mac from pmd"
    print Bcolors.HELP + "\tvlanFiltering           \t      1: Filtering on one vlan (Vlan 4)"
    print Bcolors.HELP + "\t               \t       	    2: Filtering on two vlan (Vlan 4,5)"
    print Bcolors.HELP + "\tvmware           \t          VMware machine"
    print Bcolors.HELP + "\tmaster_rc           \t          Use the master DPDK RC "
    print Bcolors.HELP + "\tstatic           \t          Use the static compiled libibverbs & libmlx4 "
    print Bcolors.HELP + "\tsg1           \t          Use the DPDK compiled with SGE_WR_N=1"
    print Bcolors.HELP + "\toffloaded           \t Use hardware checksum offloading"

def parse(tuple):
    """
    Function : parse
    Description : Parse is a method to parse the parameters, and produce the executed test command line
    Todo: Support unlimited option
    """

    global accepted_sock, connect_sock, ip_hw, kvm, generator_device, generator_port, vmware, master_rc, testpmd, offloaded
    
    outputCommand = "/hpc/home/USERS/halsayyed/get_rxtx_throughput.sh mlx4_1 1"
    ip       	= None
    port        = 20202
    is_s        = False
    exit_status = 0
    mip = None
    cip_port1 = None
    cip_port2 = None
    invalidMac = False
    setPromisc = True
    dest_ip = "unicast"
    add_mac = False
    rxq = 1 
    txq = 1
    disable_rss = False
    rssQueuesFlage =  False
    destMac  = ""
    vlan = False 
    portUpInInit = False
    mtuSet = None
    vlanFiltering = None
    mtuSetMultipleTimes = False
    autonegotiateEthtool = None 
    rxEthtool = None
    txEthtool = None 
    device = None
    dmfs = None
    vxlan = None
    msgSize = 64
    recv_inline = None
    set_flow_control_at_once = None
    checksum = None
    c = False
    m = False
    d = False
    addMacMultipleTimes = False
    ipv6 = False
    static = False
    sg1 = False
    multicast = False
    try:
        opts, extraparams = getopt.getopt(tuple, "hsF:f:i:a:A:E:",['server', 'vxlan=', 'ip=', 'port=', 'mip=', 'cip_port1=', 'cip_port2=', 'set_flow_control_at_once=', 'invalidMac', 'setPromisc', 'dest_ip=', 'add_mac', 'rxq=', 'txq=', 'disable_rss', 'rssQueuesFlage', 'vlan', 'portUpInInit', 'mtuSet=', 'vlanFiltering=', 'mtuSetMultipleTimes', 'autonegotiateEthtool=', 'rxEthtool=', 'txEthtool=', 'device=', 'dmfs=','recv-inline','msg-size=', 'm','checksum=', 'kvm','d','c','addMacMultipleTimes', 'vmware', 'master_rc', 'ipv6', 'static', 'sg1', 'multicast', 'offloaded'])

        if  (len(extraparams) != 0 or len(opts) == 0) :
            print("-E- Invalid extra argument:" )
            usage()
            sys.exit(1)
        
        for o,p in opts:
            if o in ['-h','--help']:
                usage()
                sys.exit(exit_status)

            elif o in ['-s', '--server']:
                is_s = True

            elif o in ['--dmfs']:
                dmfs = p
             
            elif o in ['--static']:
                static = True

            elif o in ['--sg1']:
                sg1 = True
    
            elif o in ['--kvm']:
                kvm = True

	    elif o in ['--vmware']:
                vmware = True
				
            elif o in ['--master_rc']:
                master_rc = True

            elif o in ['--m']:
                m = True

            elif o in ['--vxlan']:
                vxlan = p
                
            elif o in ['--set_flow_control_at_once']:
                set_flow_control_at_once = p

            elif o in ['-i', '--ip']:
                ip = p

            elif o in ['--cip_port1']:
                cip_port1 = p

            elif o in ['--cip_port2']:
                cip_port2 = p

            elif o in ['--invalidMac']:
                invalidMac = True
            elif  o in ['--mip']:
                mip = p
            elif  o in ['--device']:
                device = p
            elif o in ['--setPromisc']:
                setPromisc = False
            elif o in ['--dest_ip']:
                dest_ip = p 
            elif o in ['--add_mac']:
                add_mac = True
            elif o in ['--rxq']:
                rxq = p 
            elif o in ['--txq']:
                txq = p
            elif o in ['--disable_rss']:
                disable_rss = True
            elif o in ['--rssQueuesFlage']:
                rssQueuesFlage = True 
            elif  o in ['--vlan']:
                vlan = True 
            elif o in ['--portUpInInit']:
                portUpInInit = True
            elif o in ['--mtuSet']:
                mtuSet = p
            elif o in ['--vlanFiltering']:
                vlanFiltering = p
            elif o in ['--mtuSetMultipleTimes']:
                mtuSetMultipleTimes = True
            elif o in ['--autonegotiateEthtool']:
                autonegotiateEthtool = p
            elif o in ['--rxEthtool'] :
                rxEthtool = p
            elif o in ['--txEthtool'] :
                txEthtool = p
	    elif o in ['--msg-size']:
		msgSize = p
	    elif o in ['--recv-inline']:
		recv_inline = True
            elif o in ['--checksum']:
                checksum = p
            elif o in ['--d']:
                d = True
            elif o in ['--c']:
                c = True
            elif o in ['--addMacMultipleTimes']:
                addMacMultipleTimes = True
            elif o in ['--ipv6']:
                ipv6 = True
            elif o in ['--multicast']:
                multicast = True
            elif o in ['--offloaded']:
                offloaded = True              
            else:
                print("-E- Invalid argument:" )
                usage()
                sys.exit(1)

    except Exception, e:
        print e.message
        usage()
        exit_status = 1
        sys.exit(exit_status)
        
    '''
    testpmd='/download/dpdk2.0-mlx4_pmd_2.8.4'
    if d == False:
        if(m and not c):
            testpmd+='.mtuset'
        elif(c or checksum) and not m:
            testpmd+='.checksum'
        elif (c or checksum) and m:
            testpmd+='.mtuset.checksum'
        elif recv_inline == True:
            testpmd+='.recvinline'
        else:
            pass
    else:
        if(m and not c):
            testpmd+='.mtuset.debug'
        elif (c or checksum) and not m:
            testpmd+='.checksum.debug'
        elif (c or checksum) and m:
            testpmd+='.mtuset.checksum.debug'
        elif recv_inline == True:
            testpmd+= '.recvinline.debug'
        else:
            testpmd+='.debug'

    testpmd+='/dpdk2.0-mlx4/x86_64-native-linuxapp-gcc/app/testpmd'
    '''
    '''
    mode_file = open('/sys/module/mlx4_core/parameters/log_num_mgm_entry_size','r')
    mode = str(mode_file.read()).strip()
    mode = '-1'
    print "modeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",mode
    '''
    if master_rc:
#        if static:
#            if sg1:
#                serverCommandLine = "/download/dpdk_master_static.sg1" 
#            elif d:
#                serverCommandLine = "/download/dpdk_master_static.debug"
#            else:
#               serverCommandLine = "/download/dpdk_master_static.default"
#        else:
#            if sg1:
#                serverCommandLine = "/download/dpdk_master_dynamic.sg1"
#            elif d:
#                serverCommandLine = "/download/dpdk_master_dynamic.debug"
#            else:
#               serverCommandLine = "/download/dpdk_master_dynamic.default"
	serverCommandLine = "/download/dpdk_master"
        serverCommandLine += testpmd_master_rc + " -n 4 "
    else:
        serverCommandLine = testpmd + " -n 4 "
    
#    master_rc = True
    if kvm:
        generator_device = 'mlx4_0'
        generator_port = '2'
    elif vmware:
	generator_device = 'mlx4_2'
	generator_port = '2'
    else:
        generator_device = 'mlx4_1'
        generator_port = '2'

    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "

    if recv_inline == True and is_s == True:
        os.environ["MLX4_INLINE_RECV_SIZE"] = str(msgSize)
	
    if is_s:
        tcp_server(mip, int(port + 100))
        os.system("mst start")
        ip_hw = getHwAddr(getNameOfIp(ip))
        if not (kvm or vmware):
            whitelisted = getWhiteListed(device)
        '''
        
        if kvm:
            serverCommandLine += " -c 0xf "
	elif vmware:
	    serverCommandLine += " -c 0xf "
        else:
            serverCommandLine += " -c 0xf "
        '''    
        if (int(rxq) == 4 and int(txq) == 4) or (int(rxq) == 8 and int(txq) == 8):
            serverCommandLine += " -c 0xfff "
        else:
            serverCommandLine += " -c 0xff "

        if not (kvm or vmware):
                #serverCommandLine += " -w " + str(whitelisted)  # need to check this again when installing new Ofed 
            pass
        if master_rc == False:
            if d == False:
                if(m and not c):
                    serverCommandLine += " -d " + mtuset_pmd 
                elif(c or checksum) and not m:
                    serverCommandLine += " -d " + checksum_pmd 
                elif (c or checksum) and m:
                    serverCommandLine += " -d " + mtuset_and_checksum_pmd
                elif recv_inline == True:
                    serverCommandLine += " -d " + recvinline_pmd
                else:
                    serverCommandLine += " -d " + pmd 
            else:
                if(m and not c):
                    serverCommandLine += " -d " + mtuset_pmd_debug 
                elif (c or checksum) and not m:
                    serverCommandLine += " -d " + checksum_pmd_debug 
                elif (c or checksum) and m:
                    serverCommandLine += " -d " + mtuset_and_checksum_pmd_debug 
                elif recv_inline == True:
                    serverCommandLine += " -d " + recvinline_pmd_debug
                else:
                    serverCommandLine += " -d " + pmd_debug 

	if kvm or vmware:
            serverCommandLine += " -- --burst=64 --txd=256 --rxd=256 --mbcache=512 --portmask 0x3 -i "
	else:
	    serverCommandLine += " -- --numa --burst=64 --txd=256 --rxd=256 --mbcache=512 --portmask 0x3 -i "
        '''
        if kvm:
            serverCommandLine += " --coremask=0xe "
	elif vmware:
	    serverCommandLine += " --coremask=0xe "
        else:
            serverCommandLine += " --coremask=0xe "
        '''
        if (int(rxq) == 4 and int(txq) == 4) or (int(rxq) == 8 and int(txq) == 8):
            serverCommandLine += " --coremask=0xffe "
        else:
            serverCommandLine += " --nb-cores=4 "

        if rxq != 1 or txq != 1:
            if(rssQueuesFlage):
                serverCommandLine += " --rxq=" + str(rxq) + " --txq=" + str(txq)
            else:
                serverCommandLine += " --rxq=" + str(rxq) + " --txq=" + str(txq) #+ " --nb-cores=2"

        if mtuSetMultipleTimes:
            #if not master_rc:
            if kvm :
                serverCommandLine += " --mbuf-size=5000"
            else :
                serverCommandLine += " --mbuf-size=2400"

	if checksum != None:
	    serverCommandLine += " --enable-rx-cksum"
    if is_s:
	
        
#       if kvm or vmware:
#           os.system(pmd.split('librte_pmd_mlx4/librte_pmd_mlx4/librte_pmd_mlx4.so')[0] + "/configure_mlx4_pmd.sh -s kvm")
#       else:
#	    if dmfs == 'A0':
#               os.system("/download/configure_mlx4_pmd.sh -s nosriov")
#		os.system("/etc/init.d/openibd restart")
#		time.sleep(10)
#	    elif dmfs == 'B0':
#		os.system("/download/configure_mlx4_pmd.sh -s nosriov")
#		os.system("/etc/init.d/openibd restart")
#		time.sleep(10)
        
        print "Server Side ......................................................... mip %s port %s " %(mip, port)
        #Send MAC address to client
        try:
	    print "Dest MAC is  ", getHwAddr(getNameOfIp(ip))
            accepted_sock.send(getHwAddr(getNameOfIp(ip)))
        except Exception, e:
            print "HwAddr Send Error ...."
            sys.exit(1)
    else:
        print "Client Side ......................................................... mip %s port %s" %(mip, port)
        tcp_client(mip, int(port + 100))
        #Get MAC address from server
        destMac = connect_sock.recv(17)
	clientCommandLine += " --dest_mac=" + destMac

        if invalidMac == True:
            regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')
            datal = regex.findall(clientCommandLine)
            clientCommandLine = clientCommandLine.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

#        if add_mac == True:
#            regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')
#            datal = regex.findall(clientCommandLine)
#            clientCommandLine = clientCommandLine.replace(datal[0],'--dest_mac=%s'%(random_mac))
	  
    if disable_rss:
        serverCommandLine += ' --disable-rss'

    print "serverCommandLine:", serverCommandLine 

#    if dest_ip == "unicast":
#        clientCommandLine = clientCommandLine + " --dest_ip "+ ip
#    if dest_ip == "multicast":
#        clientCommandLine = clientCommandLine + " --dest_ip 224.10.10.10"
    
    return clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip_port1,cip_port2,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,vxlan,set_flow_control_at_once,checksum, addMacMultipleTimes, ipv6, multicast

def add_route(ip):
    cmd = "route add -net 224.0.0.0 netmask 240.0.0.0 dev " + getNameOfIp(ip)
    os.system(cmd)

def check_cores():
    cmd = "ls | grep 'core.*' | wc -l"
    rc, output = run_command(cmd)

    cmd = "ls | grep 'core.*'"
    rc, cores = run_command(cmd)

    number_of_cores = output.split('\n')[0]
    
    if(int(number_of_cores) != 0):
        cmd = "mv 'core.*' ../"
        rc, out = run_command(cmd)
        print "cores moved to ../"

    return number_of_cores, cores

def passPrint():
    """
    Function : passPrint
    Description : Pass message print 
    Return value : None
    """
    num, cores = check_cores()
    if(int(num) != 0):
        print "The tests passed but there is %s cores" %num
        print "The cores:"
        print cores
        failPrint()
        sys.exit(1)

    print Bcolors.OKGREEN + "\t\t\t---------------------Test Result---------------------"
    print Bcolors.OKGREEN + "\t\t\t                    [TEST PASSED]                    "
    print Bcolors.OKGREEN + "\t\t\t-----------------------------------------------------" + Bcolors.RESET

def failPrint():
    """
    Function : failPrint
    Description : fail message print
    Return value : None
    """
    num, cores = check_cores()
    if(int(num) != 0):
        print "The tests failed but there is %s cores" %num
        print "The cores:"
        print cores

    print Bcolors.FAIL + "\t\t\t---------------------Test Result---------------------"
    print Bcolors.FAIL + "\t\t\t                    [TEST FAILED]                    "
    print Bcolors.FAIL + "\t\t\t-----------------------------------------------------" + Bcolors.RESET

def generate_vxlan_test_file(traffic, srcMac, destMac, ip, cip_port1, vlan, invalidMac):
    if invalidMac == True:
	destMac = "FA:FA:FA:FA:FA:FA"
    scapy_file = open('vxlan.txt','w')
    scapy_file.write("% VXLAN Tests\n")
    scapy_file.write("* Tests for the Scapy VXLAN layer\n")
    scapy_file.write("+ Informations\n")
    scapy_file.write("= Build a VXLAN packet with VNI of 42\n")
    scapy_file.write("load_contrib('vxlan')\n")
    scapy_file.write("str(UDP(sport=1024, dport=4789, len=None, chksum=None)/VXLAN(flags=0x08, vni=42)) == '\\x04\\x00\\x12\\xb5\\x00\\x10\\x00\\x00\\x08\\x00\\x00\\x00\\x00\\x00\\x2a\\x00'\n")
    scapy_file.write("\n= Verify VXLAN Ethernet Binding\n")
    scapy_file.write("load_contrib('vxlan')\n")
    scapy_file.write("str(VXLAN(vni=23)/Ether(dst='11:11:11:11:11:11', src='11:11:11:11:11:11', type=0x800)) == '\\x08\\x00\\x00\\x00\\x00\\x00\\x17\\x00\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x11\\x08\\x00'\n")
    scapy_file.write("\n= Send Packet via Scapy\n")
    scapy_file.write("load_contrib('vxlan')\n")
    scapy_file.write("data= 'Data to be sent via Scapy'\n")
    if vlan == False:
        if (traffic == 'RSS'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='224.10.10.10', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, cip_port1))
            scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
            scapy_file.write("p =IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(ip, cip_port1))
            scapy_file.write("send(p) \n")
            scapy_file.close()
            return

        if(traffic == 'UC'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, cip_port1, ip))
        elif(traffic == 'MC'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='224.10.10.10', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, cip_port1))
        scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
        scapy_file.close()

    else:
        first_octet = ip.split('.')[0]
        vlan_ip = ip.replace("%s." %first_octet,"100.")
        first_octet = cip_port1.split('.')[0]
        vlan_cip = cip_port1.replace("%s." %first_octet,"100.")
        if (traffic == 'RSS'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/Dot1Q(vlan=4)/IP(dst='224.10.10.10', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, vlan_cip))
            scapy_file.write("sendp(p, iface='%s.4')\n" %(getNameOfIp(cip_port1)))
            scapy_file.write("p = Dot1Q(vlan=4)/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(vlan_ip, vlan_cip))
            scapy_file.write("send(p) \n")
            scapy_file.close()
            return

        if(traffic == 'UC'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/Dot1Q(vlan=4)/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, vlan_ip, vlan_cip))

        elif(traffic == 'MC'):
            scapy_file.write("p =Ether(src='%s', dst='%s')/Dot1Q(vlan=4)/IP(dst='224.10.10.10', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42) \n" %(srcMac, destMac, vlan_cip))

        scapy_file.write("sendp(p, iface='%s.4')\n" %(getNameOfIp(cip_port1)))

        scapy_file.close()

def generate_vlan_filter_file(vlanFiltering,srcMac, destMac, ip, cip_port1,vlan_tag):
    scapy_file = open('vlanFilter%s.txt'%(vlan_tag),'w')
    scapy_file.write("% vlanFilter Tests\n")
    scapy_file.write("+ Informations\n")
    scapy_file.write("\n= Send Packet via Scapy\n")
    scapy_file.write("data= 'Data to be sent via Scapy'\n")
    scapy_file.write("p =Ether(src='%s', dst='%s')/Dot1Q(vlan=%s)/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac, vlan_tag,ip, cip_port1))
    scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
    scapy_file.close()

def generate_bad_checksum_packet(checksum_flags, srcMac, destMac, ip, cip_port1, cip_port2):
    scapy_file = open('checksum.txt','w')
    scapy_file.write("% Checksum Tests\n")
    scapy_file.write("+ Informations\n")
    scapy_file.write("\n= Send Packet via Scapy\n")
    scapy_file.write("data= 'Data to be sent via Scapy'\n")
    if checksum_flags[3] == True or checksum_flags[4] == True:
	scapy_file_sniff = open('sniffing.txt','w')
	scapy_file_sniff.write("+ Informations\n")
        scapy_file_sniff.write("= Build a VXLAN packet with VNI of 42\n")
	scapy_file_sniff.write("load_contrib('vxlan') \n")
        scapy_file_sniff.write("sniff(iface='%s', prn=lambda x: x.show2(), count = 1) \n" %(getNameOfIp(cip_port2)))
	scapy_file_sniff.close()

    if checksum_flags[1] == True:
        scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[2] == True:
	scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/TCP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[0] == True:
        scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[3] == True:
	scapy_file.write("load_contrib('vxlan')\n")
	scapy_file.write("p = Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/VXLAN(vni=42)/Ether()/IP()/TCP(sport=1338,dport=4788) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[4] == True:
        scapy_file.write("load_contrib('vxlan')\n")
        scapy_file.write("p = Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/VXLAN(vni=42)/Ether()/IP()/TCP(sport=1338,dport=4788) \n" %(srcMac, destMac, ip, cip_port1))
        
    if(checksum_flags[0] == True):
	scapy_file.write("p.chksum = 0xabc \n")
        #scapy_file.write("p.chksum = 0x0 \n")
    if checksum_flags[1] == True:
	scapy_file.write("p[UDP].chksum = 0xabc \n")
        #scapy_file.write("p[UDP].chksum = 0x0 \n")
    if checksum_flags[2] == True:
        scapy_file.write("p[TCP].chksum = 0xabc \n")
    if checksum_flags[3] == True:
	scapy_file.write("p.show2() \n")
        scapy_file.write("p[VXLAN][IP].chksum = 0xabc \n")
    if checksum_flags[4] == True:
        scapy_file.write("p[VXLAN][TCP].chksum = 0xabc \n")

        #scapy_file.write("p[TCP].chksum = 0x0 \n")
    scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
    scapy_file.close() 

def generate_ipv6_packet(srcMac, destMac, ip, cip_port1, cip_port2, invalidMac):
    if invalidMac == True:
	destMac = "FA:FA:FA:FA:FA:FA"
    scapy_file = open('IPv6.txt','w')
    scapy_file.write("% IPv6 Tests\n")
    scapy_file.write("+ Informations\n")
    scapy_file.write("\n= Send Packet via Scapy\n")
    scapy_file.write("data= 'Data to be sent via Scapy'\n")
    scapy_file.write("p =Ether(src='%s', dst='%s')/IPv6(dst='2001:db8::1', src='2001:db9::1')/UDP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac))
    scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
    scapy_file.close()

def run_sniffer(eth):
    print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    cmd = "UTscapy -t sniffing.txt -f html -o sniff_output.html -F"
    process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_err = process.stderr.read()
    scapy_ouput = process.stdout.read()

def check_testpmd_out(output):
    port0 = False
    port1 = False

    output_list = output.split('\n')
    for index in range (len(output_list)):
        if "NIC statistics for port 0" in output_list[index]:
            port0 = True
            port1 = False

        if "NIC statistics for port 1" in output_list[index]:
            port1 = True
            port0 = False

        if "RX-packets:" in output_list[index] and port0:
            rx_port0 = output_list[index].split("RX-packets:")[1].split("RX-missed:")[0].strip()
            print "rx_port0 is :",rx_port0

        if "RX-packets:" in output_list[index] and port1:
            rx_port1 = output_list[index].split("RX-packets:")[1].split("RX-missed:")[0].strip()
            print "rx_port1 is :",rx_port1

        if "TX-packets:" in output_list[index] and port0:
            tx_port0 = output_list[index].split("TX-packets:")[1].split("TX-errors:")[0].strip()
            print "tx_port0 is :",tx_port0

        if "TX-packets:" in output_list[index] and port1:
            tx_port1 = output_list[index].split("TX-packets:")[1].split("TX-errors:")[0].strip()
            print "tx_port1 is :",tx_port1

    return rx_port0, rx_port1, tx_port0, tx_port1
            
def runTest():
    """
    Function : runTest
    Description : The main function that will run testpmd tests
    Return value : None
    """
    clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand ,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip_port1,cip_port2,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,vxlan,set_flow_control_at_once,checksum, addMacMultipleTimes, ipv6, multicast  = parse(sys.argv[1:])
    os.system("echo 1024 >  /proc/sys/vm/nr_hugepages")
    ip_first_octet = ip.split('.')[0]
    cip_port1_first_octet = cip_port1.split('.')[0]
    
    if mtuSet != None:
        clientCommandLine += " --mtu " + mtuSet

    if vxlan == 'MC' or vxlan == 'RSS':
        if is_s:
            add_route(ip)
        else:
            add_route(cip_port1)
    if checksum != None:
	print" checksum is   ",  checksum
        checksum_list = checksum.split(',')
        for w in range (len(checksum_list)):
            if "IP" in checksum_list[w] and not "VXLAN" in checksum_list[w]:
	        checksum_flags[0] = True
	    elif "UDP" in checksum_list[w] and not "VXLAN" in checksum_list[w]:
                checksum_flags[1] = True
            elif "TCP" in checksum_list[w] and not  "VXLAN" in checksum_list[w]:
                checksum_flags[2] = True
            elif "VXLAN" in checksum_list[w] and "IP" in checksum_list[w]:
                checksum_flags[3] = True
            elif "VXLAN" in checksum_list[w] and "TCP" in checksum_list[w]:
                checksum_flags[4] = True

	    else:
                print "Error: checksum takes IP, TCP, UDP"
                failPrint()
                sys.exit(1)
    vlan4_packet = None  #packets received from VLAN 4 in testing vlanFiltering
    vlan5_packet = None  #packets received from VLAN 5 in testing vlanFiltering
    if vlanFiltering != None:
	if (not vlanFiltering.isdigit()):
	    print "Errot: vlanFiltering takes scenario number only"
	    failPrint()
            sys.exit(1)

    if is_s == True:
        if portUpInInit:
            ipToAdd = ip.replace("%s." %ip_first_octet,"100.")
            cmd = "ifconfig " + str(getNameOfIp(ip)) + " down"
            cmd2 = "ifconfig " + str(getNameOfIp(ipToAdd)) + " down"
            os.popen(cmd)
            os.popen(cmd2)
        if vlan :
            addVlan(ip)
        if autonegotiateEthtool != None or rxEthtool!= None or txEthtool!= None or set_flow_control_at_once != None:
            autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg = getEthtoolparamteres(getNameOfIp(ip)) 
            
        process2  = subprocess.Popen(outputCommand + " > server.out.tmp &", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        data = accepted_sock.recv(BUF_LEN)
        if data:
            accepted_sock.send("Sync1")
        else:
            print "Sync : Recv error"

        process3 = os.popen("ibdev2netdev | grep Up").read()    #get the names of all ports on the machine
        portNamesOutput = process3.split("\n")
        portNames = [None] * (len(portNamesOutput)-1)

        for w in range (len(portNamesOutput)-1):
             portNames[w] =  portNamesOutput[w].split('==> ')[1].split(' ')[0]

        child = pexpect.spawn(serverCommandLine)
        child.expect('')
        child.sendline("show port info 0")      #get mac address of port 0 using show port info
        child.expect('qinq')
        portInfoOutput = child.before
        portInfoToPrint = portInfoOutput.split("\n")
        for w in range (len(portInfoToPrint)):
            if "MAC address: " in portInfoToPrint[w]:
                MacAddressPortZero = portInfoToPrint[w].split('MAC address: ')[1]

        child.sendline("show port info 1")      #get mac address of port 1 using show port info
        child.expect('qinq')
        portInfoOutput1 = child.before
        portInfoToPrint1 = portInfoOutput1.split("\n")
        for w in range (len(portInfoToPrint1)):
            if "MAC address: " in portInfoToPrint1[w]:
                MacAddressPortOne = portInfoToPrint1[w].split('MAC address: ')[1]
	
	portZeroName = None
	portOneName = None
        for w in range (len(portNames)):                                                        #check which port name has the mac address of port 0
            if MacAddressPortZero.strip().lower() == getHwAddr(portNames[w]).strip().lower():
                portZeroName = portNames[w]

        for w in range (len(portNames)):                                                        #check which port name has the mac address of port 1
            if MacAddressPortOne.strip().lower() == getHwAddr(portNames[w]).strip().lower():
                portOneName = portNames[w]

        if checksum != None:
            port_to_receive_traffic = "0" if portZeroName == getNameOfIp(ip) else "1"

        if autonegotiateEthtool != None or rxEthtool!= None or txEthtool!= None or set_flow_control_at_once != None:
            autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg = getEthtoolparamteres(portZeroName)
 
        if set_flow_control_at_once == "on":
            child.sendline("set flow_ctrl rx on tx on 0 0 0 0 mac_ctrl_frame_fwd on autoneg off 0")
        elif set_flow_control_at_once == "off":
            child.sendline("set flow_ctrl rx off tx off 0 0 0 0 mac_ctrl_frame_fwd off autoneg off 0")
        if rxEthtool == "on":
            child.sendline("set flow_ctrl rx on 0")
        elif rxEthtool == "off":
            child.sendline("set flow_ctrl rx off 0")
        if txEthtool == "on":
            child.sendline("set flow_ctrl tx on 0")
        elif txEthtool == "off":
            child.sendline("set flow_ctrl tx off 0")

        if autonegotiateEthtool != None or rxEthtool!= None or txEthtool!= None or set_flow_control_at_once != None:
            autonegotiateEthtoolOrg,rxEthtoolOrg_portZero_new,txEthtoolOrg_portZero_new = getEthtoolparamteres(portZeroName)
            autonegotiateEthtoolOrg1,rxEthtoolOrg_portOne_new,txEthtoolOrg_portOne_new = getEthtoolparamteres(portOneName)
	
        autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod = getEthtoolparamteres(getNameOfIp(ip))
        if rxEthtool != None or txEthtool != None or set_flow_control_at_once != None:
            checkFlowControl(autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod,autonegotiateEthtoolOrg,rxEthtoolOrg_portZero_new,txEthtoolOrg_portZero_new,rxEthtoolOrg_portOne_new,txEthtoolOrg_portOne_new,rxEthtool,txEthtool,set_flow_control_at_once)
#        if vlanFiltering != None and vlanFiltering == "on":
#            child.sendline("rx_vlan add  all 0")
#            child.sendline("rx_vlan add  all 1")
#        elif  vlanFiltering != None and vlanFiltering == "off":
#            child.sendline("vlan set filter off 0")
#            child.sendline("vlan set filter off 1")
        '''
	if vlanFiltering != None:
	    print "vlanFiltering", vlanFiltering
	    #scenario 1: add only one vlan(4) send packets from two vlans (4,5) and check the output, must receive from 4 only
	    if vlanFiltering == '1':
	        child.sendline("rx_vlan add  4 0")
                child.sendline("rx_vlan add  4 1")
	    #scenario 2: add two vlans (4,5) must recevie packets from both
	    elif vlanFiltering == '2':
		child.sendline("rx_vlan add  4 0")
		child.sendline("rx_vlan add  5 0")
                child.sendline("rx_vlan add  4 1")
                child.sendline("rx_vlan add  5 1")
            #scenario 3:
	    else:
		print "Errot: scenario not added to the test yet"
                failPrint()
                sys.exit(1)
        '''
        
        if mtuSet != None:
            child.sendline("port config mtu 0 "+str(mtuSet))
            child.sendline("port config mtu 1 "+str(mtuSet))
        if setPromisc == False:
            child.sendline("set promisc all off")
        if dest_ip == "multicast" and add_mac == False:
            child.sendline("set allmulti all on")
        elif add_mac:
            child.sendline("set promisc all off")
            child.sendline("mac_addr add 0 " + random_mac)
            child.sendline("mac_addr add 1 " + random_mac)
        elif add_mac and dest_ip == "multicast":
            child.sendline("set promisc all off")
            child.sendline("set allmulti all on")
            child.sendline("mac_addr add 0 " + random_mac)
	else:
	    print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n\nasaaaaa"

################################Check Sum####################################
	if checksum != None:
	    child.sendline("set fwd csum")
            if offloaded:
                if checksum_flags[0] == True:
                    child.sendline("tx_checksum set ip hw 0")
                    child.sendline("tx_checksum set ip hw 1")
                if checksum_flags[1] == True:
                    child.sendline("tx_checksum set udp hw 0")
                    child.sendline("tx_checksum set udp hw 1")
                if checksum_flags[2] == True:
                    child.sendline("tx_checksum set tcp hw 0")
                    child.sendline("tx_checksum set tcp hw 1")
                if checksum_flags[3] == True:
                    child.sendline("tx_checksum set vxlan hw 0")
                    child.sendline("tx_checksum set vxlan hw 1")
                if checksum_flags[4] == True:
                    child.sendline("tx_checksum set vxlan hw 0")
                    child.sendline("tx_checksum set vxlan hw 1")

        child.sendline("start")
        child.sendline("yes")
        child.expect("Command not found")
        data2 = accepted_sock.recv(BUF_LEN)
        if data2:
            accepted_sock.send("Sync2")
        else:
            print "Sync : Recv Error"
        if vlanFiltering != None:
	   ''' time.sleep(5)
	    accepted_sock.send("VLAN4")
	    vlan4_data = accepted_sock.recv(BUF_LEN)
	    if vlan4_data:
	        child.sendline("show port stats all")
	        child.sendline("yes")
	        child.expect ('Command not found')
	        output = child.before
	        vlan4_packet, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
	    time.sleep(5)
	    accepted_sock.send("VLAN5")
	    vlan5_data = accepted_sock.recv(BUF_LEN)
            if vlan4_data:
                child.sendline("show port stats all")
                child.sendline("yes")
                child.expect ('Command not found')
                output = child.before
                vlan5_packet, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
	   '''
           #if we have multicast with VLAN filter 
           if multicast:
               child.sendline("set promisc all off")
               child.sendline("set allmulti all on")
           if vlanFiltering == '1':
               old_rx = 0
               old_tx = 0
               child.sendline("rx_vlan add  4 0")
               child.sendline("rx_vlan add  4 1")
               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 1:
                       print "Testpmd did not received packet for vlan 4"
                       failPrint()
                       sys.exit(1)
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx

               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               print "vlan4_data", vlan4_data
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 0:
                       if multicast :
                           pass
                       else :
                           print "Testpmd received packet for vlan 5 which is not added"
                           failPrint()
                           sys.exit(1)
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               
               child.sendline("rx_vlan rm  4 0")
               child.sendline("rx_vlan rm  4 1")
               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 1:
                       print "Testpmd did not received packet for vlan 5 after removing all vlans"
                       failPrint()
                       sys.exit(1)
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               passPrint()
               sys.exit(0)
               #scenario 2 adding two vlans 
               # check that testpmd receives packets for them both
               # remove one of them and check if it receives for the other only
               # remove the last one and check that it receives for any 
           if vlanFiltering == '2':
               old_rx = 0
               old_tx = 0
               #add vlan 4 and 5 
               child.sendline("rx_vlan add  4 0")
               child.sendline("rx_vlan add  4 1")
               child.sendline("rx_vlan add  5 0")
               child.sendline("rx_vlan add  5 1")
               #send sync Message for vlan 4 
               print "rx_vlan add  4 0\nrx_vlan add  4 1\nrx_vlan add  5 0 \nrx_vlan add  5 1 \n wating for client to send "
               print "sych VLAN4"
               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "client receved data for vlan 4, will receive data"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 2:
                       print "Testpmd did not received packet for vlan 4 and 5 after adding two vlans"
                       failPrint()
                       sys.exit(1)
                   print "Testpmd  received packet for vlan 4 and 5 after adding two vlans"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               child.sendline("rx_vlan rm  4 0")
               child.sendline("rx_vlan rm  4 1")
               print "rx_vlan rm  4 0\nrx_vlan rm  4 1"
               print "sync VLAN4"
               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "client receved data for vlan 4, will not receive data"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 0:
                       if multicast:
                           pass
                       else:
                           print "Testpmd  received packet for vlan 4 after removing it"
                           failPrint()
                           sys.exit(1)
                   print "Testpmd didn't receive packet for vlan 4 after removing it"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #send sync Message for vlan 5
               print "sync VLAN5"
               accepted_sock.send("VLAN5")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "client receved data for vlan 5, will receive data"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 1:
                       if multicast :
                           pass
                       else :

                           print "Testpmd did not received packet for vlan 5 after removing only vlan 4"
                           failPrint()
                           sys.exit(1)
                   print "Testpmd received packet for vlan 5 after removing only vlan 4"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #removing vlan 5
               child.sendline("rx_vlan rm  5 0")
               child.sendline("rx_vlan rm  5 1")
               print "rx_vlan rm  5 0 \nrx_vlan rm  5 1"
               print "sync VLAN 4"
               accepted_sock.send("VLAN4")
               print "rx_vlan rm  5 0 \nrx_vlan rm  5 1 \n wating for client to send "
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "client receved data for vlan 4, will receive data after removing vlan 5"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 2:
                       print "Testpmd did not receive packet for vlan 4 and 5 after removing all vlans"
                       failPrint()
                       sys.exit(1)
                   print "Testpmd receive packets for vlan 4 and 5 after removing all vlans"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               
               passPrint()
               sys.exit(0)
               # scenario 3 adding three vlans 
               # check that testpmd received packets for the three of them 
               # remove one of them check that it receives for the other two only
               #remove another one check that it only receive for the remaining 
               #remove the last one and it will receive for any vlan 
           if vlanFiltering == '3':
               old_rx = 0
               old_tx = 0
               #add vlan 4, 5 and 6
               child.sendline("rx_vlan add  4 0")
               child.sendline("rx_vlan add  4 1")
               child.sendline("rx_vlan add  5 0")
               child.sendline("rx_vlan add  5 1")
               child.sendline("rx_vlan add  6 0")
               child.sendline("rx_vlan add  6 1")
               print"rx_vlan add  4 0\nrx_vlan add  4 1\nrx_vlan add  5 0\nrx_vlan add  5 1\nrx_vlan add  6 0\nrx_vlan add  6 1"
               print "sync VLAN 4,5 and 6"
               #send sync Message for vlan 4,5,6
               accepted_sock.send("VLAN|")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   time.sleep(3)
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will receive data for all three vlans"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   # print "will receive data for all three vlans"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 3:
                       print "Testpmd did not received packets after adding three vlans"
                       failPrint()
                       sys.exit(1)
                   print "Testpmd received all three packets after adding the three vlans"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #removing vlan 5
               child.sendline("rx_vlan rm  5 0")
               child.sendline("rx_vlan rm  5 1")
               print "\n\nrx_vlan rm  5 0\nrx_vlan rm  5 1"
               print "sync VLAN 4 and 6"
               #send sync Message for vlan 4 and 6
               accepted_sock.send("VLAN|")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   time.sleep(3)
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will receive data for vlan 4 and 6"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   #               print "will receive data for vlan 4 and 6"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 2:
                       print "Testpmd did not received packet for vlan 4,6 after removing vlan 5 only "
                       failPrint()
                       sys.exit(1)
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               print "sync VLAN5"
               #send sync Message for vlan 5
               accepted_sock.send("VLAN5")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will not receive data for vlan 5"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   #              print "will not receive data for vlan 5"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 0:
                       if multicast :
                           pass
                       else :

                           print "Testpmd  received packet for vlan 5 after removing vlan 5 only "
                           failPrint()
                           sys.exit(1)
                   print "Testpmd didn't receive packet for vlan 5 after removing it"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #removing vlan 6
               child.sendline("rx_vlan rm  6 0")
               child.sendline("rx_vlan rm  6 1")
               print "\n\n rx_vlan rm  6 0\nrx_vlan rm  6 0"
               #send sync Message for vlan 6
               accepted_sock.send("VLAN6")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will not receive data for vlan 6"
                
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   #               print "will not receive data for vlan 6"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 0:
                       if multicast :
                           pass
                       else :

                           print "Testpmd received packet for vlan 6 after removing vlan 6 and vlan 5"
                           failPrint()
                           sys.exit(1)
                   print "Testpmd didn't receive packet for vlan 6 after removing vlan 6 and vlan 5"
               else:
                    print "Sync : Recv error"
                    failPrint()
                    sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #send sync message for vlan 4
               accepted_sock.send("VLAN4")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will receive data for vlan 4"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   #               print "will receive data for vlan 4"
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 1:
                       print "Testpmd did not receive packet for vlan 4 after removing vlan 6 and vlan 5"
                       failPrint()
                       sys.exit(1)
                   print "Testpmd  received packet for vlan 4 after removing vlan 6 and vlan 5"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               #removing vlan 4
               child.sendline("rx_vlan rm  4 0")
               child.sendline("rx_vlan rm  4 1")
               #print "\n\nrx_vlan rm  4 0\nrx_vlan rm  4 0"
               #sync message for all 
               print "sync VLAN 4,5,6"
               accepted_sock.send("VLAN|")
               vlan4_data = accepted_sock.recv(BUF_LEN)
               time.sleep(3)
               #print "vlan4data r ",vlan4_data
               if vlan4_data:
                   child.sendline("show port stats all")
                   child.sendline("yes")
                   child.expect ('Command not found')
                   output = child.before
                   print "will receive data for all three vlans"
                   cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                   print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                   cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                   cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                   if (cur_rx - old_rx) != 3:
                       print "Testpmd did not receive packets after removing all vlans"
                       failPrint()
                       sys.exit(1)
                   print "Testpmd  received all packets after removing all vlans"
               else:
                   print "Sync : Recv error"
                   failPrint()
                   sys.exit(1)
               old_rx = cur_rx
               old_tx = cur_tx
               passPrint()
               sys.exit(0)
           if vlanFiltering == '4':
               child.sendline("set promisc all off")
               addMacWithVlanFilter(True,child,None,None,None)
        if mtuSetMultipleTimes:
            #if we have multicast with mtu set multiple times it's handeld here the multicast address  
            if multicast :
                child.sendline("set promisc all off")
                child.sendline("set allmulti all on")
            old_rx = 0
            old_tx = 0
            for i in range(len(mtu_sizes)):
                child.sendline("port config mtu 0 %s" %mtu_sizes[i])
                child.sendline("port config mtu 1 %s" %mtu_sizes[i])
                data = accepted_sock.recv(BUF_LEN)
                if data:
                    accepted_sock.send("Sync3")
                else:
                    print "Sync : Recv error"
                time.sleep(20)
                child.sendline("show port stats all")
                child.sendline("yes")
                child.expect ('Command not found')
                output = child.before
                cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
		print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
                cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
                child.sendline("port config mtu 0 1500")
                child.sendline("port config mtu 1 1500")
                if setPromisc == False and invalidMac == True and add_mac ==False:
                    if (cur_rx - old_rx) == 0 and (cur_tx - old_tx) == 0:
                        pass
                    else:
                        print "Not Expected -Got Traffic-"
                        failPrint()
                        sys.exit(1)

                elif (cur_rx - old_rx) == 0 or (cur_tx - old_tx) == 0:
                    print "Error: With MTU %s testpmd didn't get packets" %mtu_sizes[i]
                    child.sendline("port config mtu 0 1500")
                    child.sendline("port config mtu 1 1500")
                    time.sleep(1)
                    failPrint()
                    sys.exit(1)

                old_rx_p0 = cur_rx_p0
                old_rx_p1 = cur_rx_p1
                old_tx_p0 = cur_tx_p0
                old_tx_p1 = cur_tx_p1
                old_rx = cur_rx
                old_tx = cur_tx
            accepted_sock.send("Sync3")
#bbb
	if multicast and vlanFiltering == None and mtuSetMultipleTimes ==False and ipv6 == False:
            old_rx = 0
            old_tx = 0
	    child.sendline("set promisc all off")
	    child.sendline("set allmulti all on")
	    data = accepted_sock.recv(BUF_LEN)
	    if data:
	        accepted_sock.send("Sync3")
	    else:
		 print "Sync : Recv error"
	    time.sleep(3)
	    child.sendline("show port stats all")
	    child.sendline("yes")
	    child.expect ('Command not found')
	    output = child.before
	    cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
	    print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
	    cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
	    cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
	    if (cur_rx - old_rx) == 0 or (cur_tx - old_tx) == 0:
	        print "Error: Multicast is On, testpmd must receive packets with multicast mac address"
	        failPrint()
		sys.exit(1)
	    old_rx_p0 = cur_rx_p0
	    old_rx_p1 = cur_rx_p1
            old_tx_p0 = cur_tx_p0
            old_tx_p1 = cur_tx_p1
            old_rx = cur_rx
            old_tx = cur_tx

	    child.sendline("set allmulti all off")
	    data = accepted_sock.recv(BUF_LEN)
	    if data:
                accepted_sock.send("Sync3")
            else:
                 print "Sync : Recv error"
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) != 0 or (cur_tx - old_tx) != 0:
                print "Error: Multicast is Off, testpmd should not receive packets with multicast mac address becasues promisc is off"
                failPrint()
                sys.exit(1)
            old_rx_p0 = cur_rx_p0
            old_rx_p1 = cur_rx_p1
            old_tx_p0 = cur_tx_p0
            old_tx_p1 = cur_tx_p1
            old_rx = cur_rx
            old_tx = cur_tx

            child.sendline("set allmulti all on")
            data = accepted_sock.recv(BUF_LEN)
            if data:
                accepted_sock.send("Sync3")
            else:
                 print "Sync : Recv error"
            time.sleep(3)
            child.sendline("show port stats all")
            child.sendline("yes")
            child.expect ('Command not found')
            output = child.before
            cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
            print "cur_rx_p0 ", cur_rx_p0, "cur_rx_p1 ", cur_rx_p1, "cur_tx_p0 ", "cur_tx_p1 ", cur_tx_p1
            cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
            cur_tx = int(cur_tx_p0) + int(cur_tx_p1)
            if (cur_rx - old_rx) == 0 or (cur_tx - old_tx) == 0:
                print "Error: Multicast is On, testpmd must receive packets with multicast mac address"
                failPrint()
                sys.exit(1)
            accepted_sock.send("Sync4") #RRR
            old_rx_p0 = cur_rx_p0
            old_rx_p1 = cur_rx_p1
            old_tx_p0 = cur_tx_p0
            old_tx_p1 = cur_tx_p1
            old_rx = cur_rx
            old_tx = cur_tx
	    if mtuSet != None or mtuSetMultipleTimes: # to make sure that the MTU is reseted
                child.sendline("port config mtu 0 1500")
                child.sendline("port config mtu 1 1500")
            passPrint()
	    sys.exit(0)   

        if addMacMultipleTimes:
            old_rx = 0
            old_tx = 0
            for i in range(len(mac_addresses)):
                child.sendline("mac_addr add 0 %s" %mac_addresses[i])
                data = accepted_sock.recv(BUF_LEN)
                if data:
                    accepted_sock.send("Sync3")
                else:
                    print "Sync : Recv error"
                time.sleep(2)

                child.sendline("show port stats all")
                child.sendline("yes")
                child.expect ('Command not found')
                output = child.before
                cur_rx_p0, cur_rx_p1, cur_tx_p0, cur_tx_p1 = check_testpmd_out(output)
                cur_rx = int(cur_rx_p0) + int(cur_rx_p1)
                cur_tx = int(cur_tx_p0) + int(cur_tx_p1)

                if setPromisc == False and invalidMac == True and add_mac ==False:
                    if (cur_rx - old_rx) == 0 and (cur_tx - old_tx) == 0:
                        pass
                    else:
                        print "Not Expected -Got Traffic-"
                        failPrint()
                        sys.exit(1)

                elif (cur_rx - old_rx) == 0 or (cur_tx - old_tx) == 0:
                    print "Error: With add mac testpmd didn't get packets"
                    time.sleep(1)
                    failPrint()
                    sys.exit(1)

                old_rx_p0 = cur_rx_p0
                old_rx_p1 = cur_rx_p1
                old_tx_p0 = cur_tx_p0
                old_tx_p1 = cur_tx_p1
                old_rx = cur_rx
                old_tx = cur_tx

        data2 = accepted_sock.recv(BUF_LEN)
        if data2:
            accepted_sock.send("Sync4")
        else:
            print "Sync : Recv Error"

        child.sendline("show port stats all")
        child.sendline("stop")
        if mtuSet != None or mtuSetMultipleTimes:
            print "reseting MTU to 1500"
            child.sendline("port config mtu 0 1500")
            child.sendline("port config mtu 1 1500")
            time.sleep(1)
        child.expect(".*Done")
        outputToPrint = child.match.group(0)
        print "Server Output is :", outputToPrint
        outputLineToPrint = outputToPrint.split("\n")
        RxPackets = False
        TxPackets = False
        passCount = 0
        rxDataCounter = 0
        txDataCounter = 0
        countFlage = True
        flagToEnter = False
        alltraffic = False
	Bad_csum = False
        Bad_ipcsum = None
        Bad_l4csum = None
        checksum_right_port = False
        for w in range (len(outputLineToPrint)):
            if "RX-packets" in outputLineToPrint[w] and alltraffic:
                all_rx_packets = outputLineToPrint[w].split('RX-total: ')[1]#[1].split('RX-dropped:')[0]
                print "RX-total: ",int(all_rx_packets)
            if "TX-packets" in outputLineToPrint[w] and alltraffic:
                all_tx_packets = outputLineToPrint[w].split('TX-total: ')[1]#[1].split('TX-dropped:')[0]
                print "TX-total: ",int(all_tx_packets)

            if "Forward statistics for port" in outputLineToPrint[w]:
                countFlage = False 
            if "######################## NIC statistics for port 1  ########################" in outputLineToPrint[w]:
            #if "######################## NIC statistics for port 0  ########################" in outputLineToPrint[w]:
                RxPackets = True
            if "RX-packets:" in outputLineToPrint[w] and RxPackets:
                RxPacketsRate = outputLineToPrint[w].split("RX-packets:")[1].split("RX-missed:")[0].strip()
#dpdk1.6                RxPacketsRate = outputLineToPrint[w].split("RX-packets:")[1].split("RX-errors:")[0].strip()
                RxPackets = False 
            elif "RX-packets:" in outputLineToPrint[w] and TxPackets == False and countFlage and flagToEnter:
                rxDataCounter += int(outputLineToPrint[w].split("RX-packets:")[1].split("TX-packets:")[0].strip())
                txDataCounter += int(outputLineToPrint[w].split("RX-packets:")[1].split("TX-packets:")[1].split("TX-dropped:")[0].strip())
            #if "######################## NIC statistics for port 1  ########################" in outputLineToPrint[w]:
            if "######################## NIC statistics for port 0  ########################" in outputLineToPrint[w]:
                TxPackets = True
            if "TX-packets:" in outputLineToPrint[w] and TxPackets:
                TxPacketsRate = outputLineToPrint[w].split("TX-packets:")[1].split("TX-errors:")[0].strip()
                TxPackets = False
            if "Forward Stats for RX Port" in  outputLineToPrint[w] and rssQueuesFlage :
                flagToEnter = True 
                passCount += 1
                zeroQueueValue = outputLineToPrint[w].split("0/Queue=")[1].split("->")[0].strip()
                oneQueueValue = outputLineToPrint[w].split("1/Queue=")[1].strip("-------")[1].strip()
            if "Accumulated forward statistics for all ports" in outputLineToPrint[w]:
                alltraffic = True
            if checksum!= None and ("Forward statistics for port %s" %port_to_receive_traffic in outputLineToPrint[w]):
                checksum_right_port = True
	    if "Bad-ipcsum:" in outputLineToPrint[w] and checksum_right_port:
		Bad_ipcsum = outputLineToPrint[w].split("Bad-ipcsum:")[1].split("Bad-l4csum:")[0].strip().strip()
		print "Bad_ipcsum" , Bad_ipcsum
            if "Bad-l4csum:" in outputLineToPrint[w] and checksum_right_port:
                Bad_l4csum = outputLineToPrint[w].split("Bad-l4csum:")[1].strip().strip()
                checksum_right_port = False

        child.sendline("quit")
        os.system("killall -s 9 get_rxtx_throughput.sh") 
        if vlan :
            remVlan(ip)
        print "testpmd Got %s Mpps" %(str(int(all_tx_packets)/10/1024/1024))

        checkOutputFile(setPromisc,invalidMac,RxPacketsRate,TxPacketsRate,add_mac,passCount,rxDataCounter,txDataCounter,rssQueuesFlage,vlanFiltering,vxlan,all_tx_packets,all_rx_packets,checksum,Bad_ipcsum,Bad_l4csum, checksum_flags,vlan4_packet,vlan5_packet)

    else:
        #os.system("ifconfig %s  mtu 1500 up" % getNameOfIp(cip_port1))
        #time.sleep(2)
        #os.system("ifconfig %s  mtu 1500 up" % getNameOfIp(cip_port2))
        #time.sleep(2)

	if add_mac == True:
	    destMac = random_mac	
        if vlanFiltering != None:
            srcMac = getHwAddr(getNameOfIp (cip_port1))
            if multicast:
                destMac="01:00:5E:00:00:02"
            generate_vlan_filter_file(vlanFiltering,srcMac, destMac, ip, cip_port1,4)
            generate_vlan_filter_file(vlanFiltering,srcMac, destMac, ip, cip_port1,5)
            generate_vlan_filter_file(vlanFiltering,srcMac, destMac, ip, cip_port1,6)
        if checksum != None:
            srcMac = getHwAddr(getNameOfIp (cip_port1))
            generate_bad_checksum_packet(checksum_flags, srcMac, destMac, ip, cip_port1, cip_port2)

        if ipv6 != None:
            if multicast:
                destMac="01:00:5E:00:00:02" # Multicast MAC address 
            srcMac = getHwAddr(getNameOfIp (cip_port1))
            generate_ipv6_packet(srcMac, destMac, ip, cip_port1, cip_port2, invalidMac)

        if vxlan != None:
            if(vxlan == 'UC' or vxlan == 'MC' or vxlan == 'RSS'):
                srcMac = getHwAddr(getNameOfIp (cip_port1))
                generate_vxlan_test_file(vxlan, srcMac, destMac, ip, cip_port1, vlan, invalidMac)
            else:
                print "Error: vxlan takes UC, MC or RSS"
                failPrint()
                sys.exit(1)

        if vlan :
            addVlan(cip_port1)
        if mtuSet != None:
            ipToAdd = cip_port1.replace("%s." %cip_port1_first_octet,"100.")
            cmd = "ifconfig " + str(getNameOfIp(cip_port1))  + " netmask 255.255.255.0 mtu " + str(mtuSet) +" up"
            cmd2 = "ifconfig " + str(getNameOfIp(ipToAdd)) + " netmask 255.255.255.0 mtu " + str(mtuSet) +" up"
            os.popen(cmd)
            os.popen(cmd2)
        
        connect_sock.send("Sync1") # send the data
        data = connect_sock.recv(BUF_LEN)

        connect_sock.send("Sync2") # send the data
        data = connect_sock.recv(BUF_LEN)
	print "Doneeeeeeeeeeeeeeeeeeee"
        if mtuSetMultipleTimes:
            if multicast:
                destMac="01:00:5E:00:00:02"
            for i in range(len(mtu_sizes)):
                connect_sock.send("Sync3") # send the data
                data = connect_sock.recv(BUF_LEN)
                cmd = "ifconfig " + getNameOfIp(cip_port1) + " mtu " + str(mtu_sizes[i]) + " up"
                os.system(cmd)
                time.sleep(6)
                cmd = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + str(mtu_sizes[i]) + " --dest_mac=" + destMac # testpmd MTU 1k
                if invalidMac == True:
                    regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')
                    datal = regex.findall(cmd)
                    cmd = cmd.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                print "cmd to run",cmd
                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_err = process.stderr.read()
                process_out = process.stdout.read()

                cmd = "ifconfig " + getNameOfIp(cip_port1) + " mtu 1500 up"
                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_err = process.stderr.read()
                process_out = process.stdout.read()
#bbb
	elif multicast and vlanFiltering == None and mtuSetMultipleTimes == False and ipv6 == False :
	    connect_sock.send("Sync3") # send the data
	    time.sleep(3)
	    data = connect_sock.recv(BUF_LEN)
            if mtuSet == None:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
            else:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + mtuSet
            cmd = clientCommandLine +   " --dest_mac=01:00:5E:00:00:02"
            print cmd
            os.popen(cmd)

	    connect_sock.send("Sync3") # send the data
	    time.sleep(3)
            data = connect_sock.recv(BUF_LEN)
            if mtuSet == None:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
            else:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + mtuSet
            cmd = clientCommandLine +   " --dest_mac=01:00:5E:00:00:02"
            print cmd
            os.popen(cmd)

            connect_sock.send("Sync3") # send the dataa
	    time.sleep(3)
            data = connect_sock.recv(BUF_LEN)
            if mtuSet == None:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
            else:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + mtuSet
            cmd = clientCommandLine +   " --dest_mac=01:00:5E:00:00:02"
            print cmd #RRR
            os.popen(cmd)

        elif addMacMultipleTimes:
            for i in range(len(mac_addresses)):
                connect_sock.send("Sync3") # send the data
                data = connect_sock.recv(BUF_LEN)
                time.sleep(1)
                cmd = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8  --dest_mac=" + mac_addresses[i] # testpmd addMacMultipleTimes
                print "cmd to run",cmd
                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_err = process.stderr.read()
                process_out = process.stdout.read()


        elif rssQueuesFlage and vxlan == None and vlanFiltering == None:
            rssQueueCommand = []
            if mtuSet == None:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
            else:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + mtuSet
            cmd1 = clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip
            cmd2 = clientCommandLine +   " --dest_mac=" + destMac 
            cmd3 =  clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip_port1 + " --source_mac " + getHwAddr(getNameOfIp(cip_port1)) 
            cmd4 = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip_port1 + " --source_mac " + getHwAddr(getNameOfIp(cip_port1))
            cmd5 =  clientCommandLine + " --dest_mac=" + destMac + " --dest_ip " + ip

            if invalidMac == True:
                regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')
                datal = regex.findall(cmd1)
                cmd1 = cmd1.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                datal = regex.findall(cmd2)
                cmd2 = cmd2.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                datal = regex.findall(cmd3)
                cmd3 = cmd3.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                datal = regex.findall(cmd4)
                cmd4 = cmd4.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                datal = regex.findall(cmd5)
                cmd5 = cmd5.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

            print "cmd1",cmd1
            print "cmd2",cmd2 
            print "cmd3",cmd3 
            print "cmd4",cmd4 
            print "cmd5",cmd5

            time.sleep(2)
            process  = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_out = process.stderr.read()
            sockperf_output = process.stdout.read()
            #print sockperf_output
            time.sleep(2)
            process  = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_out = process.stderr.read()
            sockperf_output = process.stdout.read()
            #print sockperf_output
            time.sleep(2)
            process  = subprocess.Popen(cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_out = process.stderr.read()
            sockperf_output = process.stdout.read()
            #print sockperf_output
            time.sleep(2)
            process  = subprocess.Popen(cmd4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_out = process.stderr.read()
            sockperf_output = process.stdout.read()
            #print sockperf_output
            process  = subprocess.Popen(cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_out = process.stderr.read()
            sockperf_output = process.stdout.read()
            #print sockperf_output

        elif vlan and vxlan == None:
            time.sleep(5)
            if invalidMac:
                process  = subprocess.Popen(clientCommandLine.replace("%s." %cip_port1_first_octet,"100."), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_out = process.stderr.read()
                sockperf_output = process.stdout.read()
                time.sleep(3)
            else:
                if mtuSet == None:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
                else:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + str(mtuSet)

                cmd = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip.replace("%s." %ip_first_octet,"100.") + " --source_ip " + cip_port1.replace("%s." %cip_port1_first_octet,"100.") + " --source_mac " + getHwAddr(getNameOfIp(cip_port1.replace("%s." %cip_port1_first_octet,"100.")))

                if invalidMac == True:
                    regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')

                    datal = regex.findall(cmd2)
                    cmd = cmd2.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')

                print "cmd",cmd

                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_out = process.stderr.read()
                sockperf_output = process.stdout.read()
                time.sleep(2)

        elif vxlan != None:
            time.sleep(5)
            cmd = "UTscapy -t vxlan.txt -f html -o demo_campaign.html -F" 
            process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_err = process.stderr.read()
            scapy_ouput = process.stdout.read()

            print "scapy out is:", scapy_ouput
            print "scapy error is:", process_err
            grep_cmd = "cat demo_campaign.html | grep 'PASSED='"
            grep_process  = subprocess.Popen(grep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            grep_ouput = grep_process.stdout.read()
            number_of_passed = grep_ouput.split(' ')[0].split('=')[1]
            if int(number_of_passed) >= 3:
                result = 0
            else:
                result = 1

	elif vlanFiltering != None:
            '''time.sleep(5)
	    vlan_data1 = connect_sock.recv(BUF_LEN)
	    if vlan_data1:
	        cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
		os.popen(cmd) 

	    connect_sock.send("VLAN4") # send the data
	    print "waaaaaittttting second sync"
	    vlan_data2 = connect_sock.recv(BUF_LEN)
	    print "seconnnnddd sync comeee"
	    if vlan_data2:
                cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_err = process.stderr.read()
                scapy_ouput = process.stdout.read()
                print "scapy out is:", scapy_ouput
                print "scapy error is:", process_err
                grep_cmd = "cat demo_campaign.html | grep 'PASSED='"
                grep_process  = subprocess.Popen(grep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                grep_ouput = grep_process.stdout.read()
                number_of_passed = grep_ouput.split(' ')[0].split('=')[1]
                if int(number_of_passed) < 1:
                    print "ERROR: Scapy failed to send traffic"
                    failPrint()
                connect_sock.send("VLAN5") # send the data
            '''
            
            ####### TODO: check each vlanFiltering mode 1, 2 ,3
            #scenario for first mode
            if vlanFiltering == '1':
                #waiting for the first order to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    connect_sock.send("VLAN4")
                    #waiting for the first order to send packet    
                print "waiting for next order"
                vlan_data1 = connect_sock.recv(BUF_LEN)
                print "next order arrived"
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN4")
                #waiting for the last order in the scenario
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN4")
                ########
                passPrint()
                sys.exit(0)
            elif vlanFiltering == '2':
                #scenario for second mode 
                #waiting for the first order to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN5")
                print "waiting for VLAN4 order after the server has removed vlan 4"
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN4")
                print "waiting for vlan5 order after the server has removed vlan 4"
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN5")
                print "waiting for VLAN4 order after the server has removed all vlans"
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN5")
                passPrint()
                sys.exit(0)
            elif vlanFiltering == '3':
                #scenario for thierd mode
                #waiting for vlan 4 order to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                #print "After sync 1111111111111111111111111111111111111111111111111111111111111111111111111111111111"
                '''
                from subprocess import Popen, PIPE
                lscmd = "ls /share/dpdk/dpdk_tar/"
                inputList = Popen(lscmd, shell=True, stdout=PIPE).communicate()[0]
                print inputList
                '''
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                time.sleep(1)
                connect_sock.send("VLAN|")
                #waiting for vlan 4 and 6 order after removing vlan 5 to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                time.sleep(1)
                connect_sock.send("VLAN|")    
                #waiting for VLAN 5 order after removing vlan 5 to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN5")
                #waiting for vlan 6 order after removing vlan 5 and 6 to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN6")
                #waiting for VLAN 4 order after removing vlan 5 and 6 to send packet
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                time.sleep(1)
                connect_sock.send("VLAN4")
                #waiting for vlan 4,5,6 order after removing all vlans
                vlan_data1 = connect_sock.recv(BUF_LEN)
                if vlan_data1:
                    cmd = "UTscapy -t vlanFilter4.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter5.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                    cmd = "UTscapy -t vlanFilter6.txt -f html -o demo_campaign.html -F"
                    os.popen(cmd)
                connect_sock.send("VLAN|")
                passPrint()
                sys.exit(0)
            elif vlanFiltering == '4':
                addMacWithVlanFilter(False,None,srcMac,ip,cip_port1)
	elif ipv6 == True: 
            time.sleep(5)
	    cmd = "UTscapy -t IPv6.txt -f html -o demo_campaign.html -F"
            process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_err = process.stderr.read()
            scapy_ouput = process.stdout.read()
            print "scapy out is:", scapy_ouput
            print "scapy error is:", process_err
            grep_cmd = "cat demo_campaign.html | grep 'PASSED='"
            grep_process  = subprocess.Popen(grep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            grep_ouput = grep_process.stdout.read()
            number_of_passed = grep_ouput.split(' ')[0].split('=')[1]
            if int(number_of_passed) < 1:
                print "ERROR: Scapy failed to send traffic"
                failPrint()
		sys.exit(1)
	    passPrint()
            sys.exit(0)

        elif checksum != None and vxlan == None:
            time.sleep(5)
	    if checksum_flags[3] == True or checksum_flags[4] == True:
		thread.start_new_thread(run_sniffer, (getNameOfIp(cip_port1), ))
		time.sleep(5)
	    else:
            	thread.start_new_thread(run_tcpdump, (getNameOfIp(cip_port1), ))
            	time.sleep(1)
                print "TCPDUMP RUN"
            	thread.start_new_thread(run_tcpdump, (getNameOfIp(cip_port2), ))
            	time.sleep(10)

            cmd = "UTscapy -t checksum.txt -f html -o demo_campaign.html -F"
            process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process_err = process.stderr.read()
            scapy_ouput = process.stdout.read()

            print "scapy out is:", scapy_ouput
            print "scapy error is:", process_err
            grep_cmd = "cat demo_campaign.html | grep 'PASSED='"
            grep_process  = subprocess.Popen(grep_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            grep_ouput = grep_process.stdout.read()
	    number_of_passed = grep_ouput.split(' ')[0].split('=')[1]
            if int(number_of_passed) < 1:
                print "ERROR: Scapy failed to send traffic"
                failPrint()
                sys.exit(1)
	    if not (checksum_flags[3] == True or checksum_flags[4] == True):
                cmd = "kill -2 " + str(ports_status[getNameOfIp(cip_port1)][0])
                os.system(cmd)
                cmd = "kill -2 " + str(ports_status[getNameOfIp(cip_port2)][0])
                os.system(cmd)
                time.sleep(5)
                print "Tcpdump for port %s is:"%(getNameOfIp(cip_port1))
                #print "%s" %ports_status[getNameOfIp(cip_port1)][1]
                print
                print
                print "Tcpdump for port %s is:"%(getNameOfIp(cip_port2))
                #print "%s" %ports_status[getNameOfIp(cip_port2)][1]
                for i in range (len (ports_status[getNameOfIp(cip_port1)])) :

                    print "cip1 :  ", ports_status[getNameOfIp(cip_port1)][i]
                    print "cip2 : ",ports_status[getNameOfIp(cip_port2)][i]


            if checksum_flags[0] == True:#IP
                '''
                for i in range (len (ports_status[getNameOfIp(cip_port1)])) :
                    
                    print "cip1 :  ", ports_status[getNameOfIp(cip_port1)][i] 
                    print "cip2 : ",ports_status[getNameOfIp(cip_port2)][i]
                '''
                if "bad cksum" in ports_status[getNameOfIp(cip_port1)][1] and "bad cksum" not in ports_status[getNameOfIp(cip_port2)][1]:
                    print "IP Checksum worked well. Port1: sent packet with bad IP cksum on port1 and got packet with good IP cksum on port2"
                else:
                    print "Error: IP Checksum: expected Port1: sent packet with bad IP cksum on port1 and got packet with good IP cksum on port2"
                    failPrint()
                    sys.exit(1)

            if checksum_flags[1] == True:#UDP
                if "bad udp cksum" in ports_status[getNameOfIp(cip_port1)][1] and "udp sum ok" in ports_status[getNameOfIp(cip_port2)][1]:
                    print "UDP Checksum worked well. Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
                else:
                    print "Error: UDP Checksum: expected Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
                    failPrint()
                    sys.exit(1)

            if checksum_flags[2] == True:#TCP
                if "cksum 0x0abc (incorrect" in ports_status[getNameOfIp(cip_port1)][1] and "(correct)" in ports_status[getNameOfIp(cip_port2)][1]:
                    print "TCP Checksum worked well. Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
                else:
                    print "Error: TCP Checksum: expected Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
                    failPrint()
                    sys.exit(1)
	    if checksum_flags[3] == True: #VXLAN_IP
		checksum_result = compare_sent_received_checksum(checksum_flags)
		if checksum_result == 1:
                    print "VXLAN_IP Checksum worked well. Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
		else:
                    failPrint()
                    sys.exit(1)
            if checksum_flags[4] == True: #VXLAN_tcp
                checksum_result = compare_sent_received_checksum(checksum_flags)
                if checksum_result == 1:
                    print "VXLAN_TCP Checksum worked well. Port1: sent packet with bad cksum on port1 and got packet with good cksum on port2"
                else:
                    failPrint()
                    sys.exit(1)

            passPrint()
            sys.exit(0)

        else:
            time.sleep(5)
            if invalidMac:
                process  = subprocess.Popen(clientCommandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_out = process.stderr.read()
                sockperf_output = process.stdout.read()
                time.sleep(3)
                
            else:
                if mtuSet == None:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 "
                else:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i " + generator_port + " -d " + generator_device + " -l 8 --mtu " + mtuSet
                cmd = clientCommandLine +   " --dest_mac=" + destMac
                print "cmd to print",cmd
                
                process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process_out = process.stderr.read()
                sockperf_output = process.stdout.read()
                #time.sleep(2)
        print "Error : here "
        connect_sock.send("Sync4") # send the data
        data = connect_sock.recv(BUF_LEN)
        print "data is : ",data
        os.system("killall -s 9 get_rxtx_throughput.sh")
        if vlan :
            remVlan(cip_port1)
        if mtuSet != None:
            ipToAdd = cip_port1.replace("%s." %cip_port1_first_octet,"100.")
            cmd = "ifconfig " + str(getNameOfIp(cip_port1))  + " netmask 255.255.255.0 mtu 1500 up"
            cmd2 = "ifconfig " + str(getNameOfIp(ipToAdd)) + " netmask 255.255.255.0 mtu 1500 up"
            #print cmd
            #print cmd2
            os.popen(cmd)
            os.popen(cmd2)
        if(vxlan != None):
            if result == 0:
                passPrint()
                sys.exit(0)
            else:
                failPrint()
                sys.exit(1)

        passPrint()
        sys.exit(0)

#def get ipv6_address(ifName):

def getHwAddr(ifName):
    s = socket(AF_INET, SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifName[:15]))
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

def getNameOfIp (ip):
    cmd = "netstat -ie | grep -B1 " + ip + " | head -n1 | awk '{print $1}'"
    nameOfIp =  os.popen(cmd).read().strip()
    try:
        nameOfIp = nameOfIp.split(':')[0] # RH7 returns interface name concatenated with ':'
    except Exception, e:
        nameOfIp = nameOfIp

    return nameOfIp

def getWhiteListed(device):
    cmd = "mst status | grep -A1 " + device + " | grep -v " + device + " "
    print cmd
    #dev = os.popen(cmd).read().split('=')[1].split(' ')[0] # this was changed to a constant only with this new ofed MLNX_OFED_LINUX_RoCE-3.0-1.0.1
    dev ="0000:05:00.0"
    return dev

def compare_sent_received_checksum(checksum_flags):
    cmd1 = "cat sniff_output.html | grep chksum"
    process1  = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process1_err = process1.stderr.read()
    process1_output = process1.stdout.read()
    cmd2 = "cat demo_campaign.html | grep chksum"
    process2  = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process2_err = process2.stderr.read()
    process2_output = process2.stdout.read()
    
    porcess1_output_lines = process1_output.split('\n')
    porcess2_output_lines = process2_output.split('\n')

    VXLAN = False
    IP    = False
    TCP   = False

    if checksum_flags[3] == True:
	checksum_new = porcess1_output_lines[2].split('<span class=field_name>chksum</span>= <span class=field_value>')[1].split('</span>')[0]
	checksum_old = porcess2_output_lines[2].split('<span class=field_name>chksum</span>= <span class=field_value>')[1].split('</span>')[0]

    if checksum_flags[4] == True:
        checksum_new = porcess1_output_lines[3].split('<span class=field_name>chksum</span>= <span class=field_value>')[1].split('</span>')[0]
        checksum_old = porcess2_output_lines[3].split('<span class=field_name>chksum</span>= <span class=field_value>')[1].split('</span>')[0]	    
    
    print 'checksum_new   ', checksum_new , 'checksum_old  ', checksum_old
    if checksum_new == checksum_old:
	return 1
    else:
	return 0

def checkOutputFile(setPromisc,invalidMac,RxPacketsRate,TxPacketsRate,add_mac,passCount,rxDataCounter,txDataCounter,rssQueuesFlage,vlanFiltering,vxlan,all_tx_packets,all_rx_packets,checksum,Bad_ipcsum,Bad_l4csum, checksum_flags,vlan4_packet,vlan5_packet):
    TxOutput = []
    RxOutput = []
	
    if add_mac == True:
        if all_rx_packets > 0:
            passPrint()
            sys.exit(0)
	else:
	    failPrint()
            sys.exit(1)

    if vlanFiltering != None:
       	if vlanFiltering == '1':
	    if vlan4_packet == '1' and vlan5_packet == '1':
               	passPrint()
                sys.exit(0)
	    else:
                failPrint()
                sys.exit(1)
	elif vlanFiltering == '2':
            if vlan4_packet == '1' and vlan5_packet == '2':
                passPrint()
                sys.exit(0)
            else:
                failPrint()
                sys.exit(1)
		
    if checksum != None:
	if checksum_flags[0] == True and  Bad_ipcsum != '0':
            passPrint()
            sys.exit(0)
        if (checksum_flags[1] == True or checksum_flags[2] == True) and Bad_l4csum != '0':
            passPrint()
            sys.exit(0)
        if checksum_flags[3] == True and  Bad_ipcsum != '0':
            passPrint()
            sys.exit(0)
        if checksum_flags[4] == True  and Bad_l4csum != '0':
            passPrint()
            sys.exit(0)
	else:
            failPrint()
            sys.exit(1)


    if vxlan == 'RSS':
        if passCount == 2 and int(all_rx_packets) >= 2 and int(all_tx_packets) >= 2:
            passPrint()
            sys.exit(0)
        else:
            print "VXLAN RSS Expected (Queues : 2 Received Packets : 2 Sent Packets : 2) Real (Queues : %s Received Packets : %s Sent Packets : %s)" %(passCount, all_tx_packets, all_tx_packets)
            failPrint()
            sys.exit(1)
    elif vxlan == 'UC' or vxlan == 'MC':
        if int(all_rx_packets) == 1 and int(all_tx_packets) == 1:
            passPrint()
            sys.exit(0)
        else:
            print "No VXLAN Traffic ...."
            failPrint()
            sys.exit(1)

#    if vlanFiltering == "on":
#        if int(RxPacketsRate) >= 6 and int(TxPacketsRate) >= 6:
#            passPrint()
#            sys.exit(0)
#        else:
#            print "No Traffic ...."
#            failPrint()
#            sys.exit(1)

    if rssQueuesFlage and vxlan == None:
        if setPromisc == False and invalidMac == True and add_mac ==False:
            if int(passCount) == 0 and (int(all_rx_packets) == 0 ) and (int(all_tx_packets) == 0):
                print "Expected: Not Got Data"
                passPrint()
                sys.exit(0)
            else:
                print "Not Expected -Got Traffic-"
                failPrint()
                sys.exit(1)
                
        #if (int(passCount) == 4 or int(passCount) ==2  or int(passCount) == 5) and (int(all_rx_packets) != 0 ) and (int(all_tx_packets) != 0):
        if int(passCount) > 1 and (int(all_rx_packets) != 0 ) and (int(all_tx_packets) != 0):
            passPrint()
            sys.exit(0)
        else:
            print "passCount %s all_rx_packets %s all_tx_packets %s" %(int(passCount), int(all_rx_packets), int(all_tx_packets))
            print "Number of RSS Queues is not equal expected (2, 4 or 5)"
            failPrint()
            sys.exit(1)
    if setPromisc == False and invalidMac == True and add_mac ==False:
        if int(all_rx_packets) == 0 and int(all_tx_packets) == 0:
            passPrint()
            sys.exit(0)
        else:
            print "Not Expected -Got Traffic-"
            failPrint()
            sys.exit(1)
    elif  setPromisc == False and invalidMac == True and add_mac:
        if int(all_rx_packets) == int(all_tx_packets) and int(all_rx_packets) != 0 and int(all_tx_packets) != 0 or (int(all_rx_packets) != 0 and int(all_tx_packets) != 0 and abs(int(all_rx_packets) - int(all_tx_packets)) < 700):
            passPrint()
            sys.exit(0)
        else:
            print "RxPacketsRate is %s TxPacketsRate is %s" %(all_rx_packets, all_tx_packets)
            print "difference between RxPacketsRate & TxPacketsRate should be less than 100 while it is : %s" %(int(all_rx_packets) - int(all_tx_packets))
            failPrint()
            sys.exit(1)

    if int(all_rx_packets) == int(all_tx_packets) and int(all_rx_packets) != 0 and int(all_tx_packets) != 0 or  (int(all_rx_packets) != 0 and int(all_tx_packets) != 0 and abs(int(all_rx_packets) - int(all_tx_packets)) < 700):
        passPrint()
        sys.exit(0)
    else:
        print "RxPacketsRate is %s TxPacketsRate is %s" %(all_rx_packets, all_tx_packets)
        print "difference between RxPacketsRate & TxPacketsRate should be less than 700 while it is %s" %(int(all_rx_packets) - int(all_tx_packets))
        failPrint()
        sys.exit(1)


def addVlan(ip):
    os.popen("vconfig add " + getNameOfIp(ip) + " 4")
    first_octet = ip.split('.')[0]
    ipToAdd = ip.replace("%s." %first_octet,"100.")
    cmd = "ifconfig " + str(getNameOfIp(ip)) + ".4 " + ipToAdd  + " netmask 255.255.255.0 up"
    #print cmd
    os.popen(cmd)
    time.sleep(10)

def remVlan(ip):
    os.popen("vconfig rem " + getNameOfIp(ip) + ".4")

def getEthtoolparamteres(interfaceName):
    autonegotiate = None
    rx = None
    tx = None
    ethtoolOutput = os.popen("ethtool -a " + interfaceName)
    ethtoolOutputline = ethtoolOutput.readline()
    while ethtoolOutputline :
        if "Autonegotiate" in ethtoolOutputline :
            autonegotiate = ethtoolOutputline.split(":")[1].strip()
        elif "RX" in ethtoolOutputline:
            rx = ethtoolOutputline.split(":")[1].strip()
        elif "TX" in  ethtoolOutputline:
            tx = ethtoolOutputline.split(":")[1].strip()
        ethtoolOutputline = ethtoolOutput.readline()
    return autonegotiate,rx,tx

def checkFlowControl(autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod,autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg,rxEthtoolOrg1,txEthtoolOrg1,rxEthtool,txEthtool,set_flow_control_at_once):
    if set_flow_control_at_once != None:
        if set_flow_control_at_once == txEthtoolOrg and set_flow_control_at_once == rxEthtoolOrg:
            print "RX/TX modified at once successfully ..... RX/TX expected %s/%s actual %s/%s" %(set_flow_control_at_once, set_flow_control_at_once, rxEthtoolOrg, txEthtoolOrg)
        else:
            print "Error : RX/TX were not modified at once successfully ..... RX/TX expected %s/%s actual %s/%s" %(set_flow_control_at_once, set_flow_control_at_once, rxEthtoolOrg, txEthtoolOrg)
            failPrint()
            sys.exit(1)

    if rxEthtoolOrg1 == 'on' and txEthtoolOrg1 == 'on':
        print "RX/TX did not change for port 1 ..... RX/TX expected on/on"
    else:
        print "Error : RX/TX changed for port 1 ..... RX/TX expected on/on actual %s/%s" %(rxEthtoolOrg1,txEthtoolOrg1)
        failPrint()
        sys.exit(1)

    if rxEthtool != None and txEthtool == None:
        if rxEthtoolMod == rxEthtool and txEthtoolMod == txEthtoolOrg:
            print "Rx modified successfully , we will run traffic now"
            #passPrint()
            #sys.exit(0)
        else:
            if rxEthtoolMod != rxEthtool:
                print "Rx value suppose to be " + str(rxEthtool) + " but Rx value from system is " + str (rxEthtoolMod)  
            elif txEthtoolMod != txEthtoolOrg :
                print " Tx value should not be modifed , it was " + str(txEthtoolOrg) + " and the value now is " + str(txEthtoolMod) 
            failPrint()
            sys.exit(1)
    if txEthtool != None and rxEthtool == None :
        if txEthtoolMod == txEthtool and rxEthtoolMod == rxEthtoolOrg:
            #passPrint()
            #sys.exit(0)
            print "Tx modified successfully , we will run traffic now"
        else:
            if txEthtoolMod != txEthtool:
                print "Tx value suppose to be " + str(txEthtool) + " but Rx value from system is " + str (txEthtoolMod) 
            elif rxEthtoolMod != rxEthtoolOrg :
                print " Rx value should not be modifed , it was " + str(rxEthtoolOrg) + " and the value now is " + str(rxEthtoolMod)

            failPrint()
            sys.exit(1)
    if rxEthtool != None and txEthtool != None:
        if rxEthtoolMod == rxEthtool and txEthtoolMod == txEthtool:
            print "Both Rx and Tx modified successfully , we will run traffic now"
            #passPrint()
            #sys.exit(0)
        else:
            print "Rx value suppose to be " + str(rxEthtool) + " but Rx value from system is " + str (rxEthtoolMod) + ", Tx value suppose to be " +str(txEthtool) + " but Rx value from system is " + str (txEthtoolMod)
            failPrint()
            sys.exit(1)

if __name__ == "__main__":
    """
    Function : main
    Description : The main function that will will start the run
    Return value : None
    """
    runTest()

#bashaaaaaaaaaaaaaaaarrr
