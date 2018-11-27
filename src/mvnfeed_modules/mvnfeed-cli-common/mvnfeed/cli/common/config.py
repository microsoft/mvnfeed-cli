# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import configparser

CLI_ENV_VARIABLE_PREFIX = 'MVNFEED_'
CONFIG_FILENAME = 'mvnfeed.ini'

REPOSITORY = 'repository.'
DOWNLOAD_URL = 'download_url'
UPLOAD_URL = 'upload_url'
AUTHORIZATION = 'authorization'

def _get_config_dir():
    codegen_config_dir = os.getenv('MVNFEED_CONFIG_DIR', None) or os.path.expanduser(os.path.join('~', '.mvnfeed'))
    if not os.path.exists(codegen_config_dir):
        os.makedirs(codegen_config_dir)
    return codegen_config_dir

GLOBAL_CONFIG_DIR = _get_config_dir()


def load_config():
    """
    Returns the application configuration and create if it doesn't exist.
    """
    filename = os.path.join(_get_config_dir(), CONFIG_FILENAME)
    if os.path.exists(filename):
        config = configparser.ConfigParser()
        config.read(filename)
        return config

    config = configparser.ConfigParser()

    config[repo_section_name('central')] = {
        DOWNLOAD_URL: 'https://repo.maven.apache.org/maven2/'
    }
    config[repo_section_name('jcenter')] = {
        DOWNLOAD_URL: 'http://jcenter.bintray.com'
    }
    config[repo_section_name('jboss')] = {
        DOWNLOAD_URL: 'https://repository.jboss.org/nexus/content/repositories/releases/'
    }
    config[repo_section_name('clojars')] = {
        DOWNLOAD_URL: 'https://repo.clojars.org/'
    }
    config[repo_section_name('atlassian')] = {
        DOWNLOAD_URL: 'https://packages.atlassian.com/maven/public'
    }
    config[repo_section_name('google')] = {
        DOWNLOAD_URL: 'https://maven.google.com/'
    }

    save_config(config, filename)
    return config


def repo_section_name(name):
    return REPOSITORY + name


def save_config(config, filename=None):
    if filename is None:
        filename = os.path.join(_get_config_dir(), CONFIG_FILENAME)
    with open(filename, 'w') as config_file:
        config.write(config_file)
