# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.commands import CommandGroup


def load_transfer_commands(cli_command_loader):
    with CommandGroup(cli_command_loader, 'artifact', 'mvnfeed.cli.transfer.{}') as g:
        g.command('transfer', 'transfer#transfer_artifact')
        g.command('bulk-transfer', 'transfer#transfer_bulk')

    with CommandGroup(cli_command_loader, 'config stage_dir', 'mvnfeed.cli.transfer.{}') as g:
        g.command('set', 'configuration#set_stagedir')
        g.command('view', 'configuration#view_stagedir')

    with CommandGroup(cli_command_loader, 'config repo', 'mvnfeed.cli.transfer.{}') as g:
        g.command('add', 'configuration#add_repository')
        g.command('delete', 'configuration#delete_repository')
        g.command('list', 'configuration#list_repositories')

    with CommandGroup(cli_command_loader, 'input', 'mvnfeed.cli.transfer.{}') as g:
        g.command('cleanup', 'cleanup#cleanup_file')
