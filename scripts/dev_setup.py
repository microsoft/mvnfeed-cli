# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function

import sys
import os
from subprocess import check_call, CalledProcessError


def py_command(command):
    try:
        print('Executing: ' + sys.executable + ' ' + command)
        check_call([sys.executable] + command.split(), cwd=os.path.abspath('.'))
        print()
    except CalledProcessError as err:
        print(err, file=sys.stderr)
        sys.exit(1)


def pip_command(command):
    py_command('-m pip ' + command)


packages = []

packages.append('src/mvnfeed_modules/mvnfeed-cli-common')
packages.append('src/mvnfeed_modules/mvnfeed-cli-transfer')
packages.append('src/mvnfeed-cli')

pip_command('install -e {}'.format(' -e '.join(packages)))
