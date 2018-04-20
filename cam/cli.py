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

import argparse
import pkg_resources
import setuptools
import pkginfo

import colorama
import cpplint

import cam
from cam.config import Load


def _registered_commands(group='cam.registered_commands'):
    registered_commands = pkg_resources.iter_entry_points(group=group)
    return dict((c.name, c) for c in registered_commands)



def dispatch(argv):
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(prog="cam")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {0} ".format(cam.__version__)
    )

    parser.add_argument(
        "--toolset",
        type=str, default = '',
        help ="Specify tools set vs2015,vs205 ..."
    )

    parser.add_argument(
        '-p',"--project",
        type=str, action = 'append',
        help ="Only build the specified project"
        "If not set, build all projects"
    )

    parser.add_argument(
        "--log-dir",
        type=str, default=None,
        help ="Directory of the buid message writen to."
        "If not specified, message output to stdout.",
    )

    parser.add_argument(
        "--scheme",
        type=str, default='./build.yaml',
        help ="Scheme of the build."
    )

    parser.add_argument(
        "--debug",
        action='store_true', default=False,
        help ="Build debug version or not."
    )
    
    parser.add_argument(
        "command",
        choices=registered_commands.keys(),
    )
    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args(argv)

    main = registered_commands[args.command].load()

    configs = Load( args)

    main(args.args, configs)
