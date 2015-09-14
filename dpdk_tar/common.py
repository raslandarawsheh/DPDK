#!/usr/bin/env python
# -*- python -*-
#
# $Id: common.py,v 1.240 2010/07/12 12:45:40 lawrance Exp $
# Author:  Ali Ayoub  ali@mellanox.co.il -- Created: 2004/Oct
#
import os
import sys
import time
import tempfile
import string
import popen2
import signal
import random
## local imports
try:
    # 2do: tsutils.py should be moved
    sys.path += [os.environ['TEST_SUITE_PATH'] + os.sep + 'lib']
    sys.path += [os.environ['TEST_SUITE_PATH'] + os.sep + 'bin']
    sys.path += [os.path.dirname(os.environ['TEST_SUITE_PATH']) + os.sep + 'bin']
    sys.path += [os.path.dirname(os.path.dirname(os.environ['TEST_SUITE_PATH'])) + os.sep + 'bin']
    import tsutils
except Exception, e:
    print "Cannot import tsutils.py (" + str(e)+")"
    sys.exit(1)
try:
    import opensm
except Exception, e:
    print "Cannot import opensm.py (" + str(e)+")"
    sys.exit(1)
try:
    import ifconfig
except Exception, e:
    print "Cannot import ifconfig.py (" + str(e)+")"
    sys.exit(1)
try:
    import win_ibadm
except Exception, e:
    print "Cannot import win_ibadm.py (" + str(e)+")"
    sys.exit(1)
try:
    import vl
except Exception, e:
    print "Cannot import vl.py (" + str(e)+")"
    sys.exit(1)


FILER = tsutils.get_filer()

#0 - PASSED
#1 - FAILED
#2 - SKIPPED
#3 - MAKE_FAILED

( # Constants
PASSED,
FAILED,
SKIPPED,
MAKE_FAILED
) = range(4);

# global variables
_fileObject = None
_F_devnull = None

# would you include the stderr messages in the error files?
# this hardcoded option related to MySpawn,
# yes=1, No=0
IncludeStderr = 1


# Evaluation
def eval_file(fn):
    return tsutils.eval_file(fn)

# update the environment variables with the effective HCAs 
# same IPs and same IDs, then 2 process should see 2 HCAs, when 1 proccess should see 1 HCA
# => this function should be called in tests with 1 proccess, and then we should check
# if we have the same ip and the same id then the device name env. var. should be changed
def EffectiveHCAs(special_case = None):
    if not special_case:
        HCAs = os.environ['DEV_NAME'].split(';')
        IPs  = os.environ['RHOST'].split(';')

        if IPs[0] == IPs[1]:
            if HCAs[0] == HCAs[1]:
                os.environ['DEV_NAME'] = os.environ['DEV_NAME'].split(';')[0]
                os.environ['MST_DEV'] = os.environ['MST_DEV'].split(';')[0]
        else: # 2 machines
            if IPs[0] == MyIp():
                os.environ['DEV_NAME'] = os.environ['DEV_NAME'].split(';')[0]
                os.environ['MST_DEV'] = os.environ['MST_DEV'].split(';')[0]
            else:
                try:
                    os.environ['DEV_NAME'] = os.environ['DEV_NAME'].split(';')[1]
                    os.environ['MST_DEV'] = os.environ['MST_DEV'].split(';')[1]
                except:
                    pass
    else:
        pass
    return

# this function return the num of effective links (the links that the regression run on them)
def num_effective_links():
    try:
        if isFreeBSD():
           num_links = len(tsutils.str_to_list(os.environ['TS_EFFECTIVE_LINKS']))
        else:     
           num_links = len(eval(os.environ['TS_EFFECTIVE_LINKS']))
    except:
        num_links = 1
    return num_links


# this function return my TSindex
def get_my_TSindex():
	if os.environ.has_key('TS_RUNNER_INDEX'):
		TSindex     = os.environ['TS_RUNNER_INDEX']
	else:
		TSindex     = "0"
	return TSindex


# My grep 
def MyGrep (cmd, string2grep, field_num,txt="None"):
    if cmd==None:
        txt.split(string2grep)[field_num].split(" ")[0].split("\t")[0].split("\n")[0]    
    try:
        return os.popen(cmd).read().split(string2grep)[field_num].split(" ")[0].split("\t")[0].split("\n")[0]
    except:
        return None

# get stack_name from environment variable
def get_stack_name():
    try:
        stack_name = os.environ['MT_STACK_NAME']
    except:
        stack_name = None
    return stack_name
#get multi if ips
def get_multi_ifips():
    if 'MULTI_IF_IPS' in os.environ.keys():
       return os.environ['MULTI_IF_IPS']
    return None
#get mtusib used for shaldag
def get_mtusb_device():
    return tsutils.get_mtusb_device()

# gets an MST device, and returns the device PSID.
# if the function fails, "None" is returned. 
def get_psid(mst_dev):
    try:
        fd = os.popen("flint -d " + mst_dev + " q")
        lines = fd.readlines()
        fd.close()
    except Exception, e:
        print "Got exception when trying to get the device PSID (exception: %s)" % str(e)
        return None

    psid = None
    for line in lines:
        if line.find("PSID") != -1:
            psid = line.split()[1].rstrip("\n")

    if not psid:
        print "Failed to get the device PSID."

    return psid

# gets the given attribute from vstat,
# a list is returned, including the found strings
# an empty string is returned if the attr was not found.
def VstatGetAttr (dev_name,attr):
    return tsutils.VstatGetAttr (dev_name,attr)
 
# gets the given attribute from vstat verbose,
# a list is returned, including the found strings
# an empty string is returned if the attr was not found.
def VerboseGetAttr (attr):
    return tsutils.verbose_get_attr(attr)

# gets the given attribute from flint,
# a list is returned, including the found strings
# an empty string is returned if the attr was not found.
def FlintGetAttr (mst_dev,attr):
    AnswerList=[]
    if is_ib():
        cmd = "flint -d " + mst_dev + " q"    
        output = os.popen(cmd).read()
        print str(output)
        last_index=0
        for index in range(output.count(attr)):    
            start = output.find(attr+':',last_index)+len(attr+':')
            end = min(output.find('\n',start),output.find('\t',start),output.find(' ',start))
            last_index=start
            if (start==len(attr+'=') | end==-1):
                break
            AnswerList+=[output[start:end]]       
    return AnswerList 


# return the mst device according to the given HCA name,
# None is returned if the HCA is not found
def MstDev(dev_name, dev_ip = None):
    return tsutils.mst_devname(dev_name, dev_ip)

# restarts VAPI with the given flags
def DoRestart (flags="",exitIfFail = True):    
    rc=1
    if is_ib():
        (CurrentFD,CurrentTF) = TempFileDescriptor('VapiRestart')
        if tsutils.isLinux():        
            cmd= [os.environ['TEST_SUITE_PATH']+"/lib/vapi_restart",flags]
            rc = MySpawn(cmd,0,child_stdout = CurrentFD,child_stderr = CurrentFD)    
        elif tsutils.isWIN():
            # if is windows, stop smpd service first
            #print "DoRestart::" + "net stop mpich2_smpd"
            #is_smpd_out = RunCmdGetOutput("net stop mpich2_smpd")
            #is_smdp = True
            #if (is_smpd_out.find("not") != -1):
            #    is_smdp = False
            cmd= [os.environ['MT_TOOLS_PATH']+os.sep+get_PLATF()+os.sep+'vapi.bat','restart',flags]
            print "DoRestart:: cmd=" + str(List2String(cmd))
            rc = MySpawn(cmd,0,child_stdout = CurrentFD,child_stderr = CurrentFD)            
            #if (is_smdp):
            #    print "DoRestart:: "+ "net start mpich2_smpd"
            #    RunCmdGetOutput("net start mpich2_smpd")
        else:
            test_exit(FAILED,"DoRestart::Unknown OS!!")
        if rc != 0:
            PrintFile(CurrentTF)
            CloseFDs([CurrentFD])
            DeleteFile(CurrentTF)
            cmd = List2String(cmd)
            if (exitIfFail):
                CloseFDs([CurrentFD])
                DeleteFile(CurrentTF)
                test_exit(FAILED,"DoRestart failed, cmd=%s, rc = %d" % (cmd,rc))
    
        CloseFDs([CurrentFD])
        DeleteFile(CurrentTF)
        print "DoRestart:: rc=" + str(rc)
    else:
        test_exit(FAILED,"DoRestart failed - Regression Mode is not IB")
    return rc

# minism
# don't use spawn, cause 'echo xq' will not work
# don't use subproc.run_command cause 
# the regression already used it to call the test_suite_runner.py
def start_sm (HCAs,suffix = ""):    
    rc=1
    if is_ib():
        for HCA in HCAs:
            if suffix.find("MACOS`") != -1:
                cmd = "/usr/bin/linkup --lid1=1 --lid2=2 "
                rc = os.system(cmd)
            elif tsutils.isLinux():
                cmd ='echo "xq" | minism ' + HCA
                rc = os.system(cmd)
            elif tsutils.isWIN():            
                cmd ='minism ' + HCA
                (in_fd,out_fd) = os.popen2(cmd)
                in_fd.write("xq")
                in_fd.close()
                if (out_fd.read().find("Automatic Sweep iteration Done") != -1): #is ok
                    CloseFDs([out_fd])            
                    rc =0
                else:
                    print out_fd.read()
                    CloseFDs([out_fd])                            
                    rc = 1
            else:
                test_exit(FAILED,"minism::Unknown OS!!")
    
            if (rc == 1):
                test_exit(FAILED,"minism::failed, cmd= %s" % cmd)
    else:
        test_exit(FAILED,"start_sm::failed - Regression Mode is not IB")

#SM_sweep
def SmSweep (hca_id,port):    
    if is_ib():
        if tsutils.isLinux():
            guid = GetGuid(hca_id, port)
            cmd ='opensm -r -o -g ' + guid 
            rc = os.system(cmd)
            if rc != 0x0:
                print " ** ERROR ** opensm fail"
        elif tsutils.isWIN():
            cmd ='opensm -r -o -g' + guid 
        else:
            test_exit(FAILED,"opensm::Unknown OS!!")
        
        (in_fd,out_fd) = os.popen2(cmd)
        #in_fd.write("xq")
        in_fd.close()
        # check result
        if (out_fd.read().find("SUBNET UP") != -1): #is ok
            CloseFDs([out_fd])            
        else:
            print out_fd.read()
            CloseFDs([out_fd])
            test_exit(FAILED,"opensm::failed, cmd= %s" % cmd)            
            return 1
        return 0
    else:
        test_exit(FAILED,"SmSweep failed - Regression Mode is not IB")
    return 1

# get guid
def GetGuid(hca_id,port):
    if is_ib():
        return tsutils.GetGuid(hca_id,port)
    else:
        test_exit(FAILED,"GetGuid failed - Regression Mode is not IB")

# get lid, list of lids is returned
def GetLid(dev_name,port):
    if is_ib():
        stack_name = get_stack_name()
    
        if not tsutils.isGEN2(stack_name):
            lids  = VstatGetAttr(dev_name,'port_lid')        
        else:
            lids  = VstatGetAttr(dev_name,'Base lid')
        print "GetLid::lids=" + str(lids)
        if (len(lids) < int(port)) or (int(port) not in [1,2]):
            return None
        hexa_lid = lids[int(port)-1]
        lid = hexa_lid
        if not lid.startswith('0x'):
            lid = '0x' + lid
        lid = int(lid,16)
        return str(lid)
    else:
        test_exit(FAILED,"GetLid failed - Regression Mode is not IB")

# run command and get output as a string
def RunCmdGetOutput (cmd):
    fd = os.popen(cmd)
    return fd.read()

# Returns the memory size
def FreeMem():
    try:
        if tsutils.isWIN():  # value returned in WIN in MB
            free_mem = 1024 * int(os.popen("mem").read().split("bytes")[1].split(" ")[-2])
        elif tsutils.isLinux():
            free_mem = int(os.popen("cat /proc/meminfo").read().split("Total:")[1].split(" ")[7])
        else:
            test_exit(FAILED,"FreeMem:: Unknown OS!!")
        return free_mem
    except:
        pass

# Is 2 machines are running?
def Is2Machines ():
    try:
        ip0     = os.environ['RHOST'].split(';')[0]
        ip1     = os.environ['RHOST'].split(';')[1]
    except Exception, e:
        msg = "ERROR:Exception caught while os.environ %s" % e        
        test_exit(FAILED,msg)
    return (ip0 != ip1)


# prepare test to run on two machines
def Run2Machines(NumberOfDaemons,NumberOfClients,my_ip = None):
    # check if the connection is between two different machines
    try:
        ip0     = os.environ['RHOST'].split(';')[0]
        ip1     = os.environ['RHOST'].split(';')[1]
    except Exception, e:
        msg = "ERROR:Exception caught while os.environ %s" % e        
        return (NumberOfDaemons,NumberOfClients)
    if ip0 == ip1:
        return (NumberOfDaemons,NumberOfClients)

    if my_ip == None:
        myip    = MyIp()
    else:
        myip = my_ip

    if (myip == ip0):
        partner_ip = ip1
    elif (myip == ip1):
        partner_ip = ip0
    else:
        msg = 'ERROR:My ip (%s) is not in "connection" variable!' % (myip)
        test_exit(FAILED,msg)

    # update (NumberOfDaemons,NumberOfClients)
    # you are daemon.
    if myip == ip0:
        NumberOfClients = 0
    else: # you are client
        NumberOfDaemons = 0

    return (NumberOfDaemons,NumberOfClients)

# get current OS, Platform, arch, gcc_ver ...
def GetProgPath (TEST_NAME, SD_TEST = 0):
    if SD_TEST == 0:
        if isUNIXBASED():
            if tsutils.isGEN2(get_stack_name()) or get_stack_name() == "SHALDAG_MNG":
                PROG= './'+ TEST_NAME
            else:
                CURR_OS     = tsutils.osname2()
                CURR_PLATF  = tsutils.get_PLATF()
                CONF_SUFFIX = tsutils.get_SUFFIX()
    
                PROG= './obj_'+ CURR_OS +'_'+ CURR_PLATF + CONF_SUFFIX +'/'+ TEST_NAME
            return PROG
        elif tsutils.isWIN():    
            PROG = os.environ['MT_OBJDIR_PATH']+'\\'+ TEST_NAME + '.exe'
            return PROG
        else:
            test_exit(FAILED,"Unknown OS !!")
    else:
        PROG= './bin-vapi/' + TEST_NAME
        return PROG

# return platform from  psinfo, for window only
def GetPlatfByPsinfo(): 
    return tsutils.get_platf_by_psinfo()
# return  platform
def get_PLATF ():
    return tsutils.get_PLATF()
#return osname
def osname():
    return tsutils.osname()
# make list of IPS for mpi run, the length of the list is n
def MpiMakeIpsList(n,ip1,ip2):
    IPs = []
    for i in range(int(n)):
        if i%2:
            IPs += [ip2]
        else:
            IPs += [ip1]
    return IPs


def cluster_parse_args(argv):
    """
    parse arguments, the first 4th parameters are stored in
    envornment variables.
    """

    # export some variables from the command line (support manual execuation)
    if argv[1] == "TSMANUAL":
        #print(str(argv))
        os.environ['SEED']      = argv[2]
        os.environ['TCP_PORT']  = argv[3]
        os.environ['CLUSTER_RHOST'] = argv[4]
        os.environ['MT_STACK_NAME']= argv[5]

        if not os.environ.has_key('MT_COMMDIR'):
            os.environ['MT_COMMDIR'] = '/var/regression_com_dir'
            if isWin():
                os.environ['MT_COMMDIR'] = get_map_name('regression') + os.sep
        os.environ['MT_MODULE_CASE'] = '11;11'
        if isWin():
            if not os.environ.has_key('MT_OBJDIR_PATH'):
                try:
                    MT_ARCH_TARDIR = os.environ['BUILD_DEFAULT_TARGETS'].replace("-3","i3").replace("-",'')
                except:
                    MT_ARCH_TARDIR = 'i386'
                try:
                    os.environ['MT_OBJDIR_PATH'] = "obj" + os.environ['BUILD_ALT_DIR']+ os.sep + str(MT_ARCH_TARDIR)
                except:
                    pass
    # add the list of the LIDs
    # todo - the regression should export this variable
    IBLID = "1;2"
    os.environ['IBLID'] = IBLID

    if argv[1] == 'TSMANUAL':
       remove_items = 5
    else:
       remove_items = 0
    # Shift the 3 magic parameters
    for i in range(remove_items):
        del argv[1]

    # remove  stringa after '#' (if found)
    for i in range(len(argv)-1):
        if argv[i]=='#':
            del argv[i:];
            break;



# parse arguments (depending on the 8 magic variables)
def parse_args (argv):
    """ 
    parse arguments, the first 11th parameters are stored in 
    envornment variables.
    """

    # export some variables from the command line (support manual execuation)
    if argv[1] == "TSMANUAL":
        #print(str(argv)) 
        os.environ['SEED']      = argv[2]
        os.environ['TCP_PORT']  = argv[3]
        os.environ['RHOST']     = argv[4]
        os.environ['DEV_NAME']  = argv[5]
        os.environ['IF_IP']     = argv[6]
        os.environ['IBPORT']    = argv[7]
        os.environ['MT_STACK_NAME']= argv[8]
        os.environ['MT_CONNECTION_ID'] =  argv[9]
        os.environ['TS_CONNECT_LINKS'] =argv[10]
        os.environ['MT_REG_MOD'] = argv[11]
        os.environ['TSRUNNER'] = argv[12]

        reg_mode = tsutils.get_mode()
        if (reg_mode == None):
            ips = str(argv[4]).split(";")
            devs = str(argv[5]).split(";")
            ports = str(argv[7]).split(";")
            try:
               reg_mode = get_mode(ips[0], devs[0], ports[0], ips[1], devs[1], ports[1])
               os.environ['MT_REG_MOD']= str(reg_mode).replace(" ","")
            except:
               os.environ['MT_REG_MOD'] = "['IB']"
        if not os.environ.has_key('MT_COMMDIR'):
            os.environ['MT_COMMDIR'] = '/var/regression_com_dir'
            if isWin():
                os.environ['MT_COMMDIR'] = get_map_name('regression') + os.sep
        os.environ['MT_MODULE_CASE'] = '11;11'
        if isWin():
            if not os.environ.has_key('MT_OBJDIR_PATH'):
                try:
                    MT_ARCH_TARDIR = os.environ['BUILD_DEFAULT_TARGETS'].replace("-3","i3").replace("-",'') 
                except:
                    MT_ARCH_TARDIR = 'i386'
                try:
                    os.environ['MT_OBJDIR_PATH'] = "obj" + os.environ['BUILD_ALT_DIR']+ os.sep + str(MT_ARCH_TARDIR)
                except:
                    pass

    if os.environ['DEV_NAME'].find("[") == -1: 
            #ignore if multi_test_suite_runner call 
	    # compute MST_DEV
	    MST_DEV = ''
	    HCAs_arry = os.environ['DEV_NAME'].split(';')
	    HCAs = []
	    for item in HCAs_arry:
		HCAs.append(tsutils.str_to_list(item)[0])
	    if os.environ.has_key('IF_IP'):
		DEV_IPs = os.environ['IF_IP'].split(';')

	    i = 0
	    for hca in HCAs:
		if os.environ.has_key('IF_IP'):
		    MST_DEV += str(MstDev(hca, DEV_IPs[i])) + ';'
		    i += 1
		else:
		    MST_DEV += str(MstDev(hca)) + ';'

	    MST_DEV = MST_DEV[:-1]
            os.environ['MST_DEV'] = MST_DEV
    # add the list of the LIDs
    # todo - the regression should export this variable
    IBLID = "1;2"
    os.environ['IBLID'] = IBLID

    if argv[1] == 'TSMANUAL':
       remove_items = 12
    else:
       remove_items = 8
    # Shift the 8 magic parameters
    for i in range(remove_items):
        del argv[1]

    # remove  stringa after '#' (if found)
    for i in range(len(argv)-1):
        if argv[i]=='#':            
            del argv[i:];
            break;

# File capture, change the std output to the given file
def CaptureOutput (file = "captureFile.txt"):
    global _fileObject
    _fileObject = open(file,'w')
    sys.stdout = _fileObject

# restore the std output to __stdout__
def RestoreOutput():
    global _fileObject
    sys.stdout = sys.__stdout__
    _fileObject.close()

# print the file
def PrintFile(file = "captureFile.txt"):
    f = open(file, 'r')
    print f.read()    

# clear the contents of the file
def ClearFile (file = "captureFile.txt"):
    f = open(file,'w')
    f.close()
    return f


# Delete the file
def DeleteFile (file = "captureFile.txt"):
    try:
        os.remove(file)
    except OSError, e:
        # file could not be remvod
        print "DeleteFile ERROR %s" % e
        pass


# redirecting the output of a process which was excuted by Spawn (to a file)
# can be done by dup2 the fd of the std* ( using ">" or changing the sys.__stdout__ does
# not work)
# the folowing functions are help functions for MySpawn which do the job
# IMPORTANT: don't mess with __stdin__, this will cause Windows machines to stuck!!!
def F(x,f):
    """Return the file number corresponding to the given object
    F(x) -> fd corresponding to /dev/null if x is None
    F(x) -> x if isinstance(x, int)
    F(x) -> x.fileno() otherwise
    """
    if f is None:
        global _F_devnull
        if _F_devnull is None:
            null_dev = "/dev/null"
            if isWin():
                null_dev = "null"
            _F_devnull = os.open(null_dev, os.O_RDWR)
        return _F_devnull
    if not isinstance(x, int): return x.fileno()


def dup2_noerror(a, b):
    "a dup2 that suppresses all errors.  For use in cleanup"
    try:
        os.dup2(a, b)
    except:
        pass

# all the std* are given as parameters, We assume that args[0] is the command line execution filename
def MySpawn(args,IsParallel=1, child_stdout = sys.__stdout__, child_stderr = sys.__stderr__):
    rc = 1
    if IsParallel:
        flags = os.P_NOWAIT
    else:
        flags = os.P_WAIT

    "Call spawnv with a different set of files for stdin/stdio/stderr"
    f= child_stdout

    # if IncludeStderr flag is off, the stderr error messages will be printed on the screen
    if IncludeStderr==0:
        child_stderr = sys.__stderr__
#    try:
#        sys.stdout.flush()
#        sys.stderr.flush()
#    except:
#        pass
    old_stdout = os.dup(1)
    old_stderr = os.dup(2)
    try:
        #os.dup2(1,1);print 'kuku':  this stuck the python in XP
        if not F(child_stdout,f) == 1:
            os.dup2(F(child_stdout,f), 1)
        os.dup2(F(child_stderr,f), 2)
        try:
           rc = os.spawnv(flags, args[0], args)
        except  Exception, e:
           print "os.spawnv Failed (%s), Try again after 3 sec" % str(e)
           time.sleep(3)
           try:
              rc = os.spawnv(flags, args[0], args)
           except:
              print "os.spawnv Failed again to execute,Check Machine Resources"
        return rc
    finally:
        dup2_noerror(old_stdout, 1)
        dup2_noerror(old_stderr, 2)
        os.close(old_stdout)
        os.close(old_stderr)

# run the given command, don't wait, unless the flag was specified.
# the command is a list when list[0] is the command itself, and list[1:] is the arguments
# the pid is returned, returned value of the command is returned if flag=os.P_WAIT
def run_cmd(cmd, flag = os.P_NOWAIT): # for waiting; os.P_WAIT
    try:
        return os.spawnv(flag, cmd[0], cmd)
    except:
        test_exit(1,"run_cmd::command could not be executed!")

# make a temp file with the given suffix appended, return his name and descriptor
def run_cmd_local(cmd, flag = os.P_NOWAIT, child_stdout = sys.__stdout__, child_stderr = sys.__stderr__): # for waiting; os.P_WAIT
    
    f= child_stdout
    # if IncludeStderr flag is off, the stderr error messages will be printed on the screen
    if IncludeStderr==0:
        child_stderr = sys.__stderr__

    old_stdout = os.dup(1)
    old_stderr = os.dup(2)
    try:
        os.dup2(F(child_stdout,f), 1)
        os.dup2(F(child_stderr,f), 2)
        tsutils.cd(tsutils.get_base_dir(cmd[0]))
        return os.spawnv(flag, cmd[0], cmd)
    finally:
        dup2_noerror(old_stdout, 1)
        dup2_noerror(old_stderr, 2)
        os.close(old_stdout)
        os.close(old_stderr)

def TempFileDescriptor(string):
    #try:        
        #TMPFILE = os.tempnam(os.environ['temp'],'temp'+str)
        #TMPFILE = tempfile.mktemp(str)
        seed = "NO_SEED"
        tmp  = "/tmp"
        if os.environ.has_key('SEED'):
            seed = os.environ['SEED']
        if os.environ.has_key('temp'):
            tmp = os.environ['temp']


        # add rand number to temp file name for dividing between test_suite_runner with multiple processes
        rand_number = random.randint(1,100000)
        ts_index = ""
        if 'TS_RUNNER_INDEX' in os.environ.keys():
            ts_index = os.environ['TS_RUNNER_INDEX']
        TMPFILE = tmp + os.sep + "tmp_" + seed + "_" + str(rand_number) + '_'  + string  + "_" + ts_index
        FileDescriptor = open(TMPFILE,"w+")
        return (FileDescriptor,TMPFILE) 
    #except:
        #test_exit(FAILED,"Error creating temp file")

# print given string then the given list
# if the string is empty, this function actually converts list to string
# (cells are seperated by spaces)
def PrintCommand (string, cmd_list):
    cmd_4_print =''
    for arg in cmd_list:
        cmd_4_print += ' ' + str(arg)
    print string + cmd_4_print
    sys.stdout.flush()

# convert list to string (with spaces)
def List2String (list):
    out_str =''
    for arg in list:
        out_str  +=str(arg)+' '
    return out_str 


# remove the temp files that are in the dictionary (as values)
def RemoveTempFiles(TempFilesList):
    try:
        for file in TempFilesList :
            if tsutils.exists(file):
               os.remove(file)
    # avoiding terminating in case and some files "disappeared", printing an error msg is enough in this case
    except OSError:
        (err1,err2,err3)=sys.exc_info()
        print sys.exc_info()
        #traceback.print_exc(err3)        
        print "Some temp files could not be removed"
        pass

# close the list of File Descriptors
def CloseFDs(FDs):
    for fd in FDs:
        fd.close()

# return last returned value
def ReturnedValue():
    if isWin():
        rc = RunCmdGetOutput("echo %errorlevel%")        
    else:
        rc = RunCmdGetOutput("echo $?")
    rc = HardStrip(rc)
    return int(rc)

# Print the result, output files are printed too in case of failure
def PrintResult(RES,TempFiles,NumberOfClients,NumberOfDaemons,side1 = "Daemon", side2 = "Client", log=None):
    if TempFiles in [None, [] ] :
        if RES == PASSED:
            print "=======================+ Test Passed +===================="
            return PASSED
        elif RES == SKIPPED:
            print "=======================+ Test Skipped +===================="
            return SKIPPED
        else :
            print "=======================+ Test Failed! +===================="
            return FAILED
    if RES == PASSED:
        for n in range(NumberOfDaemons):
            print TempFiles
            print "=======================+ "+ side1+" Output +===================="
            if tsutils.exists(TempFiles[n]):
               PrintFile(TempFiles[n])
            else:
               print "file doesn't exists %s " % TempFiles[n]    

        for n in range(NumberOfDaemons, NumberOfClients + NumberOfDaemons):
            print "=======================+ "+ side2+" Output +===================="
            if tsutils.exists(TempFiles[n]):
               PrintFile(TempFiles[n])

        print "=======================+ Test Passed +===================="
    elif RES == SKIPPED:
        print "=======================+ Test Skipped +===================="
    else: #RES != 0
        for n in range(NumberOfDaemons):
            print "=======================+ "+ side1+" Output +===================="
            if tsutils.exists(TempFiles[n]):
               PrintFile(TempFiles[n])

        for n in range(NumberOfDaemons, NumberOfClients + NumberOfDaemons):
            print "=======================+ "+ side2+" Output +===================="
            if tsutils.exists(TempFiles[n]):
               PrintFile(TempFiles[n])

        print "=======================+ Test Failed! +===================="

    if log != None:
        try:
            print "Write to log: %s" %log
            fd = open(log,'a')
            for n in range(NumberOfDaemons):
                fd.write("=======================+ "+ side1+" Output +====================\n")
                if tsutils.exists(TempFiles[n]):
                   fd2=open(TempFiles[n],'r')
                   lines = fd2.read()
                   fd2.close()
                   fd.write(lines)
    
            for n in range(NumberOfDaemons, NumberOfClients + NumberOfDaemons):
                fd.write("=======================+ "+ side2+" Output +====================\n")
                if tsutils.exists(TempFiles[n]):
                   fd2=open(TempFiles[n],'r')
                   lines = fd2.read()
                   fd2.close()
                   fd.write(lines)

            fd.flush()
            fd.close()

        except Exception, e:
            print "Failed to open log files, %s" % str(e)

    return RES

def MultiPrintResult(RES,TempFiles ,log=None ,verb=0):
    if TempFiles == None:
        if RES == PASSED:
            print "=======================+ Multi Run Tests Passed +===================="
            return PASSED
        else :
            print "=======================+ Multi Run Tests Failed! +===================="
            return FAILED
    if RES == PASSED:
        print "=======================+ Multi Run Tests Passed +===================="
        if verb:
           for temp in TempFiles:
               print "=======================+ "+ temp +" Output +===================="
               if tsutils.exists(temp): 
                  PrintFile(temp) 
    if  RES != PASSED: #RES != 0
        for temp in TempFiles:
            print "=======================+ "+ temp +" Output +===================="
            if tsutils.exists(temp):
               PrintFile(temp)


        print "=======================+ Multi Run Tests Failed! +===================="

    if log != None:
        try:
            print "Write to log: %s" %log
            fd = open(log,'a')
            for temp in TempFiles:
                fd.write("=======================+ "+ temp +" Output +====================")
                fd2=open(temp,'r')
                lines = fd2.read()
                fd2.close()
                fd.write(lines)

            fd.flush()
            fd.close()

        except Exception, e:
            print "Failed to open log files, %s" % str(e)

    return RES

# print the given msg and exit with the given value
def test_exit(return_value, msg = ""):
    print msg
    sys.exit(return_value)

# check path, if not found, exit! 
def CheckPath(Path):
    if os.path.exists(Path)!= 1:
        test_exit(MAKE_FAILED,"ERROR::%s is not found" % Path);

# check the list, if one of its cells is non-zero value, 1 is returned, 0 otherwise
def CheckRCs(RC_LIST):
    for rc in RC_LIST:
        if rc != 0:
            return 1
    return 0;

# Hard strip: strip UnWantedchar
def HardStrip (string):
    return tsutils.hard_strip(string)

# return true if OS uses huge/big pages, false otherwise
def MemHugePages ():
    if not isWin():
        support = RunCmdGetOutput('cat /proc/meminfo')
        if (tsutils.grep(support,'HugePages_Free') + tsutils.grep(support,'BigPagesFree')):
            #check if there are huge pages
            num_of_pages = RunCmdGetOutput('cat /proc/meminfo  | grep HugePages_Total: | cut -f2 -d":"')
            num_of_pages = HardStrip(num_of_pages)
            if num_of_pages in ["0 kB","0"]:
                #There are 0 HUGE pages in this machine, a change in 'lilo.etc' is needed.                
                return False
            return True
    else:
        return False

# if processes run in parallel, this function waits for them and return exit satatus*
# otherwise, the function returns the exit status of the RCs list given
# *exit status: is 1 if at least one of the processes failed, zero otherwise
def WaitCheckResult(IsParallel,PIDsRCs):
    if IsParallel:
        return Wait4Proc(PIDsRCs)
    else:
        return CheckRCs(PIDsRCs)

# wait for the given proccess (by PIDs) and return 0 if all of them returned 0, 1 otherwise
def Wait4Proc(PIDs):
    exit_status = 0
    current_exit_status = 1
    for PID in PIDs:
        for iter in range(1,10):
            # baypass to "OSError: [Errno 10] No child processes"
            # retry waitpid 
            try:
                (id,current_exit_status) = os.waitpid(PID,0)
                break
            except Exception, e:
                if isLinuxORSolaris():
                    os.system("ps -ef | grep %d | grep -v grep" % PID)
                if isFreeBSD():
                    os.system("ps -x | grep %d | grep -v grep" % PID)
                print "Waitpid for PID = %s failed (%s), retry.." % (PID,str(e))

        if current_exit_status != 0:
            exit_status = 1
    return exit_status 

#  return the module extension
def ModuleExt():
    if tsutils.isLinux():
         rc = os.uname()[2].find("2.6")
         if (rc != -1):
             return "ko"
         else:
             return "o"
    else:
        return None # not relevant in Windows

# is linux?
def isLinux ():
    return tsutils.isLinux() 
# is FreeBSD?
def isFreeBSD ():
    return tsutils.isFreeBSD()
# is OpenSolaris?
def isOpenSolaris():
    return tsutils.isOpenSolaris()
# is Solaris?
def isSolaris():
    return tsutils.isSolaris()
# is SolarisBased
def isSolarisBased():
    return tsutils.isSolarisBased()
# is UNIXBASED?
def isUNIXBASED ():
    return tsutils.isUNIXBASED()
# is Linux or FreeBSD
def isLinuxORBSD():
    return tsutils.isLinuxORBSD()
# is Linux or Solaris
def isLinuxORSolaris():
    return tsutils.isLinuxORSolaris()
# is FreeBSD or Solaris
def isBSDORSolaris():
    return tsutils.isBSDORSolaris()
# is windows?
def isWin ():
    return tsutils.isWIN()
# is ESX?
def isESX():
    return tsutils.isESX()
# is gen2?
def isGEN2(stack_name):
    return tsutils.isGEN2(stack_name)

#is VMWARE
def isVMWARE(stack_name):
    return tsutils.isVMWARE(stack_name)
#is VMWARE_OFED
def isVMWARE_OFED(stack_name):
    return tsutils.isVMWARE_OFED(stack_name)
#is VMWARE_MTNIC
def isVMWARE_MTNIC(stack_name):
    return tsutils.isVMWARE_MTNIC(stack_name)


# return the IP of the machine
def MyIp():
    return tsutils.myip()   

# grep like in linux
def grep (page,string2grep):
    return tsutils.grep(page,string2grep)

# grep like in linux
def memory_size():
    return tsutils.memory_size()

def get_page_size():
    return tsutils.get_page_size()

def get_map_name(name):
    return tsutils.get_map_name(name)

def  str_to_list(str):
    return tsutils.str_to_list(str)

# Returns base 0 index of the IB port
def ib_port2idx(device, ib_port):
    # is4_X ib_ports idx are based 0, all other base 1
    return (int(ib_port) - int(device.lower().find("is4_") == -1))

# handle_read: this functions seeks for the handle number in the given file descriptor
def handle_read (FD):
    FD_lines = FD.readlines()
    for line in FD_lines:
        try:
            handle_string=line.split(" ")[0]
            equals_operator=line.split(" ")[1]
            handle_number=line.split(" ")[2]
        except:
            handle_string=""
            equals_operator=""
            handle_number=""

        if (handle_string == "Handle") & (equals_operator == "="):
            return handle_number
        else:
            return "handle not found!"
    return



# synchornize between 2 sides via file descriptors
def sync(label, timeout=None, data=None, print_debug=True):
    item_type = None
    key = 'sync_Ready'
    if data == None:
        item = '0'
        item_type = int
    else:
        if type(data) == int:
            item = str(data)
            item_type = int
        else: #str
            item = data
            item_type = str

    PutDataExchange([key],[item],label, print_debug)
    items = GetDataExchange([key],label,timeout, print_debug)
    #sync timeout
    if timeout != None and items == None:
        return -1

    #return sync value
    if items != None:
        if item_type == int:
            return int(items[0])
        else: #str
            return items[0]

    return 0

# send to partner the element with key,
# if there's an error, a msg is returned, otherwise.
def PutDataExchange(keylist, itemlist, prefix = "", print_debug=True):
    if os.environ.has_key('TS_RUNNER_INDEX'):
      fn = 'ts_DataExchange' + '_' + os.environ['TS_RUNNER_INDEX'] + "_" + prefix
    else:
      fn = 'ts_DataExchange' + "_" + prefix
    try:
        commdir  = os.environ['MT_COMMDIR']
        if print_debug:
            print "commdir=" + commdir
        mod_case = os.environ['MT_MODULE_CASE']
        if print_debug:
            print "mod_case=" + mod_case
        ips = os.environ['RHOST']
    except Exception, e:
        msg = "ERROR: PutDataExchange couldn't find the needed enviroment varibales! %s" % e
        test_exit(FAILED,msg)
        return 

    if (len(keylist) != len(itemlist)) or (len(keylist)==0) or (len(itemlist)==0):
        msg = "ERROR: PutDataExchange lists length is invalid."
        test_exit(FAILED,msg)
        return         
    
    # create and clear file    
    MyIp = mine(ips.split(';'))    
    DataPath = os.path.join(commdir,MyIp,fn)

    if (os.path.exists(os.path.join(commdir,MyIp)) != 1):
        test_exit(FAILED,"PutDataExchange:: path %s is not found!" % os.path.join(commdir,MyIp))

    ClearFile(DataPath)

    fd = open(DataPath,'w')
    for i in range(len(keylist)):
        fd.write(str(keylist[i])+': '+str(itemlist[i])+'\n')

    fd.write('TS_END'+prefix+': '+ mod_case+'\n')
    fd.flush()
    fd.close
    return



   
# given a list of keys, the responding items are returned in a list
def GetDataExchange (keylist,prefix='',timeout=None, print_debug=True):
    if os.environ.has_key('TS_RUNNER_INDEX'):
      fn = 'ts_DataExchange' + '_' + os.environ['TS_RUNNER_INDEX'] + "_" + prefix
    else:
      fn = 'ts_DataExchange' + "_" + prefix
    nap = 0.1

    try:
        commdir    = os.environ['MT_COMMDIR']
        mod_case   = os.environ['MT_MODULE_CASE']
        ips = os.environ['RHOST']
    except Exception, e:
        msg = "ERROR: GetDataExchange couldn't find the needed enviroment varibales! %s" % e        
        test_exit(FAILED,msg)
        return

    if (len(keylist)==0):
        msg = "ERROR: GetDataExchange key list length is invalid."
        test_exit(FAILED,msg)
        return

    partner_ip = NoMine(ips.split(";"))
    DataPath = os.path.join(commdir,partner_ip,fn)
    if os.environ.has_key('TS_RUNNER_INDEX'):
       hack_fn = os.path.join(os.path.dirname(DataPath),"nfs_hack" + '_' + os.environ['TS_RUNNER_INDEX'])
    else:
        hack_fn = os.path.join(os.path.dirname(DataPath),"nfs_hack")
    time_start = int(time.time())
    counter = 0

    while(True):
        # wait for file to be created
        while (exists(DataPath)!= 1):
            time.sleep(nap)
            counter += 1
            if (counter % 10) == 0:
                if print_debug:
                    print "%s Waiting for file %s" % (tsutils.strnow(),DataPath)

            delta_time = int(time.time()) - time_start
            if timeout != None:                
                if delta_time > timeout:
                    print "%s Timeout exceeded (%s sec)" % (tsutils.strnow(),timeout)
                    return None
            # hack for nfs problem
            # write another file to the same location to refrease nfs
            if (counter % 150) == 0:
                fd = open(hack_fn,'w')
                fd.write("NFS hack: write this file for refreshing the NFS\n")
                fd.close()
                if print_debug:
                    print "%s Write file %s for refreshing NFS\n" % (tsutils.strnow(),hack_fn)
                time.sleep(nap)
                try:
                    os.remove(hack_fn)
                except:
                    pass

        # check if this is the file you are waiting for
        #the file exists wait to write the file needed for hybrid regression (windows read file written by Linux)
        time.sleep(1)
        try: 
           fd = open(DataPath,'r')
        except:
           #try again 
           time.sleep(1)
           fd = open(DataPath,'r')
        lines = fd.readlines()
        if (lines != [] ) and (str(lines[-1]) in [('TS_END'+prefix+': '+ mod_case+'\n'),('TS_END'+prefix+': '+ mod_case+'\r\n')]):
            fd.close()
            break
        else:
            fd.close()
            time.sleep(nap)


    # parse the file
    itemlist = []
    for i in range(len(keylist)):
        found = False
        for j in range(len(lines)):
            line = lines[j].strip('\n').strip('\r')
            if (line.startswith(keylist[i]+":")):
                itemlist += [line.replace(keylist[i]+": ","")]                
                found = True
                break
        if not found:
            itemlist += [None]

    time.sleep(nap+1)
    DeleteFile(DataPath)
    return itemlist

# mine: returns you data from the given tuple
def mine(DataPair, IpPair=None):
    if IpPair==None:
        try:
            IpPair = os.environ['RHOST'].split(';')
        except:
            pass

    if (len(DataPair)!= 2) or (len(IpPair)!= 2):
        return None
    myip    = str(tsutils.myip())
    ip0     = str(IpPair[0])
    ip1     = str(IpPair[1])

    # Which IP is your partner IP              
    if (myip == ip0):
        return DataPair[0]
    elif (myip == ip1):
        return DataPair[1]
    else:
        test_exit(FAILED,"mine:: Your ip (" + myip + ") is not found in RHOST enviroment variable")

# return partner data from the given tuple
def NoMine (DataPair, IpPair=None):
    m = mine(DataPair, IpPair)
    if m==None: return None
    if m == DataPair[0]:
        return DataPair[1]
    else:
        return DataPair[0]

# sorts the given pair
def SortPair (pair):
    if len(pair) != 2:
        test_exit(FAILED,"SortPair: takes a pair list [x,y] (not %s)" % str(pair))
    p1 = pair[0]
    p2 = pair[1]
    try:
        ips = os.environ['RHOST'].split(';')
    except Exception, e:
        test_exit(FAILED,"SortPair: %s" %e)

    myip = str(tsutils.myip())    
    if len(ips)!=2:
        test_exit(FAILED,"SortPair: RHOST enviroment variable is invalid (%s)" % str(ips))

    if ips[0] == myip:
        return [p1,p2]
    elif ips[1] == myip:
        return [p2,p1]
    else:
        test_exit(FAILED,"SortPair: your ip cannot be found in RHOS enviroment variable (%s)" % str(ips))

############################################REMOVE WHEN FINISH############################################################################
# synchornize between many sides via file descriptors
def ClusterSync(label, timeout=None, data=None, print_debug=True):
    item_type = None
    key = 'sync_Ready'
    if data == None:
        item = '0'
        item_type = int
    else:
        item = str(data)

    if MyIp() ==  ClusterMaster():
       items_per_partners = ClusterMasterGetDataExchange([key],label,timeout, print_debug)
       if items_per_partners != None:
          for index in range(len(items_per_partners)):
              items_per_partners[index] = items_per_partners[index][0]
       ClusterMasterPutDataExchange([key],[[item] + items_per_partners] ,label, print_debug)
       items_per_partners = [item] + items_per_partners
       return items_per_partners
    else:
       ClusterPutDataExchange([key],[item],label, print_debug)
       items_per_partners = ClusterGetDataExchange([key],label,timeout, print_debug)
       
    #sync timeout
    if timeout != None and items_per_partners == None:
        return -1

    #return sync value
    if items_per_partners != None and (MyIp() in  ClusterSlaves()):
        for index in range(len(items_per_partners)): 
            items_per_partners[index] = items_per_partners[index][0]
        return eval(items_per_partners[0])

    return 0

# send to master the element with key,
# if there's an error, a msg is returned, otherwise.
def ClusterPutDataExchange(keylist, itemlist, prefix = "", print_debug=True):
    fn = 'ts_DataExchange' + "_" + prefix
    try:
        commdir  = os.environ['MT_COMMDIR']
        if print_debug:
            print "commdir=" + commdir
        mod_case = os.environ['MT_MODULE_CASE']
        if print_debug:
            print "mod_case=" + mod_case
        ips = os.environ['CLUSTER_RHOST']
    except Exception, e:
        msg = "ERROR: PutDataExchange couldn't find the needed enviroment varibales! %s" % e
        test_exit(FAILED,msg)
        return

    if (len(keylist) != len(itemlist)) or (len(keylist)==0) or (len(itemlist)==0):
        msg = "ERROR: PutDataExchange lists length is invalid."
        test_exit(FAILED,msg)
        return

    # create and clear file
    MyIp = ClusterMine(ips.split(';'))
    DataPath = os.path.join(commdir,MyIp,fn)

    if (os.path.exists(os.path.join(commdir,MyIp)) != 1):
        test_exit(FAILED,"PutDataExchange:: path %s is not found!" % os.path.join(commdir,MyIp))

    ClearFile(DataPath)

    fd = open(DataPath,'w')
    for i in range(len(keylist)):
        fd.write(str(keylist[i])+': '+str(itemlist[i])+'\n')

    fd.write('TS_END'+prefix+': '+ mod_case+'\n')
    fd.flush()
    fd.close
    return

# send to slaves the element with key,
# if there's an error, a msg is returned, otherwise.
def ClusterMasterPutDataExchange(keylist, itemlist, prefix = "", print_debug=True):
    slaves_ips = ClusterSlaves()
    
    fns = []
    for ip in slaves_ips:
        fns.append(ip + "_" + 'ts_DataExchange' + "_" + prefix)

    try:
        commdir  = os.environ['MT_COMMDIR']
        if print_debug:
            print "commdir=" + commdir
        mod_case = os.environ['MT_MODULE_CASE']
        if print_debug:
            print "mod_case=" + mod_case
        ips = os.environ['CLUSTER_RHOST']
    except Exception, e:
        msg = "ERROR: PutDataExchange couldn't find the needed enviroment varibales! %s" % e
        test_exit(FAILED,msg)
        return

    if (len(keylist) != len(itemlist)) or (len(keylist)==0) or (len(itemlist)==0):
        msg = "ERROR: PutDataExchange lists length is invalid."
        test_exit(FAILED,msg)
        return

    # create and clear file
    MyIp = ClusterMine(ips.split(';'))
    DataPaths = []
    for fn in fns: 
        DataPath = os.path.join(commdir,MyIp,fn)

        if (os.path.exists(os.path.join(commdir,MyIp)) != 1):
            test_exit(FAILED,"PutDataExchange:: path %s is not found!" % os.path.join(commdir,MyIp))

        ClearFile(DataPath)

        fd = open(DataPath,'w')
        for i in range(len(keylist)):
            fd.write(str(keylist[i])+': '+str(itemlist[i])+'\n')

        fd.write('TS_END'+prefix+': '+ mod_case+'\n')
        fd.flush()
        fd.close

    return

# given a list of keys, the responding items are returned in a list
def ClusterGetDataExchange (keylist,prefix='',timeout=None, print_debug=True):
    fn = MyIp() + "_" + 'ts_DataExchange' + "_" + prefix
    nap = 0.1

    try:
        commdir    = os.environ['MT_COMMDIR']
        mod_case   = os.environ['MT_MODULE_CASE']
        ips = os.environ['CLUSTER_RHOST']
    except Exception, e:
        msg = "ERROR: GetDataExchange couldn't find the needed enviroment varibales! %s" % e
        test_exit(FAILED,msg)
        return

    if (len(keylist)==0):
        msg = "ERROR: GetDataExchange key list length is invalid."
        test_exit(FAILED,msg)
        return

    partner_ip = ClusterMaster()
    DataPath = os.path.join(commdir,partner_ip,fn)
    hack_fn = os.path.join(os.path.dirname(DataPath),"nfs_hack")
    time_start = int(time.time())
    counter = 0

    while(True):
        # wait for file to be created
        while (exists(DataPath)!= 1):
            time.sleep(nap)
            counter += 1
            if (counter % 10) == 0:
                if print_debug:
                    print "%s Waiting for file %s" % (tsutils.strnow(),DataPath)

            delta_time = int(time.time()) - time_start
            if timeout != None:
                if delta_time > timeout:
                    print "%s Timeout exceeded (%s sec)" % (tsutils.strnow(),timeout)
                    return None
            # hack for nfs problem
            # write another file to the same location to refrease nfs
            if (counter % 150) == 0:
                try: 
                    fd = open(hack_fn,'w')
                    fd.write("NFS hack: write this file for refreshing the NFS\n")
                    fd.close()
                except:
                    pass  
                if print_debug:
                    print "%s Write file %s for refreshing NFS\n" % (tsutils.strnow(),hack_fn)
                time.sleep(nap)
                try:
                    os.remove(hack_fn)
                except:
                    pass

        # check if this is the file you are waiting for
        fd = open(DataPath,'r')
        lines = fd.readlines()
        if (lines != [] ) and (str(lines[-1]) == ('TS_END'+prefix+': '+ mod_case+'\n')):
            fd.close()
            break
        else:
            fd.close()
            time.sleep(nap)


    # parse the file
    itemlist = []
    for i in range(len(keylist)):
        found = False
        for j in range(len(lines)):
            line = lines[j][:-1]
            if (line.startswith(keylist[i]+":")):
                itemlist += [line.replace(keylist[i]+": ","")]
                found = True
                break
        if not found:
            itemlist += [None]

    time.sleep(nap+1)
    DeleteFile(DataPath)
    return [itemlist]

# given a list of keys, the responding items are returned in a list
def ClusterMasterGetDataExchange (keylist,prefix='',timeout=None, print_debug=True):

    partner_ip = ClusterSlaves()

    itemlists = []
    
    fn =  'ts_DataExchange' + "_" + prefix     
    nap = 0.1


    try:
        commdir    = os.environ['MT_COMMDIR']
        mod_case   = os.environ['MT_MODULE_CASE']
        ips = os.environ['CLUSTER_RHOST']
    except Exception, e:
        msg = "ERROR: GetDataExchange couldn't find the needed enviroment varibales! %s" % e
        test_exit(FAILED,msg)
        return

    if (len(keylist)==0):
        msg = "ERROR: GetDataExchange key list length is invalid."
        test_exit(FAILED,msg)
        return

    partners_ip = ClusterSlaves()
    for partner_ip in partners_ip:
        DataPath = os.path.join(commdir,partner_ip,fn) 
        hack_fn = os.path.join(os.path.dirname(DataPath),"nfs_hack")

        time_start = int(time.time())
        counter = 0

        while(True):
            # wait for file to be created
            while (exists(DataPath)!= 1):
                time.sleep(nap)
                counter += 1
                if (counter % 10) == 0:
                    if print_debug:
                        print "%s Waiting for file %s" % (tsutils.strnow(),DataPath)

                delta_time = int(time.time()) - time_start
                if timeout != None:
                    if delta_time > timeout:
                        print "%s Timeout exceeded (%s sec)" % (tsutils.strnow(),timeout)
                        return None
                # hack for nfs problem
                # write another file to the same location to refrease nfs
                if (counter % 150) == 0:
                    fd = open(hack_fn,'w')
                    fd.write("NFS hack: write this file for refreshing the NFS\n")
                    fd.close()
                    if print_debug:
                        print "%s Write file %s for refreshing NFS\n" % (tsutils.strnow(),hack_fn)
                    time.sleep(nap)
                    try:
                        os.remove(hack_fn)
                    except:
                        pass

            # check if this is the file you are waiting for
            fd = open(DataPath,'r')
            lines = fd.readlines()
            if (lines != [] ) and (str(lines[-1]) == ('TS_END'+prefix+': '+ mod_case+'\n')):
                fd.close()
                break
            else:
                fd.close()
                time.sleep(nap)


        # parse the file
        itemlist = []
        for i in range(len(keylist)):
            found = False
            for j in range(len(lines)):
                line = lines[j][:-1]
                if (line.startswith(keylist[i]+":")):
                    itemlist += [line.replace(keylist[i]+": ","")]
                    found = True
                    break
            if not found:
                itemlist += [None]

        time.sleep(nap+1)
        DeleteFile(DataPath)
        itemlists.append(itemlist)

    return itemlists

# mine: returns you data from the given tuple
def ClusterMine(DataList, IpList=None):
    if IpList==None:
        try:
            IpList = os.environ['CLUSTER_RHOST'].split(';')
        except:
            pass

    len_list = len(IpList)

    if (len(DataList) != len_list):
        return None
    myip    = str(tsutils.myip())
    master_ip     = str(IpList[0])
    slaves_ips     = IpList[1:]

    # Which IP is your partner IP
    if (myip == master_ip):
        return DataList[0]
    elif (myip in slaves_ips):
        return DataList[slaves_ips.index(myip)+1]
    else:
        test_exit(FAILED,"mine:: Your ip (" + myip + ") is not found in CLUSTER_RHOST enviroment variable")


# return partners data from the given tuple
def ClusterNoMine (DataList, IpList=None):
    m = ClusterMine(DataList, IpList)
    if m==None: return None
    if m == DataList[0]:
        return DataList[1:]
    else:
        return DataList.remove(m)

#get cluster master
def ClusterMaster():
    try:
      IpList = os.environ['CLUSTER_RHOST'].split(';')
      return IpList[0]
    except:
      test_exit(FAILED,"ClusterMaster:: Can't get the cluster master ip from CLUSTER_RHOST enviroment variable (" + os.environ['CLUSTER_RHOST'] + ") ")   

#get slaves ip list   
def ClusterSlaves():
    try:
      IpList = os.environ['CLUSTER_RHOST'].split(';')
      return IpList[1:]
    except:
      test_exit(FAILED,"ClusterMaster:: Can't get the cluster slaves ip list  from CLUSTER_RHOST enviroment variable (" + os.environ['CLUSTER_RHOST'] + ") ")





##############################################REMOVE WHEN FINISH###########################################################################
# return the IB interface (as function of a port)
def ULP_get_if(port):
    if port == '1':
        return "ib0"
    elif port == '2':
        return "ib1"
    else:
        test_exit(FAILED,"bad port number: " + port)


# get path for mpi exec files
def MpiGetPath(name,server=False):
    # daemon
    if (name == 'mpiexec') or (server == True):
        try:
            mpi_src_path = os.environ['MT_MPICH2']
	    mpi_path =  str(os.path.join(mpi_src_path,'bin',name+ ".exe"))
	except:
            mpi_src_path =  os.path.join(os.environ['HOMEDRIVE']+os.sep,
                "progra~1" + os.sep + "mellanox","mpich2win" + os.environ['PROCESSOR_ARCHITECTURE'][-2:])             
            mpi_src_path = mpi_src_path.replace('86','32')            
            mpi_path =  str(os.path.join(mpi_src_path,'bin',name+ ".exe"))
    # clSient
    else:
        mpi_path = os.path.join(".",str(get_PLATF()),name + ".exe")
    return mpi_path


# return the IP of a IPoIB interface (as function of the original host IP + port)
def ULP_get_ip(dev, port):
    if is_eth(dev, port):
        try:
            if os.environ.has_key('IF_IP'):
                if_ips = os.environ['IF_IP'].split(";")
                return mine(if_ips)

            dev_number = dev.split('eth')
            ib_number = 0
            if len(dev_number) > 1:
                ib_number = int(dev_number[1])
            ip = MyIp()
            return  str(int(ip.split(".")[0]) + ib_number) + "." + ".".join(ip.split(".")[1:])

        except Exception, e:
            test_exit(FAILED,"ULP_get_ip: Unable to define interface IP in Ethernet mode - (%s)" % str(e))

    stack_name = get_stack_name()
    if stack_name == None:
        test_exit(FAILED,"ULP_get_ip: stack_name undefined")

    ip = MyIp()
    port_num = 0
    devices = []
    if tsutils.isGEN2(stack_name):
        # read the IB device GID 0
        infiniband_gid_file = "/sys/class/infiniband/" + dev + "/ports/" + port + "/gids/0"

        if os.path.exists(infiniband_gid_file):
            try:
                fd = open(infiniband_gid_file, 'r')
                ib_gid = fd.read()
                fd.close()
                ib_gid = ib_gid.replace(':', '')
            except Exception, e:
                test_exit(FAILED,"ULP_get_ip: failed to open the file %s" % infiniband_gid_file)
        else:
            test_exit(FAILED,"ULP_get_ip: the gid file %s not found" % infiniband_gid_file)

        # read the MAC address of the network devices and compare it with the IB device GID
        netdev_dir = "/sys/class/net"
        if os.path.exists(netdev_dir):
            netdevs = os.listdir(netdev_dir)
            for dev in netdevs:
                dev_file = netdev_dir + "/" + dev + "/address"

                # check the address of the device only if it exists
                if os.path.exists(dev_file):
                    try:
                        fd = open(dev_file, 'r')
                        mac_addr = fd.read()
                        fd.close()
                        mac_addr = mac_addr.replace(':', '')
                    except Exception, e:
                        test_exit(FAILED,"ULP_get_ip: failed to open the file %s" % dev_file)

                    # if the MAC address is too short, we don't need it
                    if len(mac_addr) < 40:
                        continue
                    # delete the reserved byte + QP number from the MAC address
                    mac_addr = mac_addr[8:]
                    if ib_gid == mac_addr:
                        return ifconfig.get_ip_of_if(dev)
        else:
            test_exit(FAILED,"ULP_get_ip: netdev_dir %s not found" % netdev_dir)

    elif tsutils.isIBGD(stack_name):
        dev_found = False
        infinband_dir = "/proc/infiniband/core"
        if os.path.exists(infinband_dir):
            devices = os.listdir(infinband_dir)
            devices.sort()
            for devs in devices:
                dev_dir = infinband_dir+os.sep+devs+os.sep
                if os.path.exists(dev_dir+"info"):
                    # search for your device
                    fd = open(dev_dir+"info",'r')
                    info = fd.read()
                    fd.close()
                    #if it's my device stop accumulating ports
                    if info.find(dev) != -1:
                        dev_found = True
                        break
                    ports_dir = os.listdir(dev_dir)                    
                    for file in ports_dir:
                        if file.startswith("port"):
                            port_num += 1                   
            # if didn't find the device
            if not dev_found:
                test_exit(FAILED,"ULP_get_ip: dev %s not in host devices" % dev)
        else:
            test_exit(FAILED,"ULP_get_ip: infinband_dir %s not found" % infinband_dir)

    elif stack_name == "IBAL" or stack_name == "SHALDAG_MNG":
        # not support more than one device
        pass
    else:
        test_exit(FAILED,"ULP_get_ip: stack_name %s not supported" % stack_name)

    # Move is4 devices to work with port base index = 1
    port = str(int(port) + (dev.lower().find("is4_") != -1))

    if port == '1' or port == '2':
        return str(int(ip.split(".")[0]) + int(port) + port_num) + "." + ".".join(ip.split(".")[1:])
    else:
        test_exit(FAILED,"bad port number: " + port)

def ULP_get_dev_and_port(idx):
    port_num = 0
    devices = []

    infinband_dir = "/sys/class/infiniband"
    if os.path.exists(infinband_dir):
        devices = os.listdir(infinband_dir)
        devices.sort()
        for dev in devices:
            last_port_num = port_num 
            port_num += len(os.listdir(infinband_dir+os.sep+dev+os.sep+"ports"))
            if port_num >= idx:
                return [dev, idx-last_port_num]                   
    else:
        test_exit(FAILED,"ULP_get_dev_and_port: infinband_dir %s not found" % infinband_dir)

    return [None,None]

# set the environment variable to use SDP
def ULP_sdp_env_set():
    stack_name = get_stack_name()

    if tsutils.isLinux():
	# check if being executed in a 64 bit machine
	platform = tsutils.get_PLATF()
	is_64 = platform.count("64")

        # if driver is gen1 driver
        if (tsutils.isIBGD(stack_name)):
            os.putenv("LIBSDP_CONFIG_FILE", "/usr/local/ibgd/etc/libsdp.conf")
            if (is_64 != 0):
                os.putenv("LD_PRELOAD", "/usr/local/ibgd/lib64/libsdp.so")
            else:
                os.putenv("LD_PRELOAD", "/usr/local/ibgd/lib/libsdp.so")
        else:
            try:
            	os.putenv("LD_LIBRARY_PATH", "/usr/local/lib:/usr/local/lib64")
		os.putenv("LD_PRELOAD", "libsdp.so")
	    except:
	        test_exit(FAILED, "failed to load LIBSDP")
    elif tsutils.isWin():
        test_exit(FAILED, "windows SDP is not supported yet")
    else:
        test_exit(FAILED, "OS is not supported")

def copyExt(ext,src,dest):
    return tsutils.copyExt(ext,src,dest)


# get the path to the .config file by the test name, this function search for the path
# to the test by parsing the DB file
def getConfigPath (testNameWithSubPath, multiTest = 0):
        
    testNameWithSubPath = testNameWithSubPath.replace('/',os.sep).replace('\\',os.sep)
    dotConfig   = '.config'
    if multiTest:        
        dotConfig   = '.config_multi'
        #dotConfig   = '.config'
    
    fn = os.environ['MT_WORK_DIR'] + os.sep + testNameWithSubPath + os.sep +  dotConfig
    
    if ( fn == None ) or (not tsutils.fexists(fn)):
        msg =  "getConfigPath:: ERROR %s is not found for test %s" % (dotConfig,fn )
        test_exit(FAILED,msg)
    else:
        return fn

# get the path to the test bin file by the test name, this function search for the path
# to the test by parsing the DB file
def getExternProgPath(testNameWithSubPath, testName):

    # Init
    localPath = GetProgPath(testName)
    
    print "localPath=" + str(localPath)
    fn = os.environ['MT_WORK_DIR'] + os.sep + testNameWithSubPath + os.sep +  localPath

    if ( fn == None ) or (not tsutils.fexists(fn)):
        msg =  "getExternProgPath:: ERROR %s is not found for test %s" % ('exe file',fn )
        test_exit(FAILED,msg)
    else:
        return fn

# Turn off/on logical link
def setPort(action="down",mst_device=None,delay=0,timeout=10,port=1,block=1,print_debug=True):

    stack_name = get_stack_name()
    if tsutils.isVMWARE_OFED(stack_name) or tsutils.isVMWARE_MTNIC(stack_name):
       esx_ip = ""
       if_ips = None
       my_if_ip = ""
       cmd = "/mswg/projects/vmware_ofed/scripts"+os.sep+"vm_get_info.py " 
       if tsutils.isWIN():
          cmd = "m:\\projects\\vmware_ofed\\scripts"+os.sep+"vm_get_info.py "  
       if os.environ.has_key('IF_IP'):
          try:
             if_ips = os.environ['IF_IP'].split(";")
             my_if_ip = " -ifip " + mine(if_ips)
          except:
             my_if_ip = ""
       try:
          esx_ip = " -ip " + os.environ['ESX_IP']
       except:
          esx_ip = ""   
       cmd += str(my_if_ip)+str(esx_ip)+" -op esx_set_port -a \""+action+" -d "+str(delay)+" -t "+str(timeout)+"\""
    else:
        cmd = os.environ['TEST_SUITE_PATH']+os.sep+".."+os.sep+"bin"+os.sep+"set_port.py -a "+action+" -d "+str(delay)+" -t "+str(timeout)+" -p "+str(port)
        if not print_debug:
            cmd =  cmd + " --dont_print_debug"
        if mst_device != None:
            cmd = cmd + " -m "+mst_device
    if block != 1:
        if tsutils.isWIN():
            cmd = "start " + cmd
        elif tsutils.isLinux():
            cmd = cmd +" &"
    if print_debug:
        print "SetPort command = %s" % cmd
    return os.system(cmd)

def hca_fatal_event(mst_device=None,delay=0,block=1):
    if mst_device == None:
        print "Please provide mst device"
        return 1
    if tsutils.isLinux():
        mwrite = "/usr/mst/bin/mwrite"
    elif tsutils.isWIN():
        mwrite = "mwrite"

    cmd = ""
    if tsutils.isLinux():
        cmd += "("

    if delay != 0:
        if tsutils.isWIN():
            #emulate sleep on windows
            cmd += "ping -n " + str(delay) + " 127.0.0.1>nul & "
        elif tsutils.isLinux():
            cmd += "sleep " + str(delay) + " ; "

    cmd += mwrite + " " + mst_device 
    if mst_device.find('23108')!=-1 or mst_device.find('25208')!=-1 or mst_device.find('25218')!=-1:
        cmd += " 0x40188 0x00000002"
    elif mst_device.find('25204')!=-1:
        cmd += " 0x12108 0x00000002"
    elif mst_device.find('25408')!=-1 or mst_device.find('25418')!=-1 or mst_device.find('25428')!=-1:
        cmd += " 0x1C188 0x00000001"
    else:
        print "Unsupported MST device " + mst_device
        return 1

    if tsutils.isLinux():
        cmd += ")"

    if block != 1:
        if tsutils.isWIN():
            cmd = "start " + cmd
        elif tsutils.isLinux():
            cmd = cmd +" &"

    print "hca_fatal_event command = %s" % cmd
    return os.system(cmd)



# Check if file exist /don't use cache like os.path.exists and detect created file immediately
def exists(file):
    return tsutils.exists(file)

def num_cpus():
    return tsutils.num_cpus()

def driver_stop(params=""):
    rc = 0
    stack = get_stack_name()

    if stack == None:
        print "Please provide stack name ( MT_STACK_NAME )"
        return 1
    print "Stopping driver for stack %s" % stack

    if stack == 'VPI_ETH'  or stack == 'VPI_IB' or stack == 'VPI_ETH_OFED' or stack == 'VPI_IB_OFED': # this case must be first, don't change order
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/mp_tmp stop"
    elif  stack == 'OFED_1_4' or stack == 'OFA_1_4' or stack == 'OFED_1_5': # don't change order # same script for OFED_1_4 and OFED_1_5
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/vpi_1_4 stop"
    elif  stack == 'MLNX_EN':
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/mlnx_en stop"
    elif  stack == 'DOLEV_VNIC':
        #driver_stop = "echo 'No driver stop!!!'"
        driver_stop = "/mswg/projects/test_suite2/shlib/lib/bx_host stop"
    elif  stack == 'LLE':
        driver_stop = "/mswg/projects/test_suite2/shlib/lib/vpi_1_4_iboe stop"
    elif tsutils.isGEN2(stack) or tsutils.isIBGD(stack) or stack == 'SHALDAG_MNG':
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/ibgd.sh stop"
    elif stack == "VAPI":
        rc = opensm.kill()
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/vapi stop"
    elif stack == "IBAL":
        rc = opensm.kill()
        rc = rc or win_ibadm.services_stop()
        driver_stop = "m:\\projects\\test_suite2\\shlib\\lib\\ibal.py stop"
    elif stack == "WIN_NIC":
	driver_stop = "m:\\projects\\test_suite2\\shlib\\lib\\win_nic.py stop"
    elif stack in ["WIN_VPI_ETH", "WIN_VPI_ETH_HYPERV"]:
        driver_stop = "m:\\projects\\test_suite2\\shlib\\lib\\win_nic.py stop"
    elif stack == "MTNIC":
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/mtnic stop"
    elif stack == "MTNIC_BSD":
        driver_stop = FILER + "/projects/test_suite2/shlib/lib/mtnic_bsd stop"
    else: #WIN_VAPI or WIN_VMWARE or WIN_NIC
        print "Driver stop not supported on %s!." % stack
        return rc

    #override driver stop
    if os.environ.has_key('DRIVER_STOP'):
        driver_stop = os.environ['DRIVER_STOP']

    if params != "":
        params = " " + params    
    print "-- executing :- "  + driver_stop + params
    rc = rc or os.system(driver_stop + params)
    if rc:
        print "Driver stop FAILED"
        
    return rc


def driver_start(params = "", ifs = ""):
    rc = 0

    stack = get_stack_name()

    if stack == None:
        print "Please provide stack name ( MT_STACK_NAME )"
        return 1
    print "Starting driver for stack %s" % stack

    if stack == 'VPI_ETH'  or stack == 'VPI_ETH_OFED' or stack == 'VPI_IB' or stack == 'VPI_IB_OFED': # Don't change cases order (those stacks are also GEN2)
        driver_start = FILER + "/projects/test_suite2/shlib/lib/mp_tmp start"
    # For OFED_1_4 and OFED_1_5 same driver start script used
    elif stack == 'OFED_1_4' or stack == 'OFA_1_4' or stack == 'MLNX_OFED' or stack == 'OFED_1_5': # Don't change cases order (those stacks are also GEN2)
        driver_start = FILER + "/projects/test_suite2/shlib/lib/vpi_1_4 start"
    elif  stack == 'MLNX_EN':
        driver_start = FILER + "/projects/test_suite2/shlib/lib/mlnx_en start"
    elif  stack == 'DOLEV_VNIC':
        #driver_start = "echo 'No driver start!!!'"
        driver_start = "/mswg/projects/test_suite2/shlib/lib/bx_host start"
    elif  stack == 'LLE':
        driver_start = "/mswg/projects/test_suite2/shlib/lib/vpi_1_4_iboe start"
    elif tsutils.isGEN2(stack) or tsutils.isIBGD(stack) or stack == 'SHALDAG_MNG':
        driver_start = FILER + "/projects/test_suite2/shlib/lib/ibgd.sh start"
    elif stack == "VAPI":
        driver_start = FILER + "/projects/test_suite2/shlib/lib/vapi start"
    elif stack == "IBAL":
        driver_start = "m:\\projects\\test_suite2\\shlib\\lib\\ibal.py start"
    elif stack == "WIN_NIC":
	driver_start = "m:\\projects\\test_suite2\\shlib\\lib\\win_nic.py start"
    elif stack in  ["WIN_VPI_ETH", "WIN_VPI_ETH_HYPERV"]:
        driver_start = "m:\\projects\\test_suite2\\shlib\\lib\\win_nic.py start"
    elif stack == "MTNIC":
        driver_start = FILER + "/projects/test_suite2/shlib/lib/mtnic start"
    elif stack == "MTNIC_BSD":
        driver_start = FILER + "/projects/test_suite2/shlib/lib/mtnic_bsd start"
    else: #WIN_VAPI or WIN_VMWARE or WIN_NIC
        print "Driver start not supported on %s!." % stack
        return rc
    #override driver start
    if os.environ.has_key('DRIVER_START'):
        driver_start = os.environ['DRIVER_START']
    if params != "":
        params = " " + params
    if ifs != "":
        ifs = " " + ifs
    elif os.environ.has_key('MT_IFS_CONF'):
        ifs = " " + os.environ['MT_IFS_CONF']
    print "-- executing :- "  + driver_start + params + ifs
    rc = rc or os.system(driver_start + params + ifs)
    if rc:
        print "Driver start FAILED"

    if tsutils.isGEN2(stack) or tsutils.isIBGD(stack) or stack == "VAPI":
        mellanox_ip_prefix = "10"
        ib0_ip = ifconfig.get_ip_of_if('ib0')
        ib1_ip = ifconfig.get_ip_of_if('ib1')
        # hack for problem in suse10
        if ib0_ip == ib1_ip and ib1_ip != '':
            ifconfig.set_ip_of_if('ib0',"11"+MyIp()[MyIp().find('.'):])
            ifconfig.set_ip_of_if('ib1',"12"+MyIp()[MyIp().find('.'):])
    return rc


def driver_restart(params=""):
    rc = 0
    rc = driver_stop(params)
    rc = rc or driver_start(params)

    if rc:
        print "Driver restart FAILED"
    return rc

# make a best effort to find the bath of IB Tools .
def get_mlx_IB_tools_dir():
    path = os.environ['HOMEDRIVE']+os.sep+"progra~1"+os.sep+"Mellanox"+os.sep+"MLNX_WinOF"+os.sep
    if not os.path.exists(path) :
        print "path not found :"+path
        path = os.environ['HOMEDRIVE']+os.sep+"progra~1"+os.sep+"Mellanox"+os.sep+"MLNX_VPI"+os.sep+"IB"+os.sep
        if not os.path.exists(path) :
            print "path not found :"+path
            print "Failed To find IB Tools Dir"
            path = ''
    if path != '' : 
        print "IB Tools Path Found:"+path
    return path

def ndi(cmd):
    rc = 0
    if tsutils.isWIN():
        try:
            cmd_prefix = os.environ['MT_IPOIB']+os.sep
            if not os.path.exists(cmd_prefix) : 
                print "ERROR : [MT_IPOIB]=%s env var is wrong ... please fix it ." % cmd_prefix
                raise 
        except:
            cmd_prefix = get_mlx_IB_tools_dir()+"ipoib"+os.sep
        if cmd == 'install':
            cmd = cmd_prefix + "ndinstall.exe -i"
            rc = os.system(cmd)
            print "%s (rc = %d)" % (cmd,rc)
        elif cmd == 'uninstall':
            cmd = cmd_prefix + "ndinstall.exe -r"
            rc = os.system(cmd)                            
            print "%s (rc = %d)" % (cmd,rc)
        else:
            print "wrong command!"
            rc = 1
    else:
        # Not supported on Linux
        rc = 1
    return rc


def wsd(cmd):
    rc = 0
    if tsutils.isWIN():
        try:
            cmd_prefix = os.environ['MT_IPOIB'] + os.sep
            if not os.path.exists(cmd_prefix) : 
                print "ERROR : [MT_IPOIB]=%s env var is wrong ... please fix it ." % cmd_prefix
                raise 
        except:
            cmd_prefix = get_mlx_IB_tools_dir()+"ipoib"+os.sep
        if cmd == 'install':
            cmd = cmd_prefix + "installsp.exe -i"
            rc = os.system(cmd)
            print "%s (rc = %d)" % (cmd,rc)
        elif cmd == 'uninstall':
            cmd = cmd_prefix + "installsp.exe -r"
            rc = os.system(cmd)                            
            print "%s (rc = %d)" % (cmd,rc)
        else:
            print "wrong command!"
            rc = 1
    else:
        # Not supported on Linux
        rc = 1
    return rc


def sdp(cmd):
    rc = 0
    if tsutils.isWIN():
        try:
            mlx_dir_path = get_mlx_IB_tools_dir()
            cmd_prefix = mlx_dir_path+"SDP"+os.sep 
        except:
            cmd_prefix = None
	
	print cmd_prefix
	
	if cmd_prefix == None:
	    print "could not find dir"
	    return 1 
        if cmd == 'install' and os.path.exists(cmd_prefix):
            rc = os.system("net start sdp")
            if rc:
                print "-E- SDP module didn't load properly "
                return 1
            cmd = cmd_prefix + "InstallSdpProvider.exe -i"
            rc = os.system(cmd)
            print "%s (rc = %d)" % (cmd,rc)
            if rc:
                print "-E- SDP install provider failed"
                return 1

        elif cmd == 'uninstall' and os.path.exists(cmd_prefix):
            cmd = cmd_prefix + "InstallSdpProvider.exe -r"
            rc = os.system(cmd)
            print "%s (rc = %d)" % (cmd,rc)
            rc = rc or os.system("net stop sdp")
            if rc:
                print "-E- SDP module didn't unload properly "
                return 1
        else:
            print "wrong command!!!!!!"
            rc = 1
    else:
        # Not supported on Linux
        rc = 1
    return rc


PERF_MPI_DB_PATH = FILER + "/mpi_db/"
def perf_add_data_to_db(logfile, cmd_flags, cmd_nodeinfo_db, cmd_perfinfo_db):
	import pwd

	PERF_TMP_DIR4LOGS = FILER + "/tmp/"
	PERF_DB_HOST = "mtlsws01"
	HOST_LOG = "./HOST_"+MyIp()+".log"
	HOST_INFO_CMD  = PERF_MPI_DB_PATH + '/scripts/gethostinfo > ' + HOST_LOG

	# initialize this variable with 0
	result = 0
	# dump the host info to a file
	print "HOST_INFO_CMD = '%s'" % HOST_INFO_CMD
	result = result or os.system(HOST_INFO_CMD)
	result = result or os.system("echo `date` >> "+HOST_LOG)

	if result != 0:
		print "Error, failed to collect system info details\n"
		return result

	# copy the log files (host info + results) to selected place
	for fname in [HOST_LOG, logfile]:
		cmd = "cp "+ fname + " " + PERF_TMP_DIR4LOGS
		print "copy log cmd: %s" % cmd
		result = result or os.system(cmd)

	if result != 0:
		print "Error, failed to copy files to %s\n" % PERF_TMP_DIR4LOGS
		return result
	# fork, in order to insert the data as herod
	ppid = os.fork()
	if ppid:
		# code of parent process

		# wait for the child process
		print "Parent process is waiting for ppid=%s" % ppid
		get_ppid, child_status = os.waitpid(ppid, 0)
		result = 0
		print "Child (%d) was ended with status=%s" % (get_ppid, child_status)
		if child_status != 0:
			result = 1

		# delete all the log files
		try:
			os.remove(logfile)
			os.remove(PERF_TMP_DIR4LOGS+os.sep+logfile)
			os.remove(HOST_LOG)
			os.remove(PERF_TMP_DIR4LOGS+os.sep+HOST_LOG)
			print "log files were removed"
		except:
			pass

		return result
	else:
		# code of child process
		result = 0

		print "Child process is changing user name to herod"

		try:
			herod_id = pwd.getpwnam('herod')[2]
			os.setuid(herod_id)
		except Exception ,e:
			result = 1
			print "---- ERROR ---- switch user to herod failed ! (%s)" % str(e)

		if result == 0:
			INSERT2DB_CMD = "perfbase input -u " + cmd_flags + " -d "+ PERF_MPI_DB_PATH +"/utility/" + cmd_nodeinfo_db + " "+PERF_TMP_DIR4LOGS+os.sep+HOST_LOG+" -d  "+ PERF_MPI_DB_PATH +"/utility/" + cmd_perfinfo_db + " "+ PERF_TMP_DIR4LOGS+os.sep+logfile
			result = result or os.system("rsh " + PERF_DB_HOST + " " + INSERT2DB_CMD)

		print "Adding performance numbers to DB was ended with status: %u\n" % result

		sys.exit(result)



def set_ipv6_addr(if_name, dev_name = None, ib_port = None):
	ipv6_ip = ifconfig.get_ip6_of_if(if_name)
	if ipv6_ip == "" or ipv6_ip == "unknown":
		try:
			if isLinux():
				if dev_name != None and ib_port != None:
					# ipv6 addr not configured - configure it with the gid value
					gids = VstatGetAttr(dev_name,"GID[  0]")
					if gids != []:
						ipv6_ip = gids[int(ib_port)-1]
				if ipv6_ip == "":
					hw_addr = ifconfig.get_hw_addr(if_name)
					ipv6_ip = "fe80::" + hw_addr
	
				print "configuring %s with ip %s" % (if_name, ipv6_ip)
				if ifconfig.set_ip6_of_if(if_name, ipv6_ip+"/64"):
					print "1) Failed to configure %s ipv6 ip" % if_name
					return 1
				if ifconfig.get_ip6_of_if(if_name) == "":
					print "2) Failed to configure %s ipv6 ip" % if_name
					return 2
				# On RHAS4 - After configuring the IPv6 addr, it becomes active only after 2 sec
				time.sleep(2.5)
			elif isFreeBSD():
				if ipv6_ip == "" or ipv6_ip == "unknown":
					hw_addr = ifconfig.get_hw_addr(if_name)
					ipv6_ip = "fe80::" + hw_addr
				print "configuring %s with ip %s%%%s" % (if_name, ipv6_ip,if_name)
				if ifconfig.set_ip6_of_if(if_name, ipv6_ip+"%"+if_name):
					print "1) Failed to configure %s ipv6 ip" % if_name
					return 1
				if ifconfig.get_ip6_of_if(if_name) == "":
					print "2) Failed to configure %s ipv6 ip" % if_name
					return 2
				# On RHAS4 - After configuring the IPv6 addr, it becomes active only after 2 sec
				time.sleep(2.5)  
			elif isWin():
				if not ifconfig.is_ipv6_installed(if_name):
					if ifconfig.install_ipv6():
						print "1) Failed to install IPv6 for interface %s" % if_name
						return 1
					time.sleep(5)
				if ifconfig.get_ip6_of_if(if_name) == "unknown":
					print "2) Failed to configure %s ipv6 ip" % if_name
					return 2
			else:
				print "Unknown OS"
				return 3
		except:
			return 4

	return 0


#### returns true if dev is an ib device
#### if dev = None, returns true if the regression mode is IB
def is_ib (dev = None ,port=1):
    return tsutils.is_ib(dev, port)

#### returns true if dev is an eth device
#### if dev = None, returns true if the regression mode is ETH
def is_eth (dev = None, port=0):
    return tsutils.is_eth(dev)

#### returns the regression mode 
#### input: see tsutils.get_mode()
def get_mode (*params):
    #length = len(params):
    return tsutils.get_mode(*params)

def part_id(dev_name):
    value = None
    try:
        mst_dev = MstDev(dev_name)
        if mst_dev != None:
            value = mst_dev.split("/")[3].split("_")[0].replace("mt","")
    except Exception, e:
        print "EXCEPTION: cannot find part number in mst_device %s - (%s)" % (dev_name,str(e))
    return value

# compares two linux kernel versions ver1 and ver2.  It returns an integer less than, equal to, or greater
# than zero if ver1 is found, respectively, to be less than, to match, or be greater than ver2.
def cmp_linux_kernel_ver(ver1, ver2):
    ver1_s = ver1.split('.')
    ver2_s = ver2.split('.')

    for idx in range(0, 3):
        if idx < 2:
            num1 = int(ver1_s[idx])
            num2 = int(ver2_s[idx])
        else:
            tmp1 = ver1_s[idx]
            tmp2 = ver2_s[idx]

            for delm in ['.', '_', '-']:
                 tmp1 = tmp1.split(delm)[0]
                 tmp2 = tmp2.split(delm)[0]

            num1 = int(tmp1)
            num2 = int(tmp2)

        if num1 > num2:
            return idx
        if num1 < num2:
            return -idx

    return 0


# main, for testing (IGNORE)
if __name__ == '__main__':
    #CaptureOutput("txt.txt")
    #print "main was called"
    #ff = open("ttt.tt",'w')
    #MySpawn(os.P_NOWAIT,['hello.py','23','33'],child_stdout=ff)
    #RestoreOutput()
    #print "printing the file"
    #PrintFile("txt.txt")
    #ClearFile("txt.txt")
    #TMPFILE = os.tempnam()
    #TempFileDescriptor('ccc','c')
    #list = grep(os.popen("dir").read(),"DIR")
    #print "grep:" + str(list)
    #str2 =List2String(['s','rtr'])

    #attr="hw_ver"
    #attr="PSID"
    #strr = VstatGetAttr("InfiniHost0",attr)
    #print attr +" = " +strr[0]

     #rc = VstatGetAttr('InfiniHost0','Error')
     #sync('t1')
     #mst = MstDev('InfiniHost0')
     #print "mst = " + str(mst)
     #attr = 'GUID'
     #rc = GetLid("InfiniHost0",1)
     #print "rc=%s."% str(rc)
     #myg = MyGrep(None, 'Handle',1,"Handle = 12\n  ")
     #print "myg=%s."% myg
     #rc = MemHugePages()
     #print "rc=%d."% rc
     os.environ['MT_WORK_DIR'] = "c:\\tmp\\tsscr\\"
#test = '\\ulp_tests\\win_alts'
#    t= "win_alts_exe"

     rc = MyIp()
     print "my ip rc=%s."% str(rc)

#     rc = getConfigPath(test)
#    print "getConfigPath rc=%s."% str(rc)


     sys.exit(0)


def doberman_ports_mapping(port_num):

    stack = get_stack_name()
    
    if not isLinux() or not stack in ['DOLEV_MNG_IB', 'DOLEV_MNG_ETH']:
        print "Supported only for Dolev"
        return None

    # this mapping is based on the file:
    # /advg/dolev_bringup/doberman_dolev_mapping.txt
    #
    # the following dictionary mapping format is:
    # SILK_port : (slice = '0'|'1', network_direction = 'internal'|'external', HW_port = '0'|'1'|'2'|'3')
    ports_mapping = {

          # Dolev 1
          '0xa22' : ('0','internal','0'), '0xa21' : ('0','internal','1'), '0xa20' : ('0','internal','2'),  # slice 0, internal port
          '0xa10' : ('0','external','0'), '0xa12' : ('0','external','1'), '0xa11' : ('0','external','2'), '0xa13' : ('0','external','3'),  # slice 0, external port
          '0xb20' : ('1','internal','0'), '0xb21' : ('1','internal','1'), '0xb22' : ('1','internal','2'),    # slice 1, internal port
          '0xb13' : ('1','external','0'), '0xb12' : ('1','external','1'), '0xb11' : ('1','external','2'), '0xb10' : ('1','external','3'),  # slice 1, external port

          # Dolev 2
          '0xd20' : ('0','internal','0'), '0xd21' : ('0','internal','1'), '0xd22' : ('0','internal','2'),    # slice 0, internal port
          '0xd11' : ('0','external','0'), '0xd13' : ('0','external','1'), '0xd10' : ('0','external','2'), '0xd12' : ('0','external','3'),  # slice 0, external port
          '0xc22' : ('1','internal','0'), '0xc21' : ('1','internal','1'), '0xc20' : ('1','internal','2'),    # slice 1, internal port
          '0xc12' : ('1','external','0'), '0xc10' : ('1','external','1'), '0xc13' : ('1','external','2'), '0xc11' : ('1','external','3')   # slice 1, external port
    }

    return ports_mapping.get(port_num,None)


##########################################################################
# Function :get_compilation_path
##########################################################################
def get_compilation_path ():
    comp_path = ""

    if not isWin():
        return comp_path
    try:
        platf = os.environ['PROCESSOR_ARCHITEW6432']
    except:
        try:
            platf = os.environ['PROCESSOR_ARCHITECTURE']
        except:
            vl.DATA_ERR("Failed to environ of PROCESSOR_ARCHITEW6432 & PROCESSOR_ARCHITECTURE")
            return comp_path

    if platf.count('64') > 0:
        plat = "amd64"
    else:
        plat = "i386"

    try:
        ddk_os = os.environ['BUILD_ALT_DIR'].lower()
    except:
        ddk_os = "chk_wnet_x86"		#default
    ddk_os = "obj" + ddk_os

    comp_path = ddk_os + os.sep + plat
    return comp_path


##########################################################################
# Function :get_osname
##########################################################################
def get_osname():
    if isWin():
        osname = None
        try:
            fd = os.popen('gettype')
            lines = fd.readlines()
            rc = fd.close()
        except:
            lines = []

        for line in lines:
            llow = line.lower()
            if llow.find("name:") == 0:
                if llow.find('windows xp') != -1:
                    osname = "XP"
                if llow.find('windows server 2003') != -1:
                    osname = "2003Server"
                if llow.find('windows server 2008') != -1:
                    osname = "2008Server"

        if osname == None:
            #try with systeminfo
            try:
                fd = os.popen('systeminfo')
                lines = fd.readlines()
                rc = fd.close()
            except:
                vl.EXCEPTION("Failed to get osname")
                return osname

            for line in lines:
                llow = line.lower()
                if llow.find("os name:") == 0:
                    if llow.find('windows xp') != -1:
                        osname = "XP"
                    if llow.find('windows server 2003') != -1:
                        osname = "2003Server"
                    if llow.find('2008') != -1:
                        osname = "2008Server"

            if osname == None:
                vl.DATA_ERR("Failed to get osname")
                return osname

        if os.environ.has_key('PROCESSOR_ARCHITEW6432'):
            osname += "64"
        else:
            osname += "32"
    else: # Linux
        osname = None # Not implemented yet

    return osname


##################################################################
# Function: run_command
# return value: (0, output) - success, (1, output) - failed
##################################################################
def run_command (cmd, print_output_if_fail = True):
	vl.MISC_TRACE1("starting run_command %s" % (str(cmd)))

	try:
		fd = os.popen(cmd)
		output = fd.read()
		rc = fd.close()
	except Exception, e:
		vl.EXCEPTION("run_command Failed (%s), cmd %s" % (str(e), str(cmd)))
		return (1, None)

	if rc and print_output_if_fail:
		vl.MISC_ERR("Failed to run %s" % cmd)
		vl.MISC_ERR("%s Command output %s\n" % ("^" * 10, "^" * 10))
		vl.MISC_ERR(str(output))
		vl.MISC_ERR("rc = %s" % str(rc))
		vl.MISC_ERR("%s" % ("^" * 36))

	if (rc != None):
		rc = 1
	else:
		rc = 0

	return (rc, output)


##################################################################
# Function: get_compatible_command
#       Return the compatible command for windows according to 
#       it's OS (32\64 Bit).
# return value: string command - success, None - failed
##################################################################
def get_compatible_command():
	vl.MISC_TRACE1("starting get_compatible_command")

	cmd = None

	curr_os = get_osname()
	vl.DATA_TRACE1("curr_os " + curr_os)
	if curr_os == None:
		vl.DATA_TRACE("This function is supported only in Windows")
		return None

	if curr_os.find("64") != -1:
		try:
			cmd_path = [os.environ['TEST_SUITE_PATH'] + os.sep + '..\\WinTools\\cmd64\\'][0]
		except Exception, e:
			vl.EXCEPTION("TEST_SUITE_PATH isn't exist (%s)" % str(e))
			return None
		vl.DATA_TRACE1("cmd_path " + str(cmd_path))
		cmd = str(cmd_path) + "cmd64.exe /C "
	else:
		try:
			cmd_path = [os.environ['WINDIR'] + os.sep + '..\\System32\\']
		except Exception, e:
			vl.EXCEPTION("TEST_SUITE_PATH isn't exist (%s)" % str(e))
			return None
		cmd = cmd_path + "cmd.exe /C "

	vl.MISC_TRACE1("return value: cmd " + str(cmd))
	return cmd


####################################Topology Class########################################
# Topology class used for cluster regression                                             #
##########################################################################################
class Topology:
   def __init__(self, topologyfn=None):
      if not topologyfn:
         #get topology file from commdir
         if os.environ.has_key('MT_COMMDIR'):
            topologyfn = os.path.join(os.environ['MT_COMMDIR'],MyIp(),'topology.py') 
            if os.path.exists(topologyfn):
               self.topology = tsutils.eval_file(topologyfn)
            else:
               msg = "can't find Topology file %s" % topologyfn
               print msg
               test_exit(FAILED,msg)  
         else: 
            msg = "COMMDIR not set ->can't find Topology file"
            print msg
            test_exit(FAILED,msg)       

   def MyHCAsPorts(self):    
        myip = MyIp()
        HCAs = []
        for netcomp in self.topology['netcomp'].keys():
            if myip == self.topology['netcomp'][netcomp]['ip']:
               for port in self.topology['netcomp'][netcomp]['ports'].keys():
                   HCAs.append((self.topology['netcomp'][netcomp]['ports'][port]['dev'],self.topology['netcomp'][netcomp]['ports'][port]['num']))
        return HCAs  
            


 
