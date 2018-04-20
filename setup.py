# Copyright 2018 Donald Stufft and individual contributors
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
from setuptools import setup

import sys

import cam


install_requires = [
    "colorama >= 0.3.9",
    "cpplint >= 1.3.0",
    "pyyaml  >= 3.9"
]

if sys.version_info[:2] < (2, 7):
    install_requires += [
        "argparse",
    ]

setup(
    name=cam.__title__,
    version=cam.__version__,

    description=cam.__summary__,
    long_description=open("README.md").read(),
    license=cam.__license__,
    url=cam.__uri__,
    project_urls={
        'Cam source': 'https://github.com/mingyiz/cam/',
    },

    author=cam.__author__,
    author_email=cam.__email__,

    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],

    packages=["cam", "cam.commands"],

    entry_points={
        "cam.registered_commands": [
            "build = cam.commands.build:main",
        ],
        "console_scripts": [
            "cam = cam.__main__:main",
        ],
    },

    install_requires=install_requires,
)
