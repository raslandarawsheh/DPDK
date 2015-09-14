#!/usr/bin/python
import os
import sys
import time
import subprocess

log_file = open('compile_log.log','w')
compile_flag = 0
x = sys.argv[1].split('.tar')[0]
os.system('tar xvf /download/%s' %sys.argv[1])
time.sleep(5)

os.system('/download/%s/compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m' %x)
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')


os.system('cp -rf /download/%s /download/%s.mtuset' %(x,x))

os.system('cd /download/%s.mtuset' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
	log_file.write("%s.mtuset ====>>> Pass")
	compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.checksum'%(x,x))

os.system('cd %s.checksum' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.checksum ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.checksum ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.debug'%(x,x))

os.system('cd %s.debug' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -d')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.debug ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.debug ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.checksum.debug'%(x,x))

os.system('cd %s.checksum.debug' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -c -d')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.checksum.debug ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.checksum.debug ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.mtuset.checksum'%(x,x))

os.system('cd %s.mtuset.checksum' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -c')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.checksum ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.checksum ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.mtuset.checksum.debug'%(x,x))

os.system('cd %s.mtuset.checksum.debug' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d -c ')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.checksum.debug ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.checksum.debug ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

os.system('cp -rf %s %s.mtuset.debug'%(x,x))

os.system('cd %s.mtuset.debug' %(x))
os.system('./compile_mlx4_pmd.sh -s /download/dpdk-1.8.0 -t x86_64-native-linuxapp-gcc -m -d ')
time.sleep(20)
process  = subprocess.Popen('find . -name *.so', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out = process.stdout.read()
err = process.stderr.read()
out_lines =  out.split('\n')

log_file.write("*******************************************************************************************")
for i in range (len(out_lines)):
    if 'librte_pmd_mlx4.so' in out_lines[i]:
        log_file.write("%s.mtuset.debug ====>>> Pass")
        compile_flag = 1
if compile_flag == 0:
    log_file.write("%s.mtuset.debug ====>>> Fail")
log_file.write("*******************************************************************************************")
os.system('cd ..')

