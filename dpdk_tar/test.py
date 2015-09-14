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
    
            accepted_sock.send(RxPacketsRate)
            accepted_sock.send(TxPacketsRate)
    
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
                        clientCommandLine = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8 "
                    else:
                        clientCommandLine = "raw_ethernet_bw --client --CPU-freq -d mlx4_1 -l 8 -D 10 --mtu " + msgSize
                    if RSS:
                        #cmd0 = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --dest_mac=7E:AA:42:56:92:9B -D 10 --mtu " + mtuSet #any MAC address works
                        #cmd1 = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B -D 10 --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 --mtu " + mtuSet
                        cmd0 = "raw_ethernet_bw --client --CPU-freq -i 1 -d mlx4_1 -l 8  --dest_mac=7E:AA:42:56:92:9B -D 10 --mtu " + msgSize
                        cmd1 = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
                        
                    else:
                        cmd0 = clientCommandLine + " -i 2 --dest_mac=f4:52:14:2c:5d:22 "
                        cmd1 = clientCommandLine + " -i 1 --dest_mac=f4:52:14:2c:5d:21 "
    		
            	if fwd_mode != None:
    		    if checksum_flags[0] == True:
    			cmd_checksum = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
    		    if checksum_flags[1] == True or checksum_flags[2] == True:
                            cmd_checksum = "raw_ethernet_bw --client --CPU-freq -i 2 -d mlx4_1 -l 8  --port 9999 --dest_mac=7E:AA:42:56:92:9B --dest_ip " + cip + " --source_ip " + ip + " --source_port 20911 --dest_port 20910  --source_mac F4:52:14:61:9F:F1 -D 10 --mtu " + msgSize
    		    
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
            Rx = connect_sock.recv(BUF_LEN)
            #Tx = connect_sock.recv(BUF_LEN)
            print "Data is", data
            
            passPrint()
            sys.exit(0)
    
