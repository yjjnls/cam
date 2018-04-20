import os
import sys
import subprocess
import yaml
import platform
import glob
import traceback
import cam
from cam.exceptions import BuildToolError,CommandError
from cam.enums  import Platform,Architecture
from report import Report,Status
from utils import console, Call,OStream

def _msvs_ver(year):
    if type(year) == type(''):
        year = int(year)
    ver={
        2017 : '15',
        2015 : '14',
        2012 : '11',
        2010 : '10',
        2008 : '9',
        2005 : '8'
    }
    return ver.get(year,None)


def _cmake_config_options(config):
    if config.arch == Architecture.X86:
        arch = 'win32'
    elif config.arch == Architecture.X86_64:
        arch = 'x64'

    build_type = 'Release'
    if config.__global__.debug:
        build_type = 'Debug'

    return ' --config %s -- /p:Platform=%s'%(build_type,arch)

def Configure(config,stream):
    directory = config.directory
    location  = config.location
    arch      = config.arch
    platform  = config.platform
    command   = None
    rpath = os.path.relpath(location,directory)
    
    if config.tool == 'cmake':
        command = 'cmake '
        if config.platform.lower() == 'windows':
            ver = _msvs_ver(config.msvs)
            if ver is None:
                raise BuildToolError('Unsupport msvs : %d'% config.msvs)

        if arch == Architecture.X86_64:
            arch = 'Win64'
        command += ' -G"Visual Studio %s %d %s" '%(ver,config.msvs,arch)
        command += ' %s '%rpath

    elif config.tool == 'node-gyp':
        command = 'node-gyp configure '
        if platform == Platform.WINDOWS:
            command += '--msvs_version=%d'%config.msvs
            
            if config.arch == Architecture.X86:
                arch = 'win32'
            elif arch == Architecture.X86_64:
                arch = 'x64'

            command += ' --arch=%s'%arch
            command += ' --directory=%s'%config.location
            directory = config.location
    
    if command is None:
        raise Exception('can not hanlde the comand')
    Call( command,directory ,stream)
 





def Make(config,stream):
    directory = config.directory
    location  = config.location
    arch      = config.arch
    platform  = config.platform
    command   = None
    
    if config.make is None:
        if config.tool == 'cmake':
            command = 'cmake --build . --target ALL_BUILD'
            command += _cmake_config_options(config)

        elif config.tool == 'node-gyp':
            command = 'node-gyp build'
            command += ' --directory=%s'%config.location
            if config.__global__.debug:
                command +=' options=--debug'
        else:
            raise Exception('make with %s not support'%(config.tool))
    else:
        command = config.make
    
    Call( command,directory ,stream)



def CPPLint(config,stream):
    cpplint = config.cpplint
    filters  = cpplint.get('filter',[])
    sources  = cpplint.get('sources',[])
    directory = config.directory
    options = ''
    if len(filters):
        options +=" --filter=" + ",".join(filters)
    slist=[]
    for src in sources:
        rex = os.path.join(config.location,src)
        slist +=glob.glob(rex)
    for filename in slist:
        try:
            Call('cpplint %s %s'%(options,filename),directory,stream)
        except subprocess.CalledProcessError:
            raise Exception('cpplint failed at %s'%filename)


    
def _Exec(commands,config,stream,directory = None):

    if directory:
        directory = config.directory

    for command in commands:
        for name, script in command.viewitems():
            try :
                if script.startswith('$python'):
                    script = script[len('$python'):]
                    exec( script, {
                        'config'   : config,
                        '__file__' : config.__file__
                    })
                else:
                    Call(script,directory,stream)
            except Exception:
                traceback.print_exc(stream)
                raise CommandError(name)

def _Install(config,stream):

    if config.tool == 'cmake':
        command = 'cmake --build . --target INSTALL '
        command += _cmake_config_options(config)
        Call(command, config.directory,stream)
    else:
        raise Exception('unspport install for tool :%s'%config.tool)
    
def _Test(config,stream):

    if config.tool == 'cmake':
        command = 'cmake --build . --target RUN_TESTS '
        command += _cmake_config_options(config)
        Call(command, config.directory,stream)
    else:
        raise Exception('unspport test for tool :%s'%config.tool)

def _Clean(config,stream):
    if config.tool == 'cmake':
        command  = 'cmake --build . --target ALL_BUILD '
        command += _cmake_config_options(config)  + ' /t:clean'
        Call(command, config.directory,stream)
    if config.tool == 'node-gyp':
        command = 'node-gyp clean'
        #command += ' --directory=%s'%config.location
        if config.__global__.debug:
            command +=' options=--debug'
        Call(command, config.location,stream)
    else:
        raise Exception('unspport test for tool :%s'%config.tool)
    

    
class Build(object) :

    projects =[]



    def __init__(self, config):
        self.reports = config.__reports__
        self.args    = config.__args__
        self.option  = config.__global__
        self.config  = config

    def _configure(self,stream ):
        Configure(self.config,stream)

    def _make(self,stream):
        Make(self.config,stream)


    
    def _install(self,stream ):        
        if self.config.install is None:
            _Install( self.config,stream)
        else:
            try:
                _Exec(self.config.install,self.config,stream )
            except CommandError,e:
                raise CommandError( '%s@%s.install'%(self.config.name,e.msg))

    def _test(self,stream ):
        if self.config.test is None:
            _Test( self.config,stream)
        else:
            try:
                _Exec(self.config.test,self.config,stream )
            except CommandError,e:
                raise CommandError( '%s@%s.test'%(self.config.name,e.msg))

 
    def _cpplint(self,stream ):
        CPPLint(self.config,stream)

    def _clean(self,stream):
        _Clean(self.config,stream)

    def _package(self,stream):
        raise CommandError( 'package command not implement' )


    def run(self):
        for report in self.reports:

            if report.status == Status.SKIP:
                continue


            func = getattr(self,'_'+ report.type)

            config = self.config
            if not os.path.isdir(config.directory):
                os.makedirs(config.directory)
            f = None
            logd = self.option.log_dir
            if logd:
                filename = os.path.join( logd,
                '%s-%s-%s-%s.log'%(config.name,report.type,config.platform,config.arch))
                if not os.path.isdir(logd):
                    os.makedirs( logd)

                f = open(filename,'w+')
                stream = OStream(f)
            else:
                stream = OStream()

            try:
                msg = '%-10s : %sing'%(config.name,report.type) + ' ...'
                console.log( '\n'+console.fore.CYAN + console.back.WHITE + console.stype.DIM+
                    '  %-38s'%msg)

                func(stream)
                report.status = Status.DONE
            except subprocess.CalledProcessError:
                report.status  = Status.FAIL
                report.message = '<%s> %s failed'%(config.name,report.type)
                raise CommandError(report.message)
