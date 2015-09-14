#!/usr/bin/python
import os
import sys
import getopt
import time

try:
    sys.path += [os.environ['TEST_SUITE_PATH'] + os.sep + 'lib']
    sys.path += [os.environ['TEST_SUITE_PATH'] + os.sep + 'bin']
    import common
    import vl
    import sock_sync

except:
    vl.MISC_ERR ("Cannot import common.py (check TEST_SUITE_PATH)")
    sys.exit(1)

class bcolors:
    HELP = '\033[94m'
    HEADER = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    RESET  = '\033[37m'

def usage():
    print "Run Command is : ./ping.py --ip=<ip> --msg_size=<msg_size> --iter_num=<iter_num> --timeout=<timeout>"

def parser(args):
    ip = None
    msg_size = ''
    iter_num = ''
    timeout = ''

    opts,extraparams= getopt.getopt(args[1:],"h",['ip=','msg_size=','iter_num=','timeout='])
    if (len(extraparams)!=0):print('Error :'),sys.exit(1)
    for o,p in opts:
        if o in ['--help','-h']:
            usage()
            sys.exit(1)
        elif o in ['--ip']:
            ip = p
        if o in ['--msg_size']:
            msg_size = p
        if o in ['--iter_num']:
            iter_num = p
        if o in ['--timeout']:
            timeout = p


    if (str(ip) == ''):
        vl.MISC_ERR(("ERROR: IP Parameter is Mandatory \n"));
        sys.exit(1)

    if (str(msg_size) == ''):
        vl.MISC_ERR(("ERROR: Message Size is Mandatory \n"));
        sys.exit(1)
    
    if (str(iter_num) == ''):
        vl.MISC_ERR(("ERROR: Iteration Number is Mandatory \n"));
        sys.exit(1)

    if (str(timeout) == ''):
        timeout = 5

    return ip, msg_size, iter_num, timeout

def run(cmd):
    stdout_handle = os.popen(cmd)
    out = stdout_handle.read()
    return out

def generate_cmd():
    ip, msg_size, iter_num, timeout = parser(sys.argv)
    cmd="/bin/ping " 
    if(not(ip == None)):
        cmd+=str(ip)

    if(not(iter_num == None)):
        cmd+= " -c " + str(iter_num)

    if(not(msg_size == None)):
        cmd+= " -s " + str(msg_size)

    cmd+= " -timeout=" + str(timeout)
        
    return cmd, iter_num

def main():
    cmd, iter_num = generate_cmd()
    print cmd
    out = run(cmd)
    print out
    if not ((iter_num + " packets transmitted") in out):
        vl.MISC_ERR(("Test Fail: packets transmitted is 0 \n"));
        return -1
    if not ((iter_num + " received") in out):
        vl.MISC_ERR(("Test Fail: packets received is 0 \n"));
        return -1
    if (not("0% packet loss" in out)):
        vl.MISC_ERR(("Test Fail: packets lost not 0 \n"));
        return -1
    return 0

res = main()
if (res == -1):
    vl.MISC_ERR(("Test Fail \n"));
    sys.exit(1)
