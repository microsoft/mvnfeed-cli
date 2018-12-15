# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os

def cleanup_file(type, input, output):
    """
    Cleanup input file.

    :param type: type of fhe file. Either 'maven' or 'gradle'
    :param input: input filename
    :param output: output filename
    """
    if type == 'maven':
        _cleanup_maven(input, output)
    elif type == 'gradle':
        _cleanup_gradle(input, output)
    else:
        raise ValueError('Invalid type ' + type)


def _cleanup_maven(input, output):
    if not os.path.exists(input):
        raise ValueError('Input file doesn\'t exist')

    packages = []
    with open(input, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip().rstrip()
            if line == '' or line == 'The following files have been resolved:':
                continue
            # let's just remove the scope information
            packages.append(line[:line.rfind(':')])

    packages = list(set(packages))
    packages.sort()

    with open(output, 'w') as file:
        for package in packages:
            file.write(package + '\n')


def _cleanup_gradle(input, output):
    RESOLVE = 'Attempting to resolve component for '

    if not os.path.exists(input):
        raise ValueError('Input file doesn\'t exist')

    packages = []
    with open(input, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip().rstrip()
            if RESOLVE in line:
                start = line.find(RESOLVE) + len(RESOLVE)
                end = line.find(' ', start)
                packages.append(line[start:end])
                continue

            if not '\--- ' in line and not '+--- ' in line:
                # not a package line
                continue
            if ' -> ' in line or ' (*)' in line or ' (n)' in line:
                # package was bumped somewhere else
                continue

            packages.append(line[line.rfind(' ') + 1:])

    packages = list(set(packages))
    packages.sort()

    with open(output, 'w') as file:
        for package in packages:
            file.write(package + '\n')
