#!/usr/bin/env python
# Copyright 2013 Mingyi Zhang
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

import sys
import traceback
from cam.cli import dispatch


def main():
    try:
        return dispatch(sys.argv[1:])
    except Exception as exc:
        f = open('cam.~dump','w+')
        traceback.print_exc(file=f)
        f.write( str(exc))
        f.close()
        return '{0}: {1}'.format(
            exc.__class__.__name__,
            exc.args[0],
        )


if __name__ == "__main__":
    sys.exit(main())