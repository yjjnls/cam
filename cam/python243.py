
#Python 2 function wrapper For Python 3
from colorama import Style
def Print(file, args):
    if file:
        for arg in args:
            print >>file,arg,
        print >>file, Style.RESET_ALL
    else:
        for arg in args:
            print arg,