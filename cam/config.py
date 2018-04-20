# porting from cerbero config.py
import os
import sys
import copy

import yaml
import cam
from cam.enums import Platform,Architecture
from cam.sysinfo import PLATFORM,ARCH



class Config (object):
    name    = ''
    _properties = ['platform', 'arch', 
                   'prefix', 'target',
                   'tool','msvs','directory',
                   'steps',
                   'location',
                   'configure','cpplint','make','test','install'
                   ]

    def __init__(self,name):
        self.name = name

        for a in self._properties:
            setattr(self, a, None)
        self._load_defaults()

    def _load_defaults(self):
        self.set_property('directory', './build')
        self.set_property('prefix', None)
        self.set_property('target', None)
        
       
        self.set_property('platform', PLATFORM)
        self.set_property('arch', ARCH)
        self.set_property('tool', 'cmake')
        self.set_property('configure',None)
        self.set_property('cpplint',None)
        self.set_property('make',None)
        self.set_property('test',None)
        self.set_property('install',None)
        self.set_property('steps',['configure','make'])

    def set_property(self, name, value, force=False):
        if name not in self._properties:
            raise Exception('Unknown key %s' % name)
        if force or getattr(self, name) is None:
            setattr(self, name, value)

    def overlap(self, conf):
        for name in self._properties:
            if conf.has_key(name):
                setattr(self,name, conf[name])

    def map(self):
        d={'name':self.name}
        for name in self._properties:
            d[name] =getattr(self,name)
        return d

    def __str__(self):
        obj={}
        for name in self._properties:
            if hasattr(self,name):
                obj[name] = getattr(self,name)
        return '---- %s ----\n%s'%(self.name,yaml.dump(obj,default_flow_style=False))



def Load(args):
    ''' Load the configuration '''
    if not os.path.isfile( args.scheme):
        raise Exception('specified build scheme <%s> not exists'%args.file)
    scheme = yaml.load( open(args.scheme) )
    config = Config('global')
    config.overlap( scheme )
    projects = scheme.get('project',[])
    configs =[]
    for prj in projects:
        for name , val in prj.viewitems():
            config = Config(name)
            config.overlap(scheme)
            config.overlap(val)

            if args.toolset and args.toolset.startswith("vs"):
                config.msvs = int(args.toolset[2:])

            path = os.path.abspath( args.scheme)
            dir  = os.path.dirname( path)

            if not os.path.isabs( config.location ):
                config.location = os.path.join( dir, config.location)

            config.directory = os.path.join( config.location, config.directory)
            config.directory = os.path.abspath(config.directory)
            config.__file__      = path
            config.__global__    = args
            config.__scheme__    = scheme

            configs.append(config)
    return configs