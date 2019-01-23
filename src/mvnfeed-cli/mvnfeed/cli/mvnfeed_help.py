from knack.help import CLIHelp
from mvnfeed.cli.common.version import VERSION


class MvnFeedHelp(CLIHelp):
    def __init__(self, cli_ctx=None):
        # import command group help
        import mvnfeed.cli.transfer._help  # noqa
        super(MvnFeedHelp, self).__init__(cli_ctx=cli_ctx,
                                          welcome_message=WELCOME_MESSAGE)


WELCOME_MESSAGE = """MvnFeed CLI {}

Use `mvnfeed -h` to see available commands.

Available commands:""".format(VERSION)
