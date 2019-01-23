from __future__ import print_function

from knack import CLI
from mvnfeed.cli.common.config import GLOBAL_CONFIG_DIR, CLI_ENV_VARIABLE_PREFIX, load_config
from mvnfeed.cli.common.logmodule import init_logging
from .mvnfeed_help import MvnFeedHelp
from .mvnfeed_commands import MvnFeedCommandsLoader

CLI_NAME = "mvnfeed"
CLI_PACKAGE_NAME = 'mvnfeed-cli'
COMPONENT_PREFIX = 'mvnfeed-cli-'


class MvnFeedCLI(CLI):
    def __init__(self):
        super(MvnFeedCLI, self).__init__(cli_name=CLI_NAME,
                                         config_dir=GLOBAL_CONFIG_DIR,
                                         config_env_var_prefix=CLI_ENV_VARIABLE_PREFIX,
                                         commands_loader_cls=MvnFeedCommandsLoader,
                                         help_cls=MvnFeedHelp)
        self.args = None
        load_config()
        init_logging('mvnfeed.log')
