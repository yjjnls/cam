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
from __future__ import absolute_import, unicode_literals, print_function

import argparse
import os.path
import copy
import math

from cam.utils import console
from cam.report import Report,Status
from cam.build import Build
from cam.exceptions import CommandError

def _is_null(args):
    for v in var(args).values():
        if v:
            return False
    return True

def _filter(args,configs):
    confs=[]
    for config in configs:
        g = config.__global__
        config.__reports__=[]
        config.__args__=copy.deepcopy(args)
        

        if g.project is None or config.name in g.project:
            if not (True in vars(args).values()):
                for name in config.steps:
                    setattr(config.__args__,name, True)

            #clean should be run separately
            if args.clean:
                config.__reports__.append(Report('clean',config))

            for name in config.steps:
                if vars(config.__args__).get(name,False):
                    config.__reports__.append(Report(name,config))
                #else:
                #    config.__reports__.append(Report(name,config,Status.SKIP))
            confs.append(config)            
    return confs

def _Print(configs):
    for config in configs:
        console.log('')
        console.log( console.back.BLUE + '    %-36s'%config.name)
        for report in config.__reports__:
            report.Print()

def build(args,configs):
    configs = _filter(args,configs)

    for config in configs:
        try:
            Build(config).run()
        except CommandError,e:
            _Print(configs)
            raise e
    _Print(configs)        






def main(args, configs):
    parser = argparse.ArgumentParser(prog="cam build")
    parser.add_argument(
        "--configure",
        action='store_true',
        default=False,
        help="Do configure for specifed project. ",
    )
    parser.add_argument(
        "--make",
        action='store_true',
        default=False,
        help="Do make for specifed project. ",
    )
    parser.add_argument(
        "--test",
        action='store_true',
        default=False,
        help="Do test for specifed project. ",
    )
    parser.add_argument(
        "--install",
        action='store_true',
        default=False,
        help="Do installation for specifed project. ",
    )
    parser.add_argument(
        "--cpplint",
        action='store_true',
        default=False,
        help="Do cpplint check for specifed project. ",
    )

    parser.add_argument(
        "--clean",
        action='store_true',
        default=False,
        help="Do clean specifed project. ",
    )

    parser.add_argument(
        "--package",
        action='store_true',
        default=False,
        help="Do package for specifed project. ",
    )

    args = parser.parse_args(args)

    if args.clean and math.fsum((vars(args).values())) > 1:
        print(vars(args))
        raise CommandError('clean could not work with other options.')

    # Call the register function with the args from the command line
    build(args,configs)
