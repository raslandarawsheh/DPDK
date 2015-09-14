#!/usr/bin/python
import os
import sys
import time
import subprocess

if len(sys.argv) != 2:
    print "The script takes the mlx_version.tar.gz"
    exit(0)

log_file = open('compile_log.log','w')
compile_flag = 0
x = sys.argv[1].split('.tar')[0]
print "aaaaaaaaaaaaaa",x
time.sleep(20)
os.system('tar xvf %s' %sys.argv[1])
print 'tar xvf %s' %sys.argv[1]

os.system('cd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc ' %x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc ' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s ====>>> Pass"%x)
	print "paaaaassssssssssss"
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system('cp -rf %s %s.recvinline' %(x,x))

os.system('cd %s.recvinline/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -r'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -r' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.recvinline/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.recvinline ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.recvinline ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.recvinline.debug' %(x,x))

os.system('cd %s.recvinline.debug/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -r -d'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -r -d' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.recvinline.debug/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.recvinline.debug ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.recvinline.debug ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")


os.system(' cp -rf %s %s.mtuset' %(x,x))

os.system('cd %s.mtuset/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.mtuset/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
	log_file.write("%s.mtuset ====>>> Pass"%x)
	compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.checksum'%(x,x))

os.system('cd %s.checksum/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c' %x)

#time.sleep(20)
process  = subprocess.Popen('cd %s.checksum/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.checksum ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.checksum ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.debug'%(x,x))

os.system('cd %s.debug/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -d'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -d' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.debug/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.debug ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.debug ====>>> Fail")
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.checksum.debug'%(x,x))

os.system('cd %s.checksum.debug/ ;./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c -d'%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c -d' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.checksum.debug/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.checksum.debug ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.checksum.debug ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.mtuset.checksum'%(x,x))

os.system('cd %s.mtuset.checksum/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -c' %x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -c' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.mtuset.checksum/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.checksum ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.checksum ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.mtuset.checksum.debug'%(x,x))

os.system('cd %s.mtuset.checksum.debug/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d -c '%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d -c' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.mtuset.checksum.debug/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.checksum.debug ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.checksum.debug ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")

os.system(' cp -rf %s %s.mtuset.debug'%(x,x))

os.system('cd %s.mtuset.debug/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d '%x)
os.system("pwd >> compile_log.log")
log_file.write('\ncd %s/ ; ./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d' %x)
#time.sleep(20)
process  = subprocess.Popen('cd %s.mtuset.debug/ ; find . -name *.so'%x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("\n*******************************************************************************************\n")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.debug ====>>> Pass"%x)
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.debug ====>>> Fail"%x)
log_file.write("\n*******************************************************************************************\n")


