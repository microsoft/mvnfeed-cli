# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import knack

def load_transfer_arguments(cli_command_loader):
    with knack.arguments.ArgumentsContext(cli_command_loader, 'config stage_dir') as ac:
        ac.argument('path', options_list=('--path'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'config repo add') as ac:
        ac.argument('name', options_list=('--name'))
        ac.argument('username', options_list=('--username'))
        ac.argument('feed_url', options_list=('--feed_url'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'config repo delete') as ac:
        ac.argument('name', options_list=('--name'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'artifact') as ac:
        ac.argument('from_repo', options_list=('--from'))
        ac.argument('to_repo', options_list=('--to'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'artifact transfer') as ac:
        ac.argument('name', options_list=('--name'))
        ac.argument('transfer_deps', options_list=('--transfer_deps'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'artifact bulk-transfer') as ac:
        ac.argument('filename', options_list=('--filename'))
        ac.argument('transfer_deps', options_list=('--transfer_deps'))

    with knack.arguments.ArgumentsContext(cli_command_loader, 'input cleanup') as ac:
        ac.argument('type', options_list=('--type'))
        ac.argument('input', options_list=('--input_file'))
        ac.argument('output', options_list=('--output_file'))
