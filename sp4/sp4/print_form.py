import os


def isRun():
    if os.system('lpstat -r'):
        return True
        else:
            return False


def gerPrinter():
    printer = os.system('lpstat -a')
    if printer is None:
        return None
        else:
            return printer


def runPrinter(printerName, fileName):
    os.system('lpr -P -#'+''+num+''+''+printerName+''+fileName)


def start():
    if isRun():
        printerName = getPrinter()
        if not (printer Name is Nome):
            runPrinter(printerName, 1, "pdfname")
            else:
                print('Kein frei Druken')
    else:
        print('No CUPS')


start()
