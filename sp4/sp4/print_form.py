import subprocess
def isRun():
	if cmd('lpstat -r'):
		return True
	else:
		return False

def getPrinter():
	printer = cmd('lpstat -a')
	if printer is None:
		return None
	else:
		return printer

def runPrinter(printerName,num,fileName):
	printstring = 'lpr -P {p} -# {n} {file}'
	cmd(printstring.format(p=printerName,n=num,file=fileName))

def start():
	if isRun():
		printerName = getPrinter()
		if not (printerName is None):
			runPrinter(printerName,1,"pdfname")
		else:
			print('Keinen freien Druker')
	else:
		print('No CUPS')
		
def cmd(command):
    subp = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    subp.wait(2)
    if subp.poll() == 0:
        return subp.communicate()[1]
    else:
        return None

if __name__ == '__main__' :
	start()
