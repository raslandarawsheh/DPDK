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
    from datetime import datetime

except Exception, e:
    print ("-E- can not import file %s" %e)
    sys.exit(1)

os.system("export COVFILE=/tmp/clean.cov")

BUF_LEN          = 1024
INVALID_SOCKET   = 0
accepted_sock    = INVALID_SOCKET
connect_sock     = INVALID_SOCKET
ip_hw = None
dpdk_ver = '1.8.0'
checksum_flags = [False, False, False] #checksum_flags = [IP, UDP, TCP]
master_rc = False
msg_sizes = [64, 128, 256, 512, 1024]
testpmd = '/download/dpdk-1.8.0/x86_64-native-linuxapp-gcc/build/app/test-pmd/testpmd'
#testpmd = '/download/dpdk2.0-mlx4_pmd_2.8.4' /download/dpdk2.1-mlx5_pmd_0.5.1/
testpmd_master_rc = '/download/dpdk2.1-mlx5_pmd_0.5.1/x86_64-native-linuxapp-gcc/build/app/test-pmd/testpmd'
pmd = '/download/mlx4_pmd_accl_c67ed19c/librte_pmd_mlx4.so'
mtuset_pmd = '/download/mlx4_pmd_accl_c67ed19c.mtuset/librte_pmd_mlx4.so'
checksum_pmd = '/download/mlx4_pmd_accl_c67ed19c.checksum/librte_pmd_mlx4.so'
receive_in_line_pmd = '/download/mlx4_pmd_accl_c67ed19c.recvinline/librte_pmd_mlx4.so'
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
def get_BusInfo(ip):
    intf = getNameOfIp(ip)
    try:
        
        cmd = "ethtool -i " + intf + " | grep bus-info "
        fd= os.popen(cmd)
        output = fd.read()
        return output.split(' ')[1]
    except Exception, e:
        vl.EXCEPTION("run_command Failed (%s), cmd %s" % (str(e), str(cmd)))
        return (1, None)
        
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
    print Bcolors.HELP + "\tchecksum    \t Takes list of protocols (IP,UDP,TCP) to set bad checksum, like 'IP' or 'IP,UDP' or 'IP,TCP' or 'UDP' or 'TCP'"
    print Bcolors.HELP + "\tfirst_case           \t      : First case"
    print Bcolors.HELP + "\tlast_case           \t      : Last case"
    print Bcolors.HELP + "\tmaster_rc           \t          Use the master DPDK RC located at '/download/dpdk_master/'"
    
def parse(tuple):
    """
    Function : parse
    Description : Parse is a method to parse the parameters, and produce the executed test command line
    Todo: Support unlimited option
    """

    global accepted_sock, connect_sock, ip_hw, master_rc

    clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_0 -l 8 "
    #serverCommandLine = "/Testcode/dpdk-1.7.1/build/app/testpmd -c 0x0d000000 -n 4 -b "
    #serverCommandLine = testpmd + " -c 0xf00000000 -n 4 "
    #serverCommandLine = "/Testcode/dpdk-1.6.0r2/x86_64-default-linuxapp-gcc/app/testpmd -c 0x0d000000 -n 4 -b "

    outputCommand = "/hpc/home/USERS/halsayyed/get_rxtx_throughput.sh mlx5_0 1"
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
    Bidirectional = False
    RSS = False
    msgSize = None
    recv_inline = False
    checksum = None
    fwd_mode = None
    first_case = False
    last_case = None
    try:
        opts, extraparams = getopt.getopt(tuple, "hsF:f:i:a:A:E:",['server', 'ip=', 'port=', 'mip=', 'cip=', 'invalidMac', 'setPromisc', 'dest_ip=', 'add_mac', 'rxq=', 'txq=', 'disable_rss', 'rssQueuesFlage', 'vlan', 'portUpInInit', 'mtuSet=', 'vlanFiltering=', 'mtuSetMultipleTimes', 'autonegotiateEthtool=', 'rxEthtool=', 'txEthtool=', 'device=', 'dnfs', 'Bidirectional', 'RSS','recv-inline','msg-size=','checksum=','fwd-mode=', 'first_case', 'last_case=', 'master_rc'])

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
                
            elif o in ['--first_case']:
                first_case = True

            elif o in ['--master_rc']:
                master_rc = True

            elif o in ['--last_case']:
                last_case = p

            elif o in ['--RSS']:
                RSS = True

            elif o in ['--checksum']:
                checksum = p

            elif o in ['--Bidirectional']:
                Bidirectional = True

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
            elif o in ['--msg-size']:
                msgSize = p
            elif o in ['--recv-inline']:
                recv_inline = True
            elif o in ['--fwd-mode']:
                fwd_mode = p

            else:
                print("-E- Invalid argument:" )
                usage()
                sys.exit(1)

    except Exception, e:
        print e.message
        usage()
        exit_status = 1
        sys.exit(exit_status)

    if first_case:
        date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        directory = '/tmp/' + date
        os.mkdir(directory)
        cmd = "mv /download/performance_result/*.csv %s" %directory
        print cmd
        os.system(cmd)
    
    #testpmd = '/download/dpdk2.0-mlx4_pmd_2.8.4'
    master_rc = True 
    if master_rc:
        serverCommandLine = testpmd_master_rc 
    else:
        serverCommandLine = testpmd
    '''
    
    if checksum != None or fwd_mode != None:
        testpmd+=".checksum"
    elif recv_inline == True:
        testpmd+=".recvinline"
    else:
        pass
    testpmd+='/dpdk2.0-mlx4/x86_64-native-linuxapp-gcc/app/testpmd'

    serverCommandLine = testpmd
    '''
    if RSS:
	serverCommandLine +=  " -c 0xfffff -n 4  "
    else:
	serverCommandLine += " -c 0xfffff -n 4  "#NUMA 0 
#        serverCommandLine += " -c 0x00fff000ff -n 4  "#NUMA 1
        #serverCommandLine += " -c 0xfffffff -n 4  "
    
    if recv_inline == True and is_s == True:
        print "msg-sizeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",msgSize
        os.environ["MLX4_INLINE_RECV_SIZE"] = str(msgSize)

    if is_s:
        ip_hw = getHwAddr(getNameOfIp(ip))
        whitelisted = getWhiteListed(device)

	serverCommandLine +=  " -w  0000:04:00.0 -w  0000:04:00.1 " #+ str(whitelisted) 
        serverCommandLine += " -- --port-numa-config=0,0,1,0 --socket-num=0 --numa --burst=70 --txd=256 --rxd=256 --mbcache=128  --portmask 0x3  "
#	serverCommandLine += " -- --port-numa-config=0,1,1,1 --socket-num=1 --numa --burst=70 --txd=256 --rxd=256 --mbcache=128  --portmask 0x3  "
#        serverCommandLine += " -- --port-numa-config=0,0,1,0 --socket-num=0  --burst=70 --txd=256 --rxd=256 --mbcache=128  --portmask 0x3  "
	
    if is_s:
        print "Server Side ......................................................... mip %s port %s " %(mip, port)
        tcp_server(mip, int(port + 100))
        #Send MAC address to client
        try:
            accepted_sock.send(getHwAddr(getNameOfIp(ip)))
        except Exception, e:
            print "HwAddr Send Error ...."
            sys.exit(1)
	
	#Tunning Machine
        os.system("mst start")
        # busInfo = get_BusInfo(ip)
        #if busInfo == None :
        #    print "Error in getting Bus info "
        #    sys.exit(1)
        #cmd = "setpci -s " + busInfo 
        #cmd += " 68.w=5020"
        cmd= "setpci -s  0000:04:00.0 68.w=5020"
        print cmd
        os.system(cmd)
        os.system("ethtool -A %s autoneg off rx off" %getNameOfIp(ip))
        first_octet = ip.split(".")[0]
        if first_octet == '22':
            other_port_ip = ip.replace(first_octet , "21")
        elif first_octet == '21':
            other_port_ip = ip.replace(first_octet , "22")
        os.system("ethtool -A %s autoneg off rx off" %getNameOfIp(other_port_ip))
        os.system("for gov in /sys/devices/system/cpu/*/cpufreq/scaling_governor ; do echo performance >$gov ; done")
#        os.system("/download//configure_mlx4_pmd.sh -s nosriov -o")
#        os.system("/etc/init.d/openibd restart")

#        if master_rc and RSS:
#            serverCommandLine = testpmd_master_rc + " -c 0xe00000000 -n 4  -w 0000:21:00.0 -- --port-numa-config=0,1,1,1 --socket-num=1 --numa --burst=70 --txd=256 --rxd=256 --mbcache=512 --coremask=0xc00000000 --portmask 0x3 -i  --rxq=2 --txq=2 "
#        elif RSS:
#            if checksum != None:
#                serverCommandLine = testpmd + " -c 0xe00000000 -n 4  -w 0000:21:00.0 -d " + checksum_pmd + " -- --port-numa-config=0,1,1,1 --socket-num=1 --numa --burst=70 --txd=256 --rxd=256 --mbcache=512 --coremask=0xc00000000 --portmask 0x3 -i  --rxq=2 --txq=2"
#            else:
#                serverCommandLine = testpmd + " -c 0xe00000000 -n 4  -w 0000:21:00.0 -d " + pmd + " -- --port-numa-config=0,1,1,1 --socket-num=1 --numa --burst=70 --txd=256 --rxd=256 --mbcache=512 --coremask=0xc00000000 --portmask 0x3 -i  --rxq=2 --txq=2"
        '''
        if checksum != None:
            serverCommandLine += " --enable-rx-cksum"
        '''
	if RSS:
 	    serverCommandLine += "  -i --rxq=2 --txq=2 " 
	else:
	    #serverCommandLine += " --coremask=0x0000088000 -i --rxq=1 --txq=1 " #NUMA 1
            serverCommandLine += "  -i --rxq=1 --txq=1 "  #NUMA 0 
    else:
        print "Client Side ......................................................... mip %s port %s" %(mip, port)
        tcp_client(mip, int(port + 100))
        #Get MAC address from server
        destMac = connect_sock.recv(BUF_LEN)
        clientCommandLine += " --dest_mac=" + destMac

    print "serverCommandLine:", serverCommandLine 

    return clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,Bidirectional,RSS,msgSize,recv_inline,checksum,fwd_mode,first_case,last_case

def generate_bad_checksum_packet(checksum_flags, srcMac, destMac, ip, cip_port1):
    scapy_file = open('checksum.txt','w')
    scapy_file.write("% Checksum Tests\n")
    scapy_file.write("+ Informations\n")
    scapy_file.write("\n= Send Packet via Scapy\n")
    scapy_file.write("data= 'Data to be sent via Scapy'\n")

    if checksum_flags[1] == True:
        scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/UDP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[2] == True:
        scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/TCP(sport=1337,dport=4789)/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))
    elif checksum_flags[0] == True:
        scapy_file.write("p =Ether(src='%s', dst='%s')/IP(dst='%s', src='%s')/Raw(load=data) \n" %(srcMac, destMac, ip, cip_port1))

    if(checksum_flags[0] == True):
        scapy_file.write("p.chksum = 0xabc \n")
        #scapy_file.write("p.chksum = 0x0 \n")
    if checksum_flags[1] == True:
        scapy_file.write("p[UDP].chksum = 0xabc \n")
        #scapy_file.write("p[UDP].chksum = 0x0 \n")
    if checksum_flags[2] == True:
        scapy_file.write("p[TCP].chksum = 0xabc \n")
        #scapy_file.write("p[TCP].chksum = 0x0 \n")
    print "port11111111111111111111111111111111111111111",getNameOfIp(cip_port1)
    scapy_file.write("sendp(p, iface='%s')\n" %(getNameOfIp(cip_port1)))
    scapy_file.close()


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

def prepare_expected_TP():
    #DIC = {dpdk_version:{msg_size:[[RSS-Uni, RSS-Bi, RSS-Bi-recv-inline],[Not-RSS-Uni, Not-RSS-Bi, Not-RSS-Bi-recv-inline]]}}
    expected_results = {'1.7.1':{
        64:[[17.94,18.3,17.8],[18.75,21.84,22.15]],
        128:[[15.13,15.648,15.97],[18.09,17.14,12.25]],
        256:[[10.34,12.96,10.04],[11.51,11.76,9.98]],
        512:[[8.91,7.84,8.0],[7.77,7.84,8.0]],
        1024:[[4.56,4.33,1.53],[4.56,4.36,1.57]]
        },
                        '1.8.0':{
                            64:[[16.91,18.37,17.84],[17.75,21.82,22.14]],
                            128:[[12.12,15.41,16.09],[17.32,17.14,12.25]],
                            256:[[10.34,12.96,10.04],[11.57,11.76,9.99]],
                            512:[[8.91,7.86,8.0],[7.8,7.84,8.01]],
                            1024:[[4.56,4.35,1.53],[4.56,4.34,1.59]]
                        }
    }

    return expected_results

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

def check_performance_result(result, expected_dic, msg_size, dpdk_ver, last_case, bi=False, rss=False, recv_inline=False, first_case = False):#result, bidirectional, RSS Queue
    out_list_index = None
    in_list_index = None
    #DIC = {dpdk_version:{msg_size:[[RSS-Uni, RSS-Bi, RSS-Bi-recv-inline],[Not-RSS-Uni, Not-RSS-Bi, Not-RSS-Bi-recv-inline]]}}
        
    if rss:
        out_list_index = 0 
    else:
        out_list_index = 1
    if bi:
        in_list_index = 1
    else:
        in_list_index = 0
    if recv_inline:
        in_list_index = 2
    
    expected_res = expected_dic[dpdk_ver][msg_size][out_list_index][in_list_index]
#   if first_case:
#       date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
#       directory = '/tmp/' + date
#       os.mkdir(directory)
#	cmd = "mv /download/performance_result/*.csv %s" %directory
#	print cmd
#	os.system(cmd)
    
    results_file = open('/download/performance_result/%s.csv' %( msg_size),'a')
    results_file.write('%s, %s\n' %(expected_res, float(result)))

    percentage = ((float(result) - float(expected_res))/float(result))*100
    if (percentage < -1):
        print "Test Fail: Expected result is %s real result is %s percentage is %s" %(float(expected_res), float(result), float(percentage))
        failPrint()
        sys.exit(1)
    elif (percentage > 0):
        print "Result improved : Expected result is %s real result is %s percentage is %s" %(float(expected_res), float(result), float(percentage))
        passPrint()
        sys.exit(0)
    else:
        print "Result acceptable : Expected result is %s real result is %s percentage is %s" %(float(expected_res), float(result), float(percentage))
        passPrint()
        sys.exit(0)

def runTest():
    #try:
    if True:
        """
        Function : runTest
        Description : The main function that will run testpmd tests
        Return value : None
        """
        clientCommandLine,serverCommandLine,is_s, ip, port, outputCommand ,mip,setPromisc,invalidMac,dest_ip,add_mac,rssQueuesFlage,destMac,cip,vlan,portUpInInit,mtuSet,vlanFiltering,mtuSetMultipleTimes,autonegotiateEthtool,rxEthtool,txEthtool,Bidirectional,RSS,msgSize,recv_inline,checksum,fwd_mode,first_case, last_case = parse(sys.argv[1:])
        os.system("echo 1024 >  /proc/sys/vm/nr_hugepages")
        if mtuSet != None:
            clientCommandLine += " --mtu " + mtuSet
        '''
        if checksum != None:
            checksum_list = checksum.split(',')
            for w in range (len(checksum_list)):
                if "IP" in checksum_list[w]:
                    checksum_flags[0] = True
                elif "UDP" in checksum_list[w]:
                    checksum_flags[1] = True
                elif "TCP" in checksum_list[w]:
                    checksum_flags[2] = True
                else:
                    print "Error: checksum takes IP, TCP, UDP"
                    failPrint()
                    sys.exit(1)
        '''            
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
    
            for w in range (len(portNames)):                                                        #check which port name has the mac address of port 0
                if MacAddressPortZero.strip().lower() == getHwAddr(portNames[w]).strip().lower():
                    portZeroName = portNames[w]
    
            for w in range (len(portNames)):                                                        #check which port name has the mac address of port 1
                if MacAddressPortOne.strip().lower() == getHwAddr(portNames[w]).strip().lower():
                    portOneName = portNames[w]
            '''
            if checksum != None:
                port_to_receive_traffic = "0" if portZeroName == getNameOfIp(ip) else "1"
            '''    
                
            #child = pexpect.spawn(serverCommandLine)
            #child.expect('')
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
            '''
            if mtuSet != None:
                child.sendline("port config mtu 0 "+str(mtuSet))
                child.sendline("port config mtu 1 "+str(mtuSet))
            '''
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
            if fwd_mode != None:
    	        child.sendline("set fwd csum")
    	        if fwd_mode == 'hw':
    	            if checksum_flags[0] == True:
    		        child.sendline("tx_checksum set ip hw 0")
    		        child.sendline("tx_checksum set ip hw 1")
                    if checksum_flags[1] == True:
                        child.sendline("tx_checksum set udp hw 0")
                        child.sendline("tx_checksum set udp hw 1")
                    if checksum_flags[2] == True:
                        child.sendline("tx_checksum set tcp hw 0")
                        child.sendline("tx_checksum set tcp hw 1")
            '''
            if checksum != None:
                child.sendline("set fwd csum")
                if checksum_flags[0] == True:
                    child.sendline("tx_checksum set ip hw 0")
                    child.sendline("tx_checksum set ip hw 1")
                if checksum_flags[1] == True:
                    child.sendline("tx_checksum set udp hw 0")
                    child.sendline("tx_checksum set udp hw 1")
                if checksum_flags[2] == True:
                    child.sendline("tx_checksum set tcp hw 0")
                    child.sendline("tx_checksum set tcp hw 1")
            '''        
            child.sendline("start")
            #child.expect(".*Done")
    
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
            '''
            if mtuSet != None:
                child.sendline("port config mtu 0 1500")
                child.sendline("port config mtu 1 1500")
                time.sleep(1)
            '''
            child.expect(".*Done")
            outputToPrint = child.match.group(0)
            print "Server Output is :", outputToPrint
            outputLineToPrint = outputToPrint.split("\n")
            #print "outputLineToPrint",outputLineToPrint
            RxPackets = False
            TxPackets = False
            passCount = 0
            rxDataCounter = 0
            txDataCounter = 0
            countFlage = True
            flagToEnter = False
            alltraffic = False
            queues = {} # queue number is the key, value is list of [rx packets, tx packets]
            #checksum_right_port = False
            for w in range (len(outputLineToPrint)):
                print "line is:",outputLineToPrint[w]
                if "RX-packets:" in outputLineToPrint[w] and flagToEnter:
                    rx_packets = outputLineToPrint[w].split("RX-packets:")[1].split("TX-packets:")[0]
                    tx_packets = outputLineToPrint[w].split("TX-packets:")[1].split("TX-dropped:")[0]
                    queues[passCount]= [int(rx_packets), int(tx_packets)]
                    flagToEnter = False
                if "RX-packets" in outputLineToPrint[w] and alltraffic:
                    all_rx_packets = outputLineToPrint[w].split('RX-packets: ')[1].split("RX-dropped: ")[0]#[1].split('RX-dropped:')[0]
                    print "RX-total: ",int(all_rx_packets)
                if "TX-packets" in outputLineToPrint[w] and alltraffic:
                    all_tx_packets = outputLineToPrint[w].split('TX-packets: ')[1].split("TX-dropped: ")[0]#[1].split('TX-dropped:')[0]
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
                if "Forward Stats for RX Port" in  outputLineToPrint[w] :
                    flagToEnter = True 
                    passCount += 1
                    zeroQueueValue = outputLineToPrint[w].split("0/Queue=")[1].split("->")[0].strip()
                    oneQueueValue = outputLineToPrint[w].split("1/Queue=")[1].strip("-------")[1].strip()
                if "Accumulated forward statistics for all ports" in outputLineToPrint[w]:
                    alltraffic = True
                '''
                if checksum!= None and ("Forward statistics for port %s" %port_to_receive_traffic in outputLineToPrint[w]):
                    checksum_right_port = True
                if "Bad-ipcsum:" in outputLineToPrint[w] and checksum_right_port:
                    Bad_ipcsum = outputLineToPrint[w].split("Bad-ipcsum:")[1].split("Bad-l4csum:")[0].strip().strip()
                if "Bad-l4csum:" in outputLineToPrint[w] and checksum_right_port:
                    Bad_l4csum = outputLineToPrint[w].split("Bad-l4csum:")[1].strip().strip()
                    checksum_right_port = False
                '''    
            child.sendline("quit")
            os.system("killall -s 9 get_rxtx_throughput.sh") 
            '''
            if checksum != None:
                if checksum_flags[0] == True and  Bad_ipcsum != '0':
                    passPrint()
                    sys.exit(0)
                if (checksum_flags[1] == True or checksum_flags[2] == True) and Bad_l4csum != '0':
                        passPrint()
                        sys.exit(0)
                else:
                    failPrint()
                    sys.exit(1)
             '''       
            if vlan :
                remVlan(ip)
            data2 = accepted_sock.recv(BUF_LEN)
            if data2:
                accepted_sock.send("echo -> " + data2)
            else:
                print "Sync : Recv Error"
    
            #accepted_sock.send(RxPacketsRate)
            #accepted_sock.send(TxPacketsRate)
    
            if(RSS and (not Bidirectional)):
                TP = int(all_tx_packets)/20.0/1024.0/1024.0
            else:
                TP = int(all_tx_packets)/10.0/1024.0/1024.0
    
            expected_dic = prepare_expected_TP() 
    
            print "testpmd Got %s Mpps" %(str(TP))
            check_performance_result(float(TP), expected_dic, int(msgSize), dpdk_ver, last_case, Bidirectional, RSS, recv_inline, first_case)
        else:
            '''
            if checksum != None:
                srcMac = getHwAddr(getNameOfIp (cip_port1))
                generate_bad_checksum_packet(checksum_flags, srcMac, destMac, ip, cip_port1)
            '''
            
            connect_sock.send("SYNC 1 DONE") # send the data
            data = connect_sock.recv(BUF_LEN)
    
    
            connect_sock.send("SYNC 2 DONE") # send the data
            data = connect_sock.recv(BUF_LEN)
    
            process2  = subprocess.Popen(outputCommand + " > client.out.tmp &", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
            rssQueueCommand = []
            if rssQueuesFlage :
                pass
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
                    if msgSize == None:
                        clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_0 -l 8 "
                    else:
                        clientCommandLine = "raw_ethernet_bw --client --CPU-freq -d mlx5_0 -l 8 -D 10 --mtu " + msgSize
                    if RSS:
                        #cmd0 = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --dest_mac=7E:AA:42:56:92:9B -D 10 --mtu " + mtuSet #any MAC address works
                        #cmd1 = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B -D 10 --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 --mtu " + mtuSet
                        cmd0 = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_0 -l 8  --dest_mac=7E:AA:42:56:92:9B -D 10 --mtu " + msgSize
                        cmd1 = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
                        
                    else:
                        cmd0 = clientCommandLine + " -i 1 --dest_mac=f4:52:14:2c:5d:22 "
                        cmd1 = clientCommandLine + " -i 1 --dest_mac=f4:52:14:2c:5d:21 "
    		
            	    if fwd_mode != None:
    		        if checksum_flags[0] == True:
    			    cmd_checksum = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_0 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
    		        if checksum_flags[1] == True or checksum_flags[2] == True:
                            cmd_checksum = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx5_0 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_port 20911 --dest_port 20910  --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
    		    
                    for w in range (1):
                        time.sleep(10)
                        if RSS or Bidirectional:
                            print "RSS or Bidirectionalllllllllllllllllllllllllllllllllllll"
                            if Bidirectional:
                                print "Bidirectionalsssssssssssssssssssssssssssssssssssssssssssssssssss"
                                cmd0 = cmd0 + " &"
                            print "cmd0 is",cmd0
                            print "cmd1 is",cmd1
                            os.system(cmd0)
                            os.system(cmd1)
    		        elif fwd_mode != None:
                            print "cmd_checksum is",cmd_checksum
                            process  = subprocess.Popen(cmd_checksum, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            error_out = process.stderr.read()
                            test_out = process.stdout.read()
                            print "error_out is",error_out
                            print "test_out is",test_out
                                
                        else:
                            print "cmd0 is",cmd0
                            process  = subprocess.Popen(cmd0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            error_out = process.stderr.read()
                            test_out = process.stdout.read()
                            print "error_out is",error_out
                            print "test_out is",test_out
    
            os.system("killall -s 9 get_rxtx_throughput.sh")
            #print "AFTER KILL"
            connect_sock.send("SYNC 1 DONE") # send the data
            #print "AFTER SEND"
            data = connect_sock.recv(BUF_LEN)
            #print "AFTER CONNECT"
            if vlan :
                remVlan(cip)
            connect_sock.send("SYNC 3 DONE") # send the data
            data = connect_sock.recv(BUF_LEN)
            #Rx = connect_sock.recv(BUF_LEN)
            #Tx = connect_sock.recv(BUF_LEN)
            print "Data is", data
            
            passPrint()
            sys.exit(0)
    '''
    except Exception, e:
        print "Error :  ",e
        if is_s == True:
            results_file = open('/download/performance_result/%s.csv' %(msgSize),'a')
            results_file.write('0,	0\n')
        sys.exit(1)
    '''    
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
