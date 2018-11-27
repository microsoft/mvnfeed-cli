import knack
from mvnfeed.cli.transfer.commands import load_transfer_commands
from mvnfeed.cli.transfer.arguments import load_transfer_arguments

class MvnFeedCommandsLoader(knack.commands.CLICommandsLoader):
    def load_command_table(self, args):
        load_transfer_commands(self)
        return super(MvnFeedCommandsLoader, self).load_command_table(args)

    def load_arguments(self, command):
        load_transfer_arguments(self)
        super(MvnFeedCommandsLoader, self).load_arguments(command)