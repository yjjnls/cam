# Copyright 2018 Mingyi Zhang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import os.path
import functools
import getpass
import sys
import argparse
import warnings

import subprocess
import colorama
from colorama import Fore, Back,Style,init

import cam
from cam.sysinfo import PLATFORM,ARCH
from cam.enums import Platform,Architecture
_colorama_stream = None

if PLATFORM == Platform.WINDOWS:
    colorama.init( wrap = False )
    _colorama_stream = colorama.AnsiToWin32(sys.stderr).stream

else:
    colorama.init(autoreset = True)


# Shim for raw_input,print in python3
if sys.version_info > (3,):
    input_func = input
else:
    input_func = raw_input
class Console:
    stype = colorama.Style
    fore  = colorama.Fore
    back  = colorama.Back


    #python 3
    def _print(self,*args):
        global _colorama_stream
        print(args, file= _colorama_stream)
        if _colorama_stream:
            print(Style.RESET_ALL,file=_colorama_stream )
    
    def log(self,*args):
        global _colorama_stream
        if sys.version_info < (3,):
            from cam.python243 import Print
            Print(_colorama_stream,list(args))
        else:
            self._print(args)

console = Console()
class OStream:
    ''' out stream
    '''

    def __init__(self, stream=sys.stdout):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
       
def Call(cmd, cmd_dir='.',stream = sys.stdout):
    
    if stream.stream != sys.stdout:
        stream.write("Running command '%s'\n" % cmd)
        stream.flush()
    
    subprocess.check_call(cmd, cwd=cmd_dir,
        stderr= subprocess.STDOUT,
        stdout= stream,
        env=os.environ.copy(), shell=True)

