#!/usr/bin/python
import xlsxwriter

workBook = xlsxwriter.Workbook('/download/performance_result/dpdk.xlsx')
workSheet64 = workBook.add_worksheet('64')
workSheet128 = workBook.add_worksheet('128')
workSheet256 = workBook.add_worksheet('256')
workSheet512 = workBook.add_worksheet('512')
workSheet1024 = workBook.add_worksheet('1024')

workSheet64.set_column(0, 7, 20)
workSheet128.set_column(0, 7, 20)
workSheet256.set_column(0, 7, 20)
workSheet512.set_column(0, 7, 20)
workSheet1024.set_column(0, 7, 20)

headerFormat3 = workBook.add_format({
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#00CCFF',
            'border': True,

            })
headerFormat4 = workBook.add_format({
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#3366FF',
            'border': True,
            })

headerFormat0 = workBook.add_format({ #PASS Case
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#008000',
            'border': True,
            })

headerFormat1 = workBook.add_format({ # Failed Case
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#FFCC00',
            'border': True,
            })

headerFormat2 = workBook.add_format({ # Improved Case
            'bold':     True,
            'align':    'center',
            'valign':   'vcenter',
            'fg_color': '#FF6600',
            'border': True,
            })

headerFormat4.set_num_format('0.00')

workSheet64.merge_range('A3:A4', '', headerFormat4)
workSheet128.merge_range('A3:A4', '', headerFormat4)
workSheet256.merge_range('A3:A4', '', headerFormat4)
workSheet512.merge_range('A3:A4', '', headerFormat4)
workSheet1024.merge_range('A3:A4', '', headerFormat4)

workSheet64.merge_range('B2:H2', '64', headerFormat4)
workSheet128.merge_range('B2:H2', '128', headerFormat4)
workSheet256.merge_range('B2:H2', '256', headerFormat4)
workSheet512.merge_range('B2:H2', '512', headerFormat4)
workSheet1024.merge_range('B2:H2', '1024', headerFormat4)

workSheet64.merge_range('B3:H3', 'Testpmd TP Mpps', headerFormat4)
workSheet128.merge_range('B3:H3', 'Testpmd TP Mpps', headerFormat4)
workSheet256.merge_range('B3:H3', 'Testpmd TP Mpps', headerFormat4)
workSheet512.merge_range('B3:H3', 'Testpmd TP Mpps', headerFormat4)
workSheet1024.merge_range('B3:H3', 'Testpmd TP Mpps', headerFormat4)

workSheet64.write('A1', 'Tests Configuration', headerFormat4)
workSheet128.write('A1', 'Tests Configuration', headerFormat4)
workSheet256.write('A1', 'Tests Configuration', headerFormat4)
workSheet512.write('A1', 'Tests Configuration', headerFormat4)
workSheet1024.write('A1', 'Tests Configuration', headerFormat4)

workSheet64.write('A2', 'msg-size', headerFormat4)
workSheet128.write('A2', 'msg-size', headerFormat4)
workSheet256.write('A2', 'msg-size', headerFormat4)
workSheet512.write('A2', 'msg-size', headerFormat4)
workSheet1024.write('A2', 'msg-size', headerFormat4)

workSheet64.write('A5', 'Uni', headerFormat4)
workSheet128.write('A5', 'Uni', headerFormat4)
workSheet256.write('A5', 'Uni', headerFormat4)
workSheet512.write('A5', 'Uni', headerFormat4)
workSheet1024.write('A5', 'Uni', headerFormat4)

workSheet64.write('A6', 'Bi', headerFormat4)
workSheet128.write('A6', 'Bi', headerFormat4)
workSheet256.write('A6', 'Bi', headerFormat4)
workSheet512.write('A6', 'Bi', headerFormat4)
workSheet1024.write('A6', 'Bi', headerFormat4)

workSheet64.write('A7', 'Bi Receive-in-line', headerFormat4)
workSheet128.write('A7', 'Bi Receive-in-line', headerFormat4)
workSheet256.write('A7', 'Bi Receive-in-line', headerFormat4)
workSheet512.write('A7', 'Bi Receive-in-line', headerFormat4)
workSheet1024.write('A7', 'Bi Receive-in-line', headerFormat4)

workSheet64.write('A8', 'RSS Uni', headerFormat4)
workSheet128.write('A8', 'RSS Uni', headerFormat4)
workSheet256.write('A8', 'RSS Uni', headerFormat4)
workSheet512.write('A8', 'RSS Uni', headerFormat4)
workSheet1024.write('A8', 'RSS Uni', headerFormat4)

workSheet64.write('A9', 'RSS Bi', headerFormat4)
workSheet128.write('A9', 'RSS Bi', headerFormat4)
workSheet256.write('A9', 'RSS Bi', headerFormat4)
workSheet512.write('A9', 'RSS Bi', headerFormat4)
workSheet1024.write('A9', 'RSS Bi', headerFormat4)

workSheet64.write('A10', 'RSS Bi Receive-in-line', headerFormat4)
workSheet128.write('A10', 'RSS Bi Receive-in-line', headerFormat4)
workSheet256.write('A10', 'RSS Bi Receive-in-line', headerFormat4)
workSheet512.write('A10', 'RSS Bi Receive-in-line', headerFormat4)
workSheet1024.write('A10', 'RSS Bi Receive-in-line', headerFormat4)



workSheet64.merge_range('B1:C1', 'Basic Tests', headerFormat4)
workSheet128.merge_range('B1:C1', 'Basic Tests', headerFormat4)
workSheet256.merge_range('B1:C1', 'Basic Tests', headerFormat4)
workSheet512.merge_range('B1:C1', 'Basic Tests', headerFormat4)
workSheet1024.merge_range('B1:C1', 'Basic Tests', headerFormat4)

workSheet64.write('D1', 'Checksum Enabled', headerFormat4)
workSheet128.write('D1', 'Checksum Enabled', headerFormat4)
workSheet256.write('D1', 'Checksum Enabled', headerFormat4)
workSheet512.write('D1', 'Checksum Enabled', headerFormat4)
workSheet1024.write('D1', 'Checksum Enabled', headerFormat4)

workSheet64.write('E1', 'Checksum L3 SW', headerFormat4)
workSheet128.write('E1', 'Checksum L3 SW', headerFormat4)
workSheet256.write('E1', 'Checksum L3 SW', headerFormat4)
workSheet512.write('E1', 'Checksum L3 SW', headerFormat4)
workSheet1024.write('E1', 'Checksum L3 SW', headerFormat4)

workSheet64.write('F1', 'Checksum L3 HW', headerFormat4)
workSheet128.write('F1', 'Checksum L3 HW', headerFormat4)
workSheet256.write('F1', 'Checksum L3 HW', headerFormat4)
workSheet512.write('F1', 'Checksum L3 HW', headerFormat4)
workSheet1024.write('F1', 'Checksum L3 HW', headerFormat4)

workSheet64.write('G1', 'Checksum L4 SW', headerFormat4)
workSheet128.write('G1', 'Checksum L4 SW', headerFormat4)
workSheet256.write('G1', 'Checksum L4 SW', headerFormat4)
workSheet512.write('G1', 'Checksum L4 SW', headerFormat4)
workSheet1024.write('G1', 'Checksum L4 SW', headerFormat4)

workSheet64.write('H1', 'Checksum L4 HW', headerFormat4)
workSheet128.write('H1', 'Checksum L4 HW', headerFormat4)
workSheet256.write('H1', 'Checksum L4 HW', headerFormat4)
workSheet512.write('H1', 'Checksum L4 HW', headerFormat4)
workSheet1024.write('H1', 'Checksum L4 HW', headerFormat4)

workSheet64.write('B4', 'Expected', headerFormat4)
workSheet128.write('B4', 'Expected', headerFormat4)
workSheet256.write('B4', 'Expected', headerFormat4)
workSheet512.write('B4', 'Expected', headerFormat4)
workSheet1024.write('B4', 'Expected', headerFormat4)

workSheet64.write('C4', 'Real', headerFormat4)
workSheet128.write('C4', 'Real', headerFormat4)
workSheet256.write('C4', 'Real', headerFormat4)
workSheet512.write('C4', 'Real', headerFormat4)
workSheet1024.write('C4', 'Real', headerFormat4)

workSheet64.write('D4', 'Real', headerFormat4)
workSheet128.write('D4', 'Real', headerFormat4)
workSheet256.write('D4', 'Real', headerFormat4)
workSheet512.write('D4', 'Real', headerFormat4)
workSheet1024.write('D4', 'Real', headerFormat4)

workSheet64.write('E4', 'Real', headerFormat4)
workSheet128.write('E4', 'Real', headerFormat4)
workSheet256.write('E4', 'Real', headerFormat4)
workSheet512.write('E4', 'Real', headerFormat4)
workSheet1024.write('E4', 'Real', headerFormat4)

workSheet64.write('F4', 'Real', headerFormat4)
workSheet128.write('F4', 'Real', headerFormat4)
workSheet256.write('F4', 'Real', headerFormat4)
workSheet512.write('F4', 'Real', headerFormat4)
workSheet1024.write('F4', 'Real', headerFormat4)

workSheet64.write('G4', 'Real', headerFormat4)
workSheet128.write('G4', 'Real', headerFormat4)
workSheet256.write('G4', 'Real', headerFormat4)
workSheet512.write('G4', 'Real', headerFormat4)
workSheet1024.write('G4', 'Real', headerFormat4)

workSheet64.write('H4', 'Real', headerFormat4)
workSheet128.write('H4', 'Real', headerFormat4)
workSheet256.write('H4', 'Real', headerFormat4)
workSheet512.write('H4', 'Real', headerFormat4)
workSheet1024.write('H4', 'Real', headerFormat4)



def check_result(expected, real):
    if float(real) != 0:
        percentage = ((float(real) - float(expected))/float(real))*100
        if (percentage < -1):
            return 1 # Fail
        elif (percentage > 0):
            return 2 # Improved
        else:
            return 0 # Pass
    else:
        return 1
csv_64 =  open('/download/performance_result/64.csv', 'r')
csv_128 =  open('/download/performance_result/128.csv', 'r')
csv_256 =  open('/download/performance_result/256.csv', 'r')
csv_512 =  open('/download/performance_result/512.csv', 'r')
csv_1024 =  open('/download/performance_result/1024.csv', 'r')

row = 5
coloumn = 'C'

for line in csv_64:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    if coloumn == 'C':
        workSheet64.write('B%s' %row, expected, headerFormat4)
    workSheet64.write('%s%s' %(coloumn,row), real, eval(cell_format))
    if row == 10:
	row = 4
	new_coloumn = chr(ord(coloumn)+1)
	coloumn = new_coloumn
    row = row + 1

row = 5
coloumn = 'C'

for line in csv_128:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    if coloumn == 'C':
        workSheet128.write('B%s' %row, expected, headerFormat4)
    workSheet128.write('%s%s' %(coloumn,row), real, eval(cell_format))
    if row == 10:
        row = 4
	new_coloumn = chr(ord(coloumn)+1)
        coloumn = new_coloumn

    row = row + 1

row = 5
coloumn = 'C'

for line in csv_256:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    if coloumn == 'C':
        workSheet256.write('B%s' %row, expected, headerFormat4)
    workSheet256.write('%s%s' %(coloumn,row), real, eval(cell_format))
    if row == 10:
        row = 4
        new_coloumn = chr(ord(coloumn)+1)
        coloumn = new_coloumn

    row = row + 1

row = 5
coloumn = 'C'

for line in csv_512:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    if coloumn == 'C':
        workSheet512.write('B%s' %row, expected, headerFormat4)
    workSheet512.write('%s%s' %(coloumn,row), real, eval(cell_format))
    if row == 10:
        row = 4
        new_coloumn = chr(ord(coloumn)+1)
        coloumn = new_coloumn
    row = row + 1

row = 5
coloumn = 'C'

for line in csv_1024:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    if coloumn == 'C':
        workSheet1024.write('B%s' %row, expected, headerFormat4)
    workSheet1024.write('%s%s' %(coloumn,row), real, eval(cell_format))
    if row == 10:
        row = 4
	new_coloumn = chr(ord(coloumn)+1)
        coloumn = new_coloumn

    row = row + 1


workBook.close()
