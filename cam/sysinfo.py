# cerbero - a multi-platform build system for Open Source software
# Copyright (C) 2012 Andoni Morales Alastruey <ylatuya@gmail.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
import shutil
import sys
try:
    import sysconfig
except:
    from distutils import sysconfig
try:
    import xml.etree.cElementTree as etree
except ImportError:
    from lxml import etree
from distutils.version import StrictVersion
import gettext
import platform as pplatform
import re

import cam
from cam.enums import Platform,Architecture,Distro,DistroVersion


def windows_arch():
    """
    Detecting the 'native' architecture of Windows is not a trivial task. We
    cannot trust that the architecture that Python is built for is the 'native'
    one because you can run 32-bit apps on 64-bit Windows using WOW64 and
    people sometimes install 32-bit Python on 64-bit Windows.
    """
    # These env variables are always available. See:
    # https://msdn.microsoft.com/en-us/library/aa384274(VS.85).aspx
    # https://blogs.msdn.microsoft.com/david.wang/2006/03/27/howto-detect-process-bitness/
    arch = os.environ.get('PROCESSOR_ARCHITEW6432', '').lower()
    if not arch:
        # If this doesn't exist, something is messing with the environment
        try:
            arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
        except KeyError:
            raise FatalError(_('Unable to detect Windows architecture'))
    return arch

def system_info():
    '''
    Get the sysem information.
    Return a tuple with the platform type, the architecture and the
    distribution
    '''
    # Get the platform info
    platform = os.environ.get('OS', '').lower()
    if not platform:
        platform = sys.platform
    if platform.startswith('win'):
        platform = Platform.WINDOWS
    elif platform.startswith('darwin'):
        platform = Platform.DARWIN
    elif platform.startswith('linux'):
        platform = Platform.LINUX
    else:
        raise FatalError(_("Platform %s not supported") % platform)

    # Get the architecture info
    if platform == Platform.WINDOWS:
        arch = windows_arch()
        if arch in ('x64', 'amd64'):
            arch = Architecture.X86_64
        elif arch == 'x86':
            arch = Architecture.X86
        else:
            raise FatalError(_("Windows arch %s is not supported") % arch)
    else:
        uname = os.uname()
        arch = uname[4]
        if arch == 'x86_64':
            arch = Architecture.X86_64
        elif arch.endswith('86'):
            arch = Architecture.X86
        elif arch.startswith('armv7'):
            arch = Architecture.ARMv7
        elif arch.startswith('arm'):
            arch = Architecture.ARM
        else:
            raise FatalError(_("Architecture %s not supported") % arch)

    # Get the distro info
    if platform == Platform.LINUX:
        d = pplatform.linux_distribution()

        if d[0] == '' and d[1] == '' and d[2] == '':
            if os.path.exists('/etc/arch-release'):
                # FIXME: the python2.7 platform module does not support Arch Linux.
                # Mimic python3.4 platform.linux_distribution() output.
                d = ('arch', 'Arch', 'Linux')
            elif os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    if 'ID="amzn"\n' in f.readlines():
                        d = ('RedHat', 'amazon', '')
                    else:
                        f.seek(0, 0)
                        for line in f:
                            k,v = line.rstrip().split("=")
                            if k == 'NAME':
                                name = v.strip('"')
                            elif k == 'VERSION_ID':
                                version = v.strip('"')
                        d = (name, version, '');

        if d[0] in ['Ubuntu', 'debian', 'LinuxMint']:
            distro = Distro.DEBIAN
            if d[2] in ['maverick', 'isadora']:
                distro_version = DistroVersion.UBUNTU_MAVERICK
            elif d[2] in ['lucid', 'julia']:
                distro_version = DistroVersion.UBUNTU_LUCID
            elif d[2] in ['natty', 'katya']:
                distro_version = DistroVersion.UBUNTU_NATTY
            elif d[2] in ['oneiric', 'lisa']:
                distro_version = DistroVersion.UBUNTU_ONEIRIC
            elif d[2] in ['precise', 'maya']:
                distro_version = DistroVersion.UBUNTU_PRECISE
            elif d[2] in ['quantal', 'nadia']:
                distro_version = DistroVersion.UBUNTU_QUANTAL
            elif d[2] in ['raring', 'olivia']:
                distro_version = DistroVersion.UBUNTU_RARING
            elif d[2] in ['saucy', 'petra']:
                distro_version = DistroVersion.UBUNTU_SAUCY
            elif d[2] in ['trusty', 'qiana', 'rebecca']:
                distro_version = DistroVersion.UBUNTU_TRUSTY
            elif d[2] in ['utopic']:
                distro_version = DistroVersion.UBUNTU_UTOPIC
            elif d[2] in ['vivid']:
                distro_version = DistroVersion.UBUNTU_VIVID
            elif d[2] in ['wily']:
                distro_version = DistroVersion.UBUNTU_WILY
            elif d[2] in ['xenial', 'sarah', 'serena', 'sonya', 'sylvia']:
                distro_version = DistroVersion.UBUNTU_XENIAL
            elif d[2] in ['artful']:
                distro_version = DistroVersion.UBUNTU_ARTFUL
            elif d[1].startswith('6.'):
                distro_version = DistroVersion.DEBIAN_SQUEEZE
            elif d[1].startswith('7.') or d[1].startswith('wheezy'):
                distro_version = DistroVersion.DEBIAN_WHEEZY
            elif d[1].startswith('8.') or d[1].startswith('jessie'):
                distro_version = DistroVersion.DEBIAN_JESSIE
            elif d[1].startswith('9.') or d[1].startswith('stretch'):
                distro_version = DistroVersion.DEBIAN_STRETCH
            elif d[1].startswith('10.') or d[1].startswith('buster'):
                distro_version = DistroVersion.DEBIAN_BUSTER
            else:
                raise Exception("Distribution '%s' not supported" % str(d))
        elif d[0] in ['RedHat', 'Fedora', 'CentOS', 'Red Hat Enterprise Linux Server', 'CentOS Linux']:
            distro = Distro.REDHAT
            if d[1] == '16':
                distro_version = DistroVersion.FEDORA_16
            elif d[1] == '17':
                distro_version = DistroVersion.FEDORA_17
            elif d[1] == '18':
                distro_version = DistroVersion.FEDORA_18
            elif d[1] == '19':
                distro_version = DistroVersion.FEDORA_19
            elif d[1] == '20':
                distro_version = DistroVersion.FEDORA_20
            elif d[1] == '21':
                distro_version = DistroVersion.FEDORA_21
            elif d[1] == '22':
                distro_version = DistroVersion.FEDORA_22
            elif d[1] == '23':
                distro_version = DistroVersion.FEDORA_23
            elif d[1] == '24':
                distro_version = DistroVersion.FEDORA_24
            elif d[1] == '25':
                distro_version = DistroVersion.FEDORA_25
            elif d[1] == '26':
                distro_version = DistroVersion.FEDORA_26
            elif d[1] == '27':
                distro_version = DistroVersion.FEDORA_27
            elif d[1].startswith('6.'):
                distro_version = DistroVersion.REDHAT_6
            elif d[1].startswith('7.'):
                distro_version = DistroVersion.REDHAT_7
            elif d[1] == 'amazon':
                distro_version = DistroVersion.AMAZON_LINUX
            else:
                # FIXME Fill this
                raise Exception("Distribution '%s' not supported" % str(d))
        elif d[0].strip() in ['openSUSE']:
            distro = Distro.SUSE
            if d[1] == '42.2':
                distro_version = DistroVersion.OPENSUSE_42_2
            elif d[1] == '42.3':
                distro_version = DistroVersion.OPENSUSE_42_3
            else:
                # FIXME Fill this
                raise Exception("Distribution OpenSuse '%s' "
                                 "not supported" % str(d))
        elif d[0].strip() in ['openSUSE Tumbleweed']:
            distro = Distro.SUSE
            distro_version = DistroVersion.OPENSUSE_TUMBLEWEED
        elif d[0].strip() in ['arch']:
            distro = Distro.ARCH
            distro_version = DistroVersion.ARCH_ROLLING
        elif d[0].strip() in ['Gentoo Base System']:
            distro = Distro.GENTOO
            distro_version = DistroVersion.GENTOO_VERSION
        else:
            raise Exception("Distribution '%s' not supported" % str(d))
    elif platform == Platform.WINDOWS:
        distro = Distro.WINDOWS
        win32_ver = pplatform.win32_ver()[0]
        dmap = {'xp': DistroVersion.WINDOWS_XP,
                'vista': DistroVersion.WINDOWS_VISTA,
                '7': DistroVersion.WINDOWS_7,
                'post2008Server': DistroVersion.WINDOWS_8,
                '8': DistroVersion.WINDOWS_8,
                'post2012Server': DistroVersion.WINDOWS_8_1,
                '8.1': DistroVersion.WINDOWS_8_1,
                '10': DistroVersion.WINDOWS_10}
        if win32_ver in dmap:
            distro_version = dmap[win32_ver]
        else:
            raise Exception("Windows version '%s' not supported" % win32_ver)
    elif platform == Platform.DARWIN:
        distro = Distro.OS_X
        ver = pplatform.mac_ver()[0]
        if ver.startswith('10.13'):
            distro_version = DistroVersion.OS_X_HIGH_SIERRA
        elif ver.startswith('10.12'):
            distro_version = DistroVersion.OS_X_SIERRA
        elif ver.startswith('10.11'):
            distro_version = DistroVersion.OS_X_EL_CAPITAN
        elif ver.startswith('10.10'):
            distro_version = DistroVersion.OS_X_YOSEMITE
        elif ver.startswith('10.9'):
            distro_version = DistroVersion.OS_X_MAVERICKS
        elif ver.startswith('10.8'):
            distro_version = DistroVersion.OS_X_MOUNTAIN_LION
        else:
            raise Exception("Mac version %s not supported" % ver)



    return platform, arch, distro, distro_version


(PLATFORM,ARCH,DISTRO,DISTRO_VERSION ) = system_info()