#!/usr/bin/python

try:
    import os
    import re
    import sys
    import time
    import socket
    import random
    import psutil
    import signal
    import argparse
    import datetime
    import netifaces
    import subprocess
    import SocketServer
    import copy as _copy
    from netutils import Route
    from threading import Thread
except Exception,e:
    print '-E- can not import file %s' % (e)
    sys.exit(1)

FAIL = 1
PID = None
SUCCESS = 0
STDOUT = None
STDERR = None
TMP = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
#TMP = '/share/vma/vma_tar/'

try:
    logFile = open('%s/SockperfWrapper.log' % (TMP), 'aw+')
    #os.chmod('%s/SockperfWrapper.log' % (TMP), 777)
except Exception,e:
    print '-E- %s' % (e)
    sys.exit(FAIL)

####################################################################
class Bcolors:
    """
    Class : Bcolors
    Description : Set terminal color to help the user
    """
    HELP	= '\033[96m'
    HEADER	= '\033[94m'
    OKGREEN	= '\033[92m'
    WARNING	= '\033[93m'
    FAIL	= '\033[91m'
    ENDC	= '\033[0m'
    RESET	= '\033[37m'

####################################################################
def _ensureValue(namespace, name, value):
    if getattr(namespace, name, None) is None:
        setattr(namespace, name, value)
    return getattr(namespace, name)

####################################################################
class _addToStringAction(argparse.Action):
    def __init__(self,option_strings,dest,nargs=None,const=None,default=None,type=None,choices=None,required=False,help=None,metavar=None):
        super(_addToStringAction, self).__init__(option_strings=option_strings,dest=dest,nargs=nargs,const=const,default=default,type=type,choices=choices,required=required,help=help,metavar=metavar)
    
    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(_ensureValue(namespace, self.dest, ''))
        if self.option_strings[0] in items:
            print '-E- Its not allowed to have duplicated argument. Argument %s is duplicated' % (self.option_strings[0])
            sys.exit(1)
        items += ' %s' % (self.option_strings[0])
        if len(values):
            items += ' %s' % (values[0])
        setattr(namespace, self.dest, items)

####################################################################
class _addFlagToStringAction(argparse.Action):
    def __init__(self,option_strings,dest,nargs=None,const=None,default=None,type=None,choices=None,required=False,help=None,metavar=None):
        super(_addFlagToStringAction, self).__init__(option_strings=option_strings,dest=dest,nargs=nargs,const=const,default=default,type=type,choices=choices,required=required,help=help,metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = _copy.copy(_ensureValue(namespace, self.dest, ''))
        if self.option_strings[0] in items:
            print '-E- Its not allowed to have duplicated argument. Argument %s is duplicated' % (self.option_strings[0])
            sys.exit(1)
        if re.match(r'-+\w+',self.option_strings[0]):
            p = re.compile(r'-+')
            self.option_strings[0] = p.sub('', self.option_strings[0])
        items += ' %s' % (self.option_strings[0])
        if len(values):
            items += ' %s' % (values[0])
        setattr(namespace, self.dest, items)

####################################################################
def parseArg():
    parser = argparse.ArgumentParser(prog='sockperfWrapper.py', description='This is the sockperf wrapper')
    parser.add_argument('-d','--daemon',action='store_true',default=False,help='Is daemon (Default: False)')
    parser.add_argument('--cip',action='store',required=True,type=str,help='Client IP address',metavar='IP')
    parser.add_argument('--mip',action='store',required=True,type=str,help='Management IP address',metavar='IP')
    parser.add_argument('-i','--ip',action='store',required=True,type=str,help='Listen on/send to ip <ip>.',metavar='IP')
    parser.add_argument('-p','--port',action='store',default=11111,type=int,help='Listen on/connect to port <port> (Default: 11111).',metavar='PORT')
    parser.add_argument('--activity',action=_addToStringAction,nargs=1,type=int,help='Measure activity by printing a \'.\' for the last <N> messages processed',dest='command',metavar='N')
    parser.add_argument('--Activity',action=_addToStringAction,nargs=1,type=int,help='Measure activity by printing the duration for last <N>  messages processed.',dest='command',metavar='N')
    parser.add_argument('--mc-loopback-enable',action=_addToStringAction,nargs=0,help='Enables mc loopback (default: Disabled)',dest='command')
    parser.add_argument('--vmazcopyread',action=_addToStringAction,nargs=0,help='If possible use VMA\'s zero copy reads API (See VMA\'s readme)',dest='command')
    parser.add_argument('--nonblocked',action=_addToStringAction,nargs=0,help='Open non-blocked sockets.',dest='command')
    parser.add_argument('--dontwarmup',action=_addToStringAction,nargs=0,help='Don\'t send warm up messages on start',dest='command')
    parser.add_argument('--buffer-size',action=_addToStringAction,nargs=1,type=long,help='Set total socket receive/send buffer <size> in bytes (system defined by default)',dest='command',metavar='SIZE')
    parser.add_argument('--msg-size',action=_addToStringAction,nargs=1,default=12,type=long,help='Use messages of size <size> bytes (Minimum Default: 12)',dest='command',metavar='SIZE')
    parser.add_argument('--mps',action=_addToStringAction,nargs=1,type=str,help='Set number of messages-per-second (Default = 10000 - for under-load mode, or max - for ping-pong and throughput modes',\
                            dest='clientCommand',metavar='MPS')
    parser.add_argument('--burst',action=_addToStringAction,nargs=1,type=long,help='Control the client\'s number of a messages sent in every burst',dest='command',metavar='N')
    parser.add_argument('--time',action=_addToStringAction,nargs=1,default=1,type=long,help='Run for <sec> seconds (Default 1, max = 36000000)',dest='clientCommand',metavar='TIME')
    parser.add_argument('--tcp',action='store_true',default=False,help='Use TCP protocol (Default: UDP)')
    parser.add_argument('--iomux-type',action=_addToStringAction,nargs=1,default='select',type=str,help='Type of multiple file descriptors handle [s|select|p|poll|e|epoll|r|recvfrom](default select)',\
                            dest='command',metavar='IOMUX')
    parser.add_argument('--file',action=_addToStringAction,nargs=1,default='feedFile',type=str,help='Read multiple ip+port combinations from file <file> (server uses select)',dest='command',metavar='FILE')
    parser.add_argument('--timeout',action=_addToStringAction,nargs=1,default=10,type=int,help='Set select/poll/epoll timeout to <msec>, -1 for infinite (Default is 10 msec)',dest='command',metavar='TIME')
    parser.add_argument('--mc-rx-if',action=_addToStringAction,nargs=1,type=str,help='Address of interface on which to receive mulitcast messages (can be other than route table)',dest='command',metavar='IP')
    parser.add_argument('--mc-tx-if',action=_addToStringAction,nargs=1,type=str,help='Address of interface on which to transmit mulitcast messages (can be other than route table)',dest='command',metavar='IP')
    parser.add_argument('--mc-ttl',action=_addToStringAction,nargs=1,type=int,help='Limit the lifetime of the message (Default: 2)',dest='command',metavar='TTL')
    parser.add_argument('--pre-warmup-wait',action=_addToStringAction,nargs=1,type=int,help='Time to wait before sending warm up messages (seconds)',dest='command',metavar='TIME')
    parser.add_argument('--no-rdtsc',action=_addToStringAction,nargs=0,help='Don\'t use register when taking time; instead use monotonic clock.',dest='command')
    parser.add_argument('-pp','--ping-pong',action=_addFlagToStringAction,nargs=0,help='Run sockperf client for latency test in ping pong mode.',dest='clientCommand')
    parser.add_argument('-pb','--playback',action=_addFlagToStringAction,nargs=0,help='Run sockperf client for latency test using playback of predefined traffic, based on timeline and message size.',dest='clientCommand')
    parser.add_argument('-ul','--under-load',action=_addFlagToStringAction,nargs=0,help='Run sockperf client for latency under load test.',dest='clientCommand')
    parser.add_argument('-tp','--throughput',action=_addFlagToStringAction,nargs=0,help='Run sockperf client for one way throughput test.',dest='clientCommand')
    parser.add_argument('-sr','--server',action=_addFlagToStringAction,nargs=0,help='Run sockperf as a server.',dest='serverCommand')
    parser.add_argument('--servers',action='store',default=1,type=int,help='The number of servers to be started',metavar='N')
    parser.add_argument('-m','--mode',action='store',default=1,type=int,help='The mode to run sockperf with',choices=[1,2,3,4],metavar='N')
    parser.add_argument('--multicast',action='store_true',default=False,help='Generate multicast traffic')
    parser.add_argument('--sockets',action='store',default=1,type=int,help='The number of sockets in the sockperf feed file',metavar='N')
    parser.add_argument('--multi-port',action='store_true',default=False,help='Generate traffic across multiple ports')
    parser.add_argument('--mixed-file',action='store_true',default=False,help='Generate a mixed feed file')
    parser.add_argument('--VMA_APPLICATION_ID',action='store',help='VMA application ID')
    parser.add_argument('--VMA_CONFIG_FILE',action='store',help='VMA configuration file')
    parser.add_argument('--VMA_STATS_FILE',action='store',help='The output file for the VMA state')
    parser.add_argument('--clients',action='store',default=1,type=int,help='The number of clients ',metavar='N')
    parser.add_argument('--management',action='store_true',default=False,help='Use management interface')
    parser.add_argument('--max-memory',action='store_true',default=False,help='Use maximum memory availble on the machine')
    parser.add_argument('--syncPort',default=20200,type=int,help='The server/client sync port',metavar='N')
    args = parser.parse_args()
    print args.command 
    print args.multicast
    return args

####################################################################
def runCommand(cmd):
    proc = subprocess.Popen(cmd, shell = True, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.wait() != 0:
        msg =  '-E- Failed to run: %s. Error: %s' % (cmd,str(stderr))
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL
    return SUCCESS,stdout

####################################################################
def getAllUpInterfaces():
    allInterfaces = {}
    testedInterfaces = {}
    try:
        interfaces =  netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs.keys():
                if interface != 'lo':
                    ip = addrs[netifaces.AF_INET][0]['addr']
                    managementIP = socket.gethostbyname(socket.gethostname())
                    allInterfaces[interface] = ip
                    if ip != managementIP:
                        testedInterfaces[interface] = ip
        return SUCCESS,allInterfaces,testedInterfaces
    except Exception,e:
        msg =  '-E- Failed to get all up interfaces on the machine. Error: %s' % (e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL,allInterfaces,testedInterfaces

####################################################################
def preRunConfigurations(args, allInterfaces, testedInterfaces):
    feedFile = None
    if '--file' in args.command:
        result = re.search(r'--file \w+',args.command)
        feedFile = result.group(0).split('--file ')[1]
        args.command = args.command.replace('--file %s' % (feedFile),'--file %s/%s' % (TMP,feedFile))
        if args.daemon:
            if args.mixed_file:
                rc = generateMixedFeedFile(args.sockets, feedFile, allInterfaces, testedInterfaces, args.multi_port, args.ip)
            else:
                rc = generateFeedFile(args.sockets, feedFile, testedInterfaces, args.tcp, args.multicast, args.management, args.multi_port, args.ip, args.mip)
            if rc == FAIL:
                return FAIL,feedFile
    return SUCCESS,feedFile

####################################################################
def prepareSockperfCommands(args, feedFile):
    if feedFile == None:
        if args.management:
            args.command += ' --ip %s' % (args.mip)
        elif args.multicast:
            args.command += ' --ip %s' % ('224.%s.10.1' % args.ip.split(".")[3])
        else:
            args.command += ' --ip %s' % (args.ip)
        args.command += ' --port %d' % (args.port)
        if args.tcp:
            args.command += ' --tcp'
    args.serverCommand = 'sockperf %s %s' % (str(args.serverCommand),args.command)
    args.clientCommand = 'sockperf %s %s' % (str(args.clientCommand),args.command)
    print 'args.serverCommand',args.serverCommand
    print 'args.clientCommand',args.clientCommand

####################################################################
def intToBin(integer, bits = 5):
    return "".join([str((integer >> y) & 1) for y in range(bits - 1, -1, -1)])

####################################################################
def generateMixedFeedFile(sockets, feedFile, allInterfaces, testedInterfaces, multiPort, ip):
    try:
        mixedFeedFile = open('%s/%s' % (TMP,feedFile), 'w+')
        multicastGroup = ['224','239']
        allInterfacesKeys = allInterfaces.keys()
        testedInterfacesKeys = testedInterfaces.keys()
        randomPort = random.randint(10000,29499)
        for i in range(sockets):
            randomType = random.randint(0,2)
            randomInterface = random.randint(0,len(allInterfacesKeys) - 1)
            if randomType == 0:
                mixedFeedFile.write('T:%s:%d\n' % (interfaces[allInterfacesKeys[randomInterface]],randomPort + i))
            elif randomType == 1:
                mixedFeedFile.write('U:%s:%d\n' % (interfaces[allInterfacesKeys[randomInterface]],randomPort + i))
            else:
                if multiPort:
                    randomMulticastRange = random.randint(0,len(testedInterfacesKeys) - 1)
                    part1 = str(intToBin(int(testedInterfaces[testedInterfacesKeys[randomMulticastRange]].split(".")[3])))
                    part2 = str(intToBin(int(testedInterfaces[testedInterfacesKeys[randomMulticastRange]].split(".")[0]) - 10, 3))
                    testedIp = '%s.%s.%s.%s' % (multicastGroup[randomMulticastRange],str(int(part1 + part2, 2)),random.randint(2,224),random.randint(2,224))
                    mixedFeedFile.write('U:%s:%d\n' % (testedIp,randomPort + i))
                else:
                    testedIp = '224.%s.%d.%d' % (ip.split(".")[3],random.randint(2,224),random.randint(2,224))
                    mixedFeedFile.write('U:%s:%d\n' % (testedIp,randomPort + i))
        mixedFeedFile.close()
        return FAIL
    except Exception,e:
        msg =  '-E- Failed to generate the sockperf mixed feed file. Error: %s' % (e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL

####################################################################
def generateFeedFile(sockets, feedFile, testedInterfaces, tcp, multicast, management, multiPort, ip, managementIp):
    try:
        sockperfFeedFile = open('%s/%s' % (TMP,feedFile), 'w+')
        randomInterface = 0
        multicastGroup = ['224','239']
        randomPort = random.randint(10000,29499)
        testedInterfacesKeys = testedInterfaces.keys()
        if management:
            ip = managementIp
        else:
            if multiPort:
                testedInterfacesKeys = testedInterfaces.keys()
                randomInterface = random.randint(0,len(testedInterfacesKeys) - 1)
                ip = testedInterfaces[testedInterfacesKeys[randomInterface]]            
        for i in range(sockets):
            if multicast:
                part1 = ip.split(".")[3]
                if multiPort:
                    part1 = str(int(str(intToBin(int(part1))) + str(intToBin(int(ip.split(".")[0]) - 10, 3)),2))
                testedIp = '%s.%s.%s.%s' % (multicastGroup[randomInterface],part1,random.randint(2,224),random.randint(2,224))
                sockperfFeedFile.write('U:%s:%d\n' % (testedIp,randomPort + i))
            else:
                if tcp:
                    sockperfFeedFile.write('T:%s:%d\n' % (ip,randomPort + i))
                else:
                    sockperfFeedFile.write('U:%s:%d\n' % (ip,randomPort + i))            
        sockperfFeedFile.close()
        return SUCCESS
    except Exception,e:
        msg =  '-E- Failed to generate the sockperf feed file. Error: %s' % (e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL

####################################################################
def addRoute(daemon, ip, cip, multiPort, testedInterfaces):
    port1 = 0
    port2 = 0
    try:
        if not daemon:
            ip = cip
        routes = Route.read_route_table()
        for interface,interfaceIp in testedInterfaces.iteritems():
            if interfaceIp == ip:
                port1 = interface
            else:
                port2 = interface
        route1 = Route('224.0.0.0','0.0.0.0',port1,'240.0.0.0')
        route2 = Route('239.0.0.0','0.0.0.0',port2,'255.0.0.0')
        rc = checkRoute(routes,'240.0.0.0')
        if rc == FAIL:
            return FAIL
        Route.add(route1)
        if multiPort:
            rc = checkRoute(routes,'239.0.0.0')
            if rc == FAIL:
                return FAIL
            Route.add(route2)
        return SUCCESS
    except Exception,e:
        msg =  '-E- Failed to add the multicast routes on the machine. Error: %s' % (e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL
    
####################################################################
def checkRoute(routes, multicastRange):
    try:
        match = [route for route in routes if multicastRange in str(route)]
        if len(match) != 0:
            Route.delete(match[0])
        return SUCCESS
    except Exception,e:
        msg =  '-E- Failed to check existing routes on the machine. Error: %s' % (e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL

####################################################################
def sync(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SocketServer.TCPServer.allow_reuse_address = True
    SocketServer.TCPServer.allow_reuse_port = True
    if args.daemon:
        try:
            s.bind((args.mip, args.syncPort))
            s.listen(5)
            connection, address = s.accept()
        except Exception,e:
            msg =  '-E- Server Sync Error. Error: %s' % (e)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
    else:
        while (True):
            try:
                s.connect((args.mip, args.syncPort))
                time.sleep(2)
                break;
            except Exception,e:
                if ((str(e).split(" ")[2] == "Connection") and (str(e).split(" ")[3] == "refused")):
                    continue
                else:
                    return FAIL
    s.close()
    args.syncPort += 1
    return SUCCESS

####################################################################
def checkVMA():
    if os.environ.get('VMA_LOAD') == None or os.environ.get('VMA_LOAD') == '':
        msg =  '-E- Failed to load VMA. Error: VMA_LOAD is not set' 
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL
    else:
        return os.environ.get('VMA_LOAD')
        
####################################################################
def main():            
    args = parseArg()
    (rc,allInterfaces,testedInterfaces) = getAllUpInterfaces()
    if rc == FAIL:
        return FAIL
    rc = addRoute(args.daemon, args.ip, args.cip, args.multi_port, testedInterfaces)
    if rc == FAIL:
        return FAIL
    rc,feedFile = preRunConfigurations(args, allInterfaces, testedInterfaces)
    if rc == FAIL:
        return FAIL
    rc = sync(args)
    if rc == FAIL:
        return FAIL
    prepareSockperfCommands(args, feedFile)
    vma = checkVMA()
    if vma == FAIL:
        return FAIL
    if args.mode == 1:
        rc = RunSockperfWithAllCombinations(args, vma)
    return rc 

####################################################################
def checkResults(rc):
    if rc == FAIL:
        print Bcolors.FAIL + "\t\t\t---------------------Test Result---------------------"
        print Bcolors.FAIL + "\t\t\t                    [TEST FAILED]                    "
        print Bcolors.FAIL + "\t\t\t-----------------------------------------------------" + Bcolors.RESET
    else:
        print Bcolors.OKGREEN + "\t\t\t---------------------Test Result---------------------"
        print Bcolors.OKGREEN + "\t\t\t                    [TEST PASSED]                    "
        print Bcolors.OKGREEN + "\t\t\t-----------------------------------------------------" + Bcolors.RESET

####################################################################
def RunSockperfWithAllCombinations(args, vma):
    global PID
    status = SUCCESS
    serverCommand = args.serverCommand
    clientCommand = args.clientCommand
    serverCombinations = [True,False,True]
    clientCombinations = [False,True,True]
    for i in range(len(serverCombinations)):
        if serverCombinations[i]:
            serverCommand = 'LD_PRELOAD=%s %s' % (vma, args.serverCommand)
        if clientCombinations[i]:
            clientCommand = 'LD_PRELOAD=%s %s' % (vma, args.clientCommand)
        if args.daemon:
            rc = threadRun(serverCommand, 250, False)
        rc = sync(args)
        if rc == FAIL:
            return FAIL
        if not args.daemon:
            rc = threadRun(clientCommand, 250, True)
        rc = sync(args)
        if rc == FAIL:
            return FAIL
        if args.daemon:
            if psutil.pid_exists(int(PID)):
                os.kill(int(PID), signal.SIGINT)
                print '-I- aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa Command: %s with PID: %s is killed' % (serverCommand,str(PID))
            time.sleep(5)
            rc = parseSockperfServerOutput()
            if rc == FAIL:
                status = FAIL
        else:
            time.sleep(5)
            rc = parseSockperfClientOutput()
            if rc == FAIL:
                status = FAIL
        rc = sync(args)
        if rc == FAIL:
            return FAIL
        time.sleep(5)
        PID = None
    return status

####################################################################
def parseSockperfServerOutput():
    totalReceivedMessages = None
    outputLines  = STDOUT.split('\n')
    for line in outputLines:
        if 'VMA ERROR' in line and 'fork' not in line:
            msg =  '-E- VMA ERROR: Sockperf Server Error: %s' % (line)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
        if 'VMA PANIC' in line:
            msg =  '-E- VMA PANIC: Sockperf Server Error: %s' % (line)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
        if 'sockperf: Total ' in line:
            totalReceivedMessages = line.split('sockperf: Total')[1].split('messages')[0].strip()
            print '-I- Sockperf: Total messages received on the server side is %s ' % (totalReceivedMessages)
        if 'sockperf: No messages were received on the server' in line:
            msg =  '-E- Sockperf Server Error: No messages were received on the server' 
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
    return totalReceivedMessages

####################################################################
def parseSockperfClientOutput():
    output = None
    outputLines = STDOUT.split('\n')
    for line in outputLines:
        if 'VMA ERROR' in line and 'fork' not in line:
            msg =  '-E- VMA ERROR: Sockperf Client Error: %s' % (line)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
        if 'VMA PANIC' in line:
            msg =  '-E- VMA PANIC: Sockperf Client Error: %s' % (line)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
        if 'ERROR' in line:
            msg =  '-E- Sockperf Client Error: %s' % (line)
            print msg
            now = datetime.datetime.now()
            logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
            return FAIL
        if 'sockperf: Summary: Latency is' in line:
            output = line.split('sockperf: Summary: Latency is')[1].split('usec')[0].strip()
            print '-I- Sockperf: Latency is %s ' % (output)
        if 'sockperf: Summary: BandWidth is' in line:
            output = line.split('sockperf: Summary: BandWidth is')[1].split('MBps')[0].strip()
            print '-I- Sockperf: BandWidth is %s ' % (output)
        if 'dropped messages' in line:
            droppedMessages = line.split('dropped messages =')[1].split(';')[0].strip().split('\x1b[0m')[0]
            duplicatedMessages = line.split('duplicated messages =')[1].split(';')[0].strip().split('\x1b[0m')[0]
            outOfOrderMessages = line.split('out-of-order messages =')[1].split(';')[0].strip().split('\x1b[0m')[0]
            if int(droppedMessages) != 0 or int(duplicatedMessages) != 0 or int(outOfOrderMessages) != 0:
                msg =  '-E- Sockperf Client Error: Dropped messages = %s, duplicated messages = %s, out of order messages = %s' % (droppedMessages,duplicatedMessages,outOfOrderMessages)
                print msg
                now = datetime.datetime.now()
                logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
                return FAIL
    return output

####################################################################
def threadRun(command, time = False, join = False):
    try:
        thread = Thread(target=run, args = (command,  ))
        thread.start()
    except Exception,e:
        msg =  '-E- Failed to run sockperf. Error: An error occured while executing %s' % (command)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL
    if time:
        if join:
            print '-I- Pending on thread PID %s'  % (PID)
            thread.join(int(time))
            while(PID == None):
                pass
            if psutil.pid_exists(int(PID)):
                os.kill(int(PID), signal.SIGINT)
                print '-I- Command: %s with PID: %s is killed' % (command,str(PID))
        else:
            try:
                thread1 = Thread(target=sleepTime, args = (command, int(time), True,  ))
                thread1.start()
                print '-I- Command: %s with PID: %s will be killed after %s' % (command, PID, time)
            except Exception,e:
                msg =  '-E- Failed to put command %s on sleep. Error: %s' % (command,e)
                print msg
                now = datetime.datetime.now()
                logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
                return FAIL
    return SUCCESS

####################################################################
def sleepTime(command, sleepDuration, kill = False):
    #os.system("/bin/sleep " + str(sleep_time))
    try:
        time.sleep(int(sleepDuration))
        if kill:
            while(PID == None):
                pass
            if psutil.pid_exists(int(PID)):
                os.kill(int(PID), signal.SIGINT)
                print '-I- Command: %s with %s: PID is killed'  % (command,PID)
        return SUCCESS
    except Exception,e:
        msg =  '-E- Failed to kill command %s. Error: %s' % (command,e)
        print msg
        now = datetime.datetime.now()
        logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
        return FAIL

####################################################################
def run(command):
    global PID, STDOUT, STDERR
    try:
        proc = subprocess.Popen(command, shell = True, stderr = subprocess.PIPE, stdout = subprocess.PIPE)
        while(PID == None):
            PID = proc.pid
        print '-I- Executing command: %s. PID %s' % (command,PID) 
        STDOUT,STDERR = proc.communicate()
        rc = proc.wait()
        if STDOUT:
            print '-I- Output of executing command %s: %s' % (command,STDOUT)
        if STDERR:
            return FAIL,STDOUT,PID
        return SUCCESS,STDOUT,PID
    except Exception,e:
         msg =  '-E- Failed to execute command: %s. Error: %s' % (command, e)
         print msg
         now = datetime.datetime.now()
         logFile.write(now.strftime('%Y/%m/%d %H:%M:%S: ') + '%s\n' % (msg))
         return FAIL,STDOUT,PID

####################################################################

if __name__ == '__main__': 
    rc = main()
    checkResults(rc)
    logFile.close()
    sys.exit(rc)
