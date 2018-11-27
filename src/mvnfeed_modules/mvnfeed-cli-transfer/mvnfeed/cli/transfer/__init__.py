# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pkg_resources
pkg_resources.declare_namespace(__name__)

import knack.help

def load_params(_):
    import knack.arguments

def load_commands():
    import knack.commands
