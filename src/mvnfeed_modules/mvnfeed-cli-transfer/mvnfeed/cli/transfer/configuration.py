# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
import getpass
from mvnfeed.cli.common.config import REPOSITORY, AUTHORIZATION, DOWNLOAD_URL, UPLOAD_URL, repo_section_name, load_config, save_config

STAGE_DIR_CONFIGNAME = 'stage_dir'

def set_stagedir(path):
    """
    Sets the output directory where dependencies will be staged.

    :param path: path where the downloaded mvnfeed will be staged
    """
    config = load_config()
    if 'general' not in config:
        config.add_section('general')

    config.set('general', STAGE_DIR_CONFIGNAME, path)
    save_config(config)


def view_stagedir():
    """
    Views the output directory where mvnfeed will be staged.
    """
    config = load_config()
    if 'general' not in config:
        return ''

    return config.get('general', STAGE_DIR_CONFIGNAME)


def add_repository(name, username, upload_url=None, download_url=None):
    """
    Adds an external Maven repository.

    :param name: internal name of the repository
    :param username: name of the user for the basic authentication to the repository
    :param upload_url: url for uploading the mvnfeed
    :param download_url: url for downloading the mvnfeed
    """
    if username is None:
        raise ValueError('Username must be defined')
    if upload_url is None and download_url is None:
        raise ValueError('At least one of upload_url or download_url must be defined')

    password = getpass.getpass()
    encoded = base64.b64encode((username + ':' + password).encode('utf-8'))
    authorization = 'Basic ' + encoded.decode('utf-8')

    config = load_config()
    config[repo_section_name(name)] = {
        DOWNLOAD_URL: _default_value(download_url),
        UPLOAD_URL: _default_value(upload_url),
        AUTHORIZATION: _default_value(authorization)
    }
    save_config(config)


def delete_repository(name):
    """
    Deletes a configured Maven repository.
    """
    config = load_config()
    section_name = repo_section_name(name)
    if config.has_section(section_name):
        config.remove_section(section_name)
        save_config(config)


def list_repositories():
    """
    Lists the configured Maven repositories.
    """
    config = load_config()
    for section in config.sections():
        if section.startswith(REPOSITORY):
            repo = config[section]
            print(section[11:])
            if UPLOAD_URL in repo:
                print('  upload url  : ' + repo[UPLOAD_URL])
            if DOWNLOAD_URL in repo and repo[DOWNLOAD_URL]:
                print('  download url: ' + repo[DOWNLOAD_URL])


def get_repository(config, name):
    if config is None:
        config = load_config()
    section_name = repo_section_name(name)
    if not config.has_section(section_name):
        raise ValueError('No repository found: ' + name)
    return config[section_name]


def get_repository_shortname(repository):
    return repository.name[11:]


def get_stagedir(config):
    """
    Returns the value of the stage directory.
    """
    if config is None:
        config = load_config()
    if 'general' not in config:
        return None

    return config.get('general', STAGE_DIR_CONFIGNAME)


def _default_value(input):
    if input is None:
        return ''
    return input