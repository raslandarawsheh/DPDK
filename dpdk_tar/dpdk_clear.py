#!/usr/bin/python
# Author Name: Hadi ALSayyed
# Run Testpmd tests

# Import all needed libraries
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
    from socket import *

except Exception, e:
    print ("-E- can not import file %s" %e)
    sys.exit(1)

os.system("export COVFILE=/tmp/clean.cov")

BUF_LEN          = 1024
INVALID_SOCKET   = 0
accepted_sock    = INVALID_SOCKET
connect_sock     = INVALID_SOCKET
ip_hw = None

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
    serverHost = ip # servername is localhost
    serverPort = port
    s = socket(AF_INET, SOCK_STREAM) # create a TCP socket
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.connect((serverHost, serverPort)) # connect to server on the port
    global connect_sock
    connect_sock = s
    #return connect_sock

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
    #return accepted_sock

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
    print Bcolors.HELP + "\tcip		\t	: IP of the client interface"
    print Bcolors.HELP + "\tport		\t	: Port number"
    print Bcolors.HELP + "\tportUpInInit	\t	: The port link is brought up during init"
    print Bcolors.HELP + "\tmtuSet		\t	: Set the mtu for the giving amount for mellanox interface"
    print Bcolors.HELP + "\tvlanFiltering	\t	: Set vlan filter on or off"
    print Bcolors.HELP + "\tmtuSetMultipleTimes \t	: Set MTU multiple times at run time"
    print Bcolors.HELP + "\tautonegotiateEthtool \t	: Set autonegotiate value through Ethtool"
    print Bcolors.HELP + "\trxEthtool 		\t      : Set RX value through Ethtool"
    print Bcolors.HELP + "\ttxEthtool           \t      : Set TX value through Ethtool"
    print Bcolors.HELP + "\tDNFS           \t      : Enable DNFS"
    print Bcolors.HELP + "\tVXLAN           \t      : Send VXLAN Traffic via Scapy"
    
def parse(tuple):
    """
    Function : parse
    Description : Parse is a method to parse the parameters, and produce the executed test command line
    Todo: Support unlimited option
    """

    global accepted_sock, connect_sock, ip_hw

    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 "
    #serverCommandLine = "/Testcode/dpdk-1.7.1/build/app/testpmd -c 0x0d000000 -n 4 -b "
    serverCommandLine = "/download/dpdk-1.7.1/x86_64-native-linuxapp-gcc/build/app/test-pmd/testpmd -c 0x0d000000 -n 4 "
    #serverCommandLine = "/Testcode/dpdk-1.6.0r2/x86_64-default-linuxapp-gcc/app/testpmd -c 0x0d000000 -n 4 -b "

    outputCommand = "/hpc/home/USERS/halsayyed/get_rxtx_throughput.sh mlx4_1 1"
    ip       	= None
    port        = 20201
    is_s        = False
    exit_status = 0
    mip = "10.224.14.113"
    cip = "11.4.3.6"
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
    dnfs = None
    vxlan = None
    try:
        opts, extraparams = getopt.getopt(tuple, "hsF:f:i:a:A:E:",['server', 'vxlan', 'ip=', 'port=', 'mip=', 'cip=', 'invalidMac', 'setPromisc', 'dest_ip=', 'add_mac', 'rxq=', 'txq=', 'disable_rss', 'rssQueuesFlage', 'vlan', 'portUpInInit', 'mtuSet=', 'vlanFiltering=', 'mtuSetMultipleTimes', 'autonegotiateEthtool=', 'rxEthtool=', 'txEthtool=', 'device=', 'dnfs'])

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

            elif o in ['--dnfs']:
                dnfs = True

            elif o in ['--vxlan']:
                vxlan = True

            elif o in ['-i', '--ip']:
                ip = p
            elif o in ['--cip']:
                cip = p
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

            else:
                print("-E- Invalid argument:" )
                usage()
                sys.exit(1)

    except Exception, e:
        print e.message
        usage()
        exit_status = 1
        sys.exit(exit_status)

    if is_s:
        ip_hw = getHwAddr(getNameOfIp(ip))
        whitelisted = getWhiteListed(device)

        serverCommandLine += " -w " + str(whitelisted) + " -d /download/mlx4_pmd_beta_v2.7.0/librte_pmd_mlx4/librte_pmd_mlx4.so -- --numa --burst=64 --txd=256 --rxd=256 --mbcache=512 --coremask=0x0c000000 --portmask 0x3 -i "

        if rxq != 1 or txq != 1:
            serverCommandLine += " --rxq=" + str(rxq) + " --txq=" + str(txq) + " --nb-cores=" + str(txq)
    if is_s:
        print "Server Side ......................................................... mip %s port %s " %(mip, port)
        tcp_server(mip, int(port + 100))
        #Send MAC address to client
        try:
            accepted_sock.send(getHwAddr(getNameOfIp(ip)))
        except Exception, e:
            print "HwAddr Send Error ...."
            sys.exit(1)
    else:
        print "Client Side ......................................................... mip %s port %s" %(mip, port)
        tcp_client(mip, int(port + 100))
        #Get MAC address from server
        destMac = connect_sock.recv(BUF_LEN)
        clientCommandLine += " --dest_mac=" + destMac

        if invalidMac == True:
            regex = re.compile('--dest_mac=[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')
            datal = regex.findall(clientCommandLine)
            clientCommandLine = clientCommandLine.replace(datal[0],'--dest_mac=00:02:C9:21:00:00')
        
    if disable_rss:
        serverCommandLine += ' --disable-rss'

    print "serverCommandLine:", serverCommandLine 

    if dest_ip == "unicast":
        clientCommandLine = clientCommandLine + " --dest_ip "+ ip
    elif dest_ip == "multicast":
        clientCommandLine = clientCommandLine + " --dest_ip 224.10.10.10"
    
    return clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,vxlan

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

def generate_vxlan_test_file(ip, cip):
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
    scapy_file.write("p =IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data)/VXLAN(vni=42)\n" %(ip, cip))
    scapy_file.write("send(p)\n")

    scapy_file.close()

def runTest():
    """
    Function : runTest
    Description : The main function that will run testpmd tests
    Return value : None
    """
    clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand ,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,vxlan = parse(sys.argv[1:])
    os.system("echo 1024 >  /proc/sys/vm/nr_hugepages")
    if mtuSet != None:
        clientCommandLine += " --mtu " + mtuSet
    if is_s == True:
        if portUpInInit:
            ipToAdd = ip.replace("11.","12.")
            cmd = "/sbin/ifconfig " + str(getNameOfIp(ip)) + " down"
            cmd2 = "/sbin/ifconfig " + str(getNameOfIp(ipToAdd)) + " down"
            os.popen(cmd)
            os.popen(cmd2)
        if vlan :
            addVlan(ip)
        if autonegotiateEthtool != None or rxEthtool!= None or txEthtool!= None :
            autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg = getEthtoolparamteres(getNameOfIp(ip)) 
            
        process2  = subprocess.Popen(outputCommand + " > server.out.tmp &", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = accepted_sock.recv(BUF_LEN)

        if data:
            accepted_sock.send("echo -> " + data)
        else:
            print "Sync : Recv error"
        child = pexpect.spawn(serverCommandLine)
        child.expect('')
        if rxEthtool == "on":
            child.sendline("set flow_ctrl rx on 0")
        elif rxEthtool == "off":
            child.sendline("set flow_ctrl rx off 0")
        if txEthtool == "on":
            child.sendline("set flow_ctrl tx on 0")
        elif txEthtool == "off":
            child.sendline("set flow_ctrl tx off 0")
        autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod = getEthtoolparamteres(getNameOfIp(ip))
        if rxEthtool != None or txEthtool != None:
            checkFlowControl(autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod,autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg,rxEthtool,txEthtool)
        if vlanFiltering != None and vlanFiltering == "on":
            child.sendline("rx_vlan add  all 0")
            child.sendline("rx_vlan add  all 1")
        elif  vlanFiltering != None and vlanFiltering == "off":
            child.sendline("vlan set filter off 0")
            child.sendline("vlan set filter off 1")
        if mtuSet != None:
            child.sendline("port config mtu 0 "+str(mtuSet))
            child.sendline("port config mtu 1 "+str(mtuSet))
        if setPromisc == False:
            child.sendline("set promisc all off")
        if dest_ip == "multicast" and add_mac == False:
            child.sendline("set allmulti all on")
        if add_mac and invalidMac :
            child.sendline("mac_addr add 0 00:02:C9:21:00:00")
        elif add_mac :
            child.sendline("mac_addr add 0 " + ip_hw)
        elif add_mac and dest_ip == "multicast":
            child.sendline("set allmulti all on")
            child.sendline("mac_addr add 0 " + ip_hw)
        child.sendline("start")
        child.expect(".*Done")

        data = accepted_sock.recv(BUF_LEN)
        if data:
            accepted_sock.send("echo -> " + data)
        else:
            print "Sync : send error"

        child.sendline("show port stats all")
        if mtuSetMultipleTimes:
            child.sendline("port config mtu 0 1200")
            child.sendline("port config mtu 1 1200")
            time.sleep(10)
            child.sendline("port config mtu 0 1400")
            child.sendline("port config mtu 1 1400")
            time.sleep(10)
            child.sendline("port config mtu 0 1100")
            child.sendline("port config mtu 1 1100")
            time.sleep(10)
            child.sendline("port config mtu 0 1300")
            child.sendline("port config mtu 1 1300")
            time.sleep(10)
            child.sendline("port config mtu 0 1000")
            child.sendline("port config mtu 1 1000")


        data2 = accepted_sock.recv(BUF_LEN)
        if data2:
            accepted_sock.send("echo -> " + data2)
        else:
            print "Sync : Recv Error"

        child.sendline("show port stats all")
        child.sendline("stop")
        if mtuSet != None:
            child.sendline("port config mtu 0 1500")
            child.sendline("port config mtu 1 1500")
            time.sleep(1)
        child.expect(".*Done")
        outputToPrint = child.match.group(0)
        print "Server Outputtttttttttttttttttttttttttttttt is :", outputToPrint
        outputLineToPrint = outputToPrint.split("\n")
        RxPackets = False
        TxPackets = False
        passCount = 0
        rxDataCounter = 0
        txDataCounter = 0
        countFlage = True
        flagToEnter = False
        alltraffic = False
        for w in range (len(outputLineToPrint)):
            if "RX-packets" in outputLineToPrint[w] and alltraffic:
                all_rx_packets = outputLineToPrint[w].split('RX-total: ')[1]#[1].split('RX-dropped:')[0]
                print "RX-total: ",int(all_rx_packets)
            if "TX-packets" in outputLineToPrint[w] and alltraffic:
                all_tx_packets = outputLineToPrint[w].split('TX-total: ')[1]#[1].split('TX-dropped:')[0]
                print "TX-total: ",int(all_tx_packets)

            if "Forward statistics for port" in outputLineToPrint[w]:
                countFlage = False 
            #if "######################## NIC statistics for port 1  ########################" in outputLineToPrint[w]:
            if "######################## NIC statistics for port 0  ########################" in outputLineToPrint[w]:
                RxPackets = True
            if "RX-packets:" in outputLineToPrint[w] and RxPackets:
                RxPacketsRate = outputLineToPrint[w].split("RX-packets:")[1].split("RX-missed:")[0].strip()
#dpdk1.6                RxPacketsRate = outputLineToPrint[w].split("RX-packets:")[1].split("RX-errors:")[0].strip()
                RxPackets = False 
            elif "RX-packets:" in outputLineToPrint[w] and TxPackets == False and countFlage and flagToEnter:
                rxDataCounter += int(outputLineToPrint[w].split("RX-packets:")[1].split("TX-packets:")[0].strip())
                txDataCounter += int(outputLineToPrint[w].split("RX-packets:")[1].split("TX-packets:")[1].split("TX-dropped:")[0].strip())
            if "######################## NIC statistics for port 1  ########################" in outputLineToPrint[w]:
            #if "######################## NIC statistics for port 2  ########################" in outputLineToPrint[w]:
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

        child.sendline("quit")
        os.system("killall -s 9 get_rxtx_throughput.sh") 
        if vlan :
            remVlan(ip)
        data2 = accepted_sock.recv(BUF_LEN)
        if data2:
            accepted_sock.send("echo -> " + data2)
        else:
            print "Sync : Recv Error"
        
        print "testpmd Got %s Mpps" %(str(int(all_tx_packets)/10/1024/1024))

        accepted_sock.send(RxPacketsRate)
        accepted_sock.send(TxPacketsRate)
        checkOutputFile(setPromisc,invalidMac,RxPacketsRate,TxPacketsRate,add_mac,passCount,rxDataCounter,txDataCounter,rssQueuesFlage,vlanFiltering)

    else:
        if(vxlan):
            generate_vxlan_test_file(ip, cip)

        if vlan :
            addVlan(cip)
        if mtuSet != None:
            ipToAdd = cip.replace("11.","12.")
            cmd = "/sbin/ifconfig " + str(getNameOfIp(cip))  + " netmask 255.255.255.0 mtu " + str(mtuSet) +" up"
            cmd2 = "/sbin/ifconfig " + str(getNameOfIp(ipToAdd)) + " netmask 255.255.255.0 mtu " + str(mtuSet) +" up"
            os.popen(cmd)
            os.popen(cmd2)
        
        connect_sock.send("SYNC 1 DONE") # send the data
        data = connect_sock.recv(BUF_LEN)


        connect_sock.send("SYNC 2 DONE") # send the data
        data = connect_sock.recv(BUF_LEN)

        process2  = subprocess.Popen(outputCommand + " > client.out.tmp &", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        rssQueueCommand = []
        if rssQueuesFlage :
            if mtuSet == None:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 "
            else:
                clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 --mtu " + mtuSet
            cmd1 = clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip
            cmd2 = clientCommandLine +   " --dest_mac=" + destMac 
            cmd3 =  clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip + " --source_mac " + getHwAddr(getNameOfIp(cip)) 
            cmd4 = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip + " --source_mac " + getHwAddr(getNameOfIp(cip))
            cmd5 =  clientCommandLine + " --dest_mac=" + destMac + " --dest_ip " + ip
            #print "cmd1",cmd1
            #print "cmd2",cmd2 
            #print "cmd3",cmd3 
            #print "cmd4",cmd4 
            for w in range (4):
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


        elif vlan :
            if invalidMac:
                for i in range (10):
                    time.sleep(3)


                    process  = subprocess.Popen(clientCommandLine.replace("11.","13."), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #print data
                    process_out = process.stderr.read()

                    sockperf_output = process.stdout.read()
                    #print sockperf_output
            else:
                if mtuSet == None:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 "
                else:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 --mtu " + str(mtuSet)
                cmd1 =  clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip.replace("11.","13.") + " --source_ip " + cip.replace("11.","13.") + " --source_mac " + getHwAddr(getNameOfIp(cip.replace("11.","13.")))
                cmd2 = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip.replace("11.","13.") + " --source_ip " + cip.replace("11.","13.") + " --source_mac " + getHwAddr(getNameOfIp(cip.replace("11.","13.")))
                cmd3 = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip.replace("11.","13.") + " --source_ip " + cip.replace("11.","13.")
                cmd4 = clientCommandLine +   " --dest_mac=" + destMac + " --dest_ip " + ip.replace("11.","13.") + " --source_ip " + cip.replace("11.","13.")
                cmd5 =  clientCommandLine + " --dest_mac=" + destMac + " --dest_ip " + ip.replace("11.","13.")
                #print "cmd1",cmd1
                #print "cmd2",cmd2
                #print "cmd3",cmd3
                #print "cmd4",cmd4
                #print "cmd5",cmd5
                if vlanFiltering == None :
                    sockperfCmd =  "sockperf tp --ip " + ip.replace("11.","13.")
                    time.sleep(2)
                    process  = subprocess.Popen(sockperfCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print sockperf_output

                for w in range (4):

                    time.sleep(2)
                    
                    process  = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print "out11111111111111111111", sockperf_output
                    time.sleep(2)
                    process  = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print "out22222222222222222222", sockperf_output
                    time.sleep(2)
                    process  = subprocess.Popen(cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print "out333333333333333333333", sockperf_output
                    time.sleep(2)
                    process  = subprocess.Popen(cmd4, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print "out444444444444444444444", sockperf_output
                    time.sleep(2)
                    process  = subprocess.Popen(cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    
        elif vxlan:
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
            if int(number_of_passed) == 3:
                result = 0
            else:
                result = 1
                    
        else:
            if invalidMac:
                for i in range (10):
                    time.sleep(3)

                    process  = subprocess.Popen(clientCommandLine, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #print data
                    process_out = process.stderr.read()
                
                    sockperf_output = process.stdout.read()
                    #print sockperf_output
            else:
                if mtuSet == None:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 "
                else:
                    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 --mtu " + mtuSet
                cmd1 = clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip
                cmd2 = clientCommandLine +   " --dest_mac=" + destMac
                cmd3 =  clientCommandLine +   " --port 9999 --source_port 20911 --dest_port 20910 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip + " --source_mac " + getHwAddr(getNameOfIp(cip))
                cmd4 = clientCommandLine +   " --port 9999 --dest_mac=" + destMac + " --dest_ip " + ip + " --source_ip " + cip + " --source_mac " + getHwAddr(getNameOfIp(cip))
                cmd5 =  clientCommandLine + " --dest_mac=" + destMac + " --dest_ip " + ip
                print "cmd1",cmd1
                print "cmd2",cmd2
                print "cmd3",cmd3
                print "cmd4",cmd4

                for w in range (4):
                    #print "cmd1111111 is",cmd1
                    time.sleep(2)
                    process  = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print "out11111111111111111111111111111", sockperf_output
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
                    time.sleep(2)
                    process  = subprocess.Popen(cmd5, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process_out = process.stderr.read()
                    sockperf_output = process.stdout.read()
                    #print sockperf_output


        os.system("killall -s 9 get_rxtx_throughput.sh")
        #print "AFTER KILL"
        connect_sock.send("SYNC 1 DONE") # send the data
        #print "AFTER SEND"
        data = connect_sock.recv(BUF_LEN)
        #print "AFTER CONNECT"
        if vlan :
            remVlan(cip)
        if mtuSet != None:
            ipToAdd = cip.replace("11.","12.")
            cmd = "/sbin/ifconfig " + str(getNameOfIp(cip))  + " netmask 255.255.255.0 mtu 1500 up"
            cmd2 = "/sbin/ifconfig " + str(getNameOfIp(ipToAdd)) + " netmask 255.255.255.0 mtu 1500 up"
            #print cmd
            #print cmd2
            os.popen(cmd)
            os.popen(cmd2)
        if(vxlan):
            if result == 0:
                passPrint()
                sys.exit(0)
            else:
                failPrint()
                sys.exit(1)


        
        connect_sock.send("SYNC 3 DONE") # send the data
        data = connect_sock.recv(BUF_LEN)
        Rx = connect_sock.recv(BUF_LEN)
        #Tx = connect_sock.recv(BUF_LEN)
        print "Data is", data
        
        passPrint()
        sys.exit(0)


def getHwAddr(ifName):
    cmd = "ethtool -P " + ifName
    print "cmd is:",cmd
    hwAddr =  os.popen(cmd).read().split('Permanent address:')[1].strip()
    return hwAddr

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
    dev = os.popen(cmd).read().split('=')[1].split(' ')[0]
    return dev

def checkOutputFile(setPromisc,invalidMac,RxPacketsRate,TxPacketsRate,add_mac,passCount,rxDataCounter,txDataCounter,rssQueuesFlage,vlanFiltering):
    TxOutput = []
    RxOutput = []
    #print "RxPacketsRate=",RxPacketsRate," and TxPacketsRate=",TxPacketsRate 
    if vlanFiltering == "on":
        if int(RxPacketsRate) >= 6 and int(TxPacketsRate) >= 6:
            passPrint()
            sys.exit(0)
        else:
            print "No Traffic ...."
            failPrint()
            sys.exit(1)

    if rssQueuesFlage:
        if (int(passCount) == 4 or int(passCount) ==2  or int(passCount) == 5) and ((int(rxDataCounter) - int(txDataCounter)) < 600) and ((int(RxPacketsRate) - int(rxDataCounter)) < 600):
            passPrint()
            sys.exit(0)
        else:
            print "Number of RSS Queues is not equal expected (2, 4 or 5)"
            failPrint()
            sys.exit(1)
    if setPromisc == False and invalidMac == True and add_mac ==False:
        if int(RxPacketsRate) == 0 and int(TxPacketsRate) == 0:
            passPrint()
            sys.exit(0)
        else:
            print "Not Expected -Got Traffic-"
            failPrint()
            sys.exit(1)
    elif  setPromisc == False and invalidMac == True and add_mac:
        if int(RxPacketsRate) == int(TxPacketsRate) and int(RxPacketsRate) != 0 and int(TxPacketsRate) != 0 or (int(RxPacketsRate) != 0 and int(TxPacketsRate) != 0 and abs(int(RxPacketsRate) - int(TxPacketsRate)) < 700):
            passPrint()
            sys.exit(0)
        else:
            print "RxPacketsRate is %s TxPacketsRate is %s" %(RxPacketsRate, TxPacketsRate)
            print "difference between RxPacketsRate & TxPacketsRate should be less than 100 while it is : %s" %(int(RxPacketsRate) - int(TxPacketsRate))
            failPrint()
            sys.exit(1)

    if int(RxPacketsRate) == int(TxPacketsRate) and int(RxPacketsRate) != 0 and int(TxPacketsRate) != 0 or  (int(RxPacketsRate) != 0 and int(TxPacketsRate) != 0 and abs(int(RxPacketsRate) - int(TxPacketsRate)) < 700):
        passPrint()
        sys.exit(0)
    else:
        print "RxPacketsRate is %s TxPacketsRate is %s" %(RxPacketsRate, TxPacketsRate)
        print "difference between RxPacketsRate & TxPacketsRate should be less than 700 while it is %s" %(int(RxPacketsRate) - int(TxPacketsRate))
        failPrint()
        sys.exit(1)


def addVlan(ip):
    os.popen("/sbin/vconfig add " + getNameOfIp(ip) + " 4")
    ipToAdd = ip.replace("11.","13.")
    cmd = "/sbin/ifconfig " + str(getNameOfIp(ip)) + ".4 " + ipToAdd  + " netmask 255.255.255.0 up"
    #print cmd
    os.popen(cmd)

def remVlan(ip):
    os.popen("/sbin/vconfig rem " + getNameOfIp(ip) + ".4")

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

def checkFlowControl(autonegotiateEthtoolMod,rxEthtoolMod,txEthtoolMod,autonegotiateEthtoolOrg,rxEthtoolOrg,txEthtoolOrg,rxEthtool,txEthtool):
    if rxEthtool != None and txEthtool == None :
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
