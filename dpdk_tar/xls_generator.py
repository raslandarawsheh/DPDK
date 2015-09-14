#!/usr/bin/python
import xlsxwriter

workBook = xlsxwriter.Workbook('dpdk.xlsx')
workSheet = workBook.add_worksheet('dpdk')

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
workSheet.merge_range('A2:A3', '', headerFormat4)

workSheet.merge_range('B1:C1', '64', headerFormat4)
workSheet.merge_range('B2:C2', 'Testpmd TP Mpps', headerFormat4)

workSheet.merge_range('D1:E1', '128', headerFormat3)
workSheet.merge_range('D2:E2', 'Testpmd TP Mpps', headerFormat3)

workSheet.merge_range('F1:G1', '256', headerFormat4)
workSheet.merge_range('F2:G2', 'Testpmd TP Mpps', headerFormat4)

workSheet.merge_range('H1:I1', '512', headerFormat3)
workSheet.merge_range('H2:I2', 'Testpmd TP Mpps', headerFormat3)

workSheet.merge_range('J1:K1', '1024', headerFormat4)
workSheet.merge_range('J2:K2', 'Testpmd TP Mpps', headerFormat4)

workSheet.set_column('A:A', 20)

workSheet.write('A1', 'msg-size', headerFormat4)
workSheet.write('A4', 'Uni', headerFormat4)
workSheet.write('A5', 'BI', headerFormat4)
workSheet.write('A6', 'Bi Receive-in-line', headerFormat4)
workSheet.write('A7', 'RSS Uni', headerFormat4)
workSheet.write('A8', 'RSS Bi', headerFormat4)
workSheet.write('A9', 'RSS Bi Receive-in-line', headerFormat4)

workSheet.write('B3', 'Expected', headerFormat4)
workSheet.write('C3', 'Real', headerFormat4)

workSheet.write('D3', 'Expected', headerFormat3)
workSheet.write('E3', 'Real', headerFormat3)

workSheet.write('F3', 'Expected', headerFormat4)
workSheet.write('G3', 'Real', headerFormat4)

workSheet.write('H3', 'Expected', headerFormat3)
workSheet.write('I3', 'Real', headerFormat3)

workSheet.write('J3', 'Expected', headerFormat4)
workSheet.write('K3', 'Real', headerFormat4)

workSheet.write('A11', 'PASS', headerFormat0)
workSheet.write('A12', 'FAIL', headerFormat1)
workSheet.write('A13', 'IMPROVED', headerFormat2)


def check_result(expected, real):
    percentage = ((float(real) - float(expected))/float(real))*100
    if (percentage < -1):
        return 1 # Fail
    elif (percentage > 0):
        return 2 # Improved
    else:
        return 0 # Pass

csv_64 =  open('64.csv', 'r')
csv_128 =  open('128.csv', 'r')
csv_256 =  open('256.csv', 'r')
csv_512 =  open('512.csv', 'r')
csv_1024 =  open('1024.csv', 'r')

row = 4
for line in csv_64:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    workSheet.write('B%s' %row, expected, headerFormat4)
    workSheet.write('C%s' %row, real, eval(cell_format))
    row = row + 1

row = 4
for line in csv_128:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "cell_formatttttttttt:",cell_format
    print "Expected %s Real %s " %(expected, real)
    workSheet.write('D%s' %row, expected, headerFormat3)
    workSheet.write('E%s' %row, real, eval(cell_format))
    row = row + 1

row = 4
for line in csv_256:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    workSheet.write('F%s' %row, expected, headerFormat4)
    workSheet.write('G%s' %row, real, eval(cell_format))
    row = row + 1

row = 4
for line in csv_512:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    workSheet.write('H%s' %row, expected, headerFormat3)
    workSheet.write('I%s' %row, real, eval(cell_format))
    row = row + 1

row = 4
for line in csv_1024:
    expected = float(line.split(',')[0])
    real = float(line.split(',')[1])
    rc = check_result(expected, real)
    cell_format = "headerFormat" + str(rc)
    print "Expected %s Real %s " %(expected, real)
    workSheet.write('J%s' %row, expected, headerFormat4)
    workSheet.write('K%s' %row, real, eval(cell_format))
    row = row + 1


workBook.close()
