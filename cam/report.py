
from colorama import Fore,Back,Style
from utils import console
class Status:
    ''' Enumeration of project step exec status '''
    NULL = ' NOP '
    DONE = ' OK  '
    FAIL = ' ERR '
    SKIP = ' N/A '


class Report(object):
    scheme ={
        'color' :{
                          
            Status.NULL : (console.fore.WHITE, ''),
            Status.DONE : (console.fore.GREEN, ''),
            Status.FAIL : (console.fore.RED, ''),
            Status.SKIP : (console.fore.CYAN, ''),
        }
    }

    def __init__(self, type,config,status = Status.NULL):
        self.type    = type
        self.config  = config # config of project
        self.message = None
        self.status  = status

        


    

    def Print(self, prog=None):
        color = self.scheme['color']
        if prog :
            console.log(prog)
        fore,back = color[self.status]
        back = back #not use

        console.log( fore + '[ %6s ]    '%self.status + console.fore.WHITE + self.type)
        if self.message:
            console.log( console.fore.CYAN + '             ' + self.message)
    