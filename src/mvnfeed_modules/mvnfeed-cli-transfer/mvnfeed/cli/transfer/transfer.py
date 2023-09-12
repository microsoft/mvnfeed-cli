# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging
import os.path
import requests
import shutil
import xml.etree.ElementTree as ET
try:
    # Python 3
    from urllib.request import Request, urlopen
except ImportError:
    # Python 2
    from urllib2 import Request, urlopen
from .configuration import get_repository, get_stagedir, get_repository_shortname
from mvnfeed.cli.common.config import AUTHORIZATION, URL, AUTH_HEADER, AUTH_VALUE, load_config


def transfer_artifact(name, from_repo, to_repo, transfer_deps=False):
    """
    Transfers a single artifact.

    :param name: name of the artifact to download, following the group_id:artifact_id:version format
    :param from_repo: name of the source repository
    :param to_repo: name of the destination repository
    :param transfer_deps: True if the dependencies must be transferred
    """
    logging.info('transferring %s', name)

    config = load_config()
    from_repository = get_repository(config, from_repo)
    to_repository = get_repository(config, to_repo)
    stage_dir = get_stagedir(config)

    _transfer_single_artifact(name, from_repository, to_repository, stage_dir, transfer_deps)


def transfer_bulk(filename, from_repo, to_repo, transfer_deps=False):
    """
    Transfers artifacts from a file, one artifact per line.

    :param filename: name of the file containing the mvnfeed to upload
    :param from_repo: name of the source repository
    :param to_repo: name of the destination repository
    :param transfer_deps: True if the dependencies must be transferred
    """
    logging.info('transferring from file %s', filename)

    config = load_config()
    from_repository = get_repository(config, from_repo)
    to_repository = get_repository(config, to_repo)
    stage_dir = get_stagedir(config)

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip().rstrip()
            if line:
                _transfer_single_artifact(line, from_repository, to_repository, stage_dir, transfer_deps)


def _transfer_single_artifact(name, from_repository, to_repository, stage_dir, transfer_deps):
    logging.debug('download url: %s', from_repository[URL])
    logging.debug('upload url: %s', to_repository[URL])
    logging.debug('stage directory: %s', stage_dir)

    if not os.path.exists(stage_dir):
        raise ValueError('Output directory doesn\'t exist: ' + stage_dir)

    values = name.split(':')
    if len(values) == 3:
        group_id = values[0]
        artifact_name = values[1]
        # try to guess if we have a bom file
        if '-bom' in artifact_name:
            artifact_type = 'pom'
        else:
            artifact_type = 'jar'
        version = values[2]
        artifact_fullname = artifact_name + '-' + version
    elif len(values) == 4:
        group_id = values[0]
        artifact_name = values[1]
        artifact_type = values[2]
        version = values[3]
        artifact_fullname = artifact_name + '-' + version
    elif len(values) == 5:
        group_id = values[0]
        artifact_name = values[1]
        artifact_type = values[2]
        version = values[4]
        artifact_fullname = artifact_name + '-' + version + '-' + values[3]
    else:
        logging.warning('Artifact doesn\'t have correct format. Skipping ' + name)
        return

    artifact_path = group_id.replace('.', '/') + '/' + artifact_name + '/' + version

    if artifact_type in ['jar', 'war']:
        files2transfer = _java_artifacts(artifact_fullname, artifact_type, artifact_path, transfer_deps)
    else:
        files2transfer = _untyped_artifacts(artifact_fullname, artifact_type, artifact_path, transfer_deps)

    for file2transfer in files2transfer:
        artifact_relativepath = file2transfer['path'] + '/' + file2transfer['name']
        already_uploaded = _already_uploaded(to_repository, artifact_relativepath)

        if already_uploaded and not file2transfer['name'].endswith('.pom'):
            logging.info('%s already uploaded. Skipping', file2transfer['name'])
            continue

        # let's always download POM files in case we need to process the parent POM
        # once again or upload the children dependencies.
        outfile = os.path.join(stage_dir, file2transfer['name'])
        _download_file(from_repository, artifact_relativepath, outfile)
        if not os.path.exists(outfile):
            logging.info('%s was not downloaded. Skipping', outfile)
            if file2transfer['target']:
                logging.warning('%s was not found in the repository', file2transfer['name'])
            continue

        if not already_uploaded:
            _upload_file(to_repository, artifact_relativepath, outfile)

        if file2transfer['name'].endswith('.pom'):
            # a library will not be installed if it's parent pom.xml file
            # is not present in the repository, so let's transfer the
            # parent POM file but without transferring its dependencies.
            tree = ET.parse(outfile)
            parentNode = tree.getroot().find('{http://maven.apache.org/POM/4.0.0}parent')
            if parentNode is not None:
                parent_group_id = _findNodeValue(parentNode, 'groupId')
                parent_artifact_id = _findNodeValue(parentNode, 'artifactId')
                parent_version = _findNodeValue(parentNode, 'version')
                parent_path = parent_group_id.replace('.', '/') + '/' + parent_artifact_id + '/' + parent_version

                files2transfer.append(_pom_artifact(parent_artifact_id + '-' + parent_version, parent_path))

            if 'transfer_deps' not in file2transfer or not file2transfer['transfer_deps']:
                logging.info('not transferring dependencies from %s', file2transfer['name'])
                continue

            # try to download the dependencies
            dependenciesNode = tree.getroot().find('{http://maven.apache.org/POM/4.0.0}dependencies')
            if dependenciesNode is None:
                continue

            logging.debug("Downloading children")
            for dependencyNode in dependenciesNode.getchildren():
                dep_group_id = _findNodeValue(dependencyNode, 'groupId')
                dep_artifact_id = _findNodeValue(dependencyNode, 'artifactId')
                dep_version = _findNodeValue(dependencyNode, 'version')

                # we're only downloading `compile` versions. The user can
                # easily download other dependencies if needed.
                dep_scope = _findNodeValue(dependencyNode, 'scope')
                if dep_scope is not None and dep_scope != 'compile':
                    logging.info('not downloading %s:%s with scope %s', dep_group_id, dep_artifact_id, dep_scope)
                    continue

                # if no version has been defined, than it's getting potentially
                # tricky so let's just give up and let the user deal with it
                if dep_version is None:
                    logging.error('missing explicit version for %s:%s in %s. Skipping',
                                  dep_group_id, dep_artifact_id, file2transfer['name'])
                    continue

                # let's download the dependency
                artifact_fullname = dep_artifact_id + '-' + dep_version
                artifact_path = dep_group_id.replace('.', '/') + '/' + dep_artifact_id + '/' + dep_version
                files2transfer.extend(_java_artifacts(artifact_fullname, 'jar', artifact_path, transfer_deps))


# Definitions of the artifacts to download:
#  - name: name of the artifact
#  - path: full path of the artifact, will be prepended to the urls
#  - transfer_deps: true if the dependencies defined in the pom file must be tranferred
#  - target: true if definition was created for an artifact that was
#            explicitely requested. Used for logging purpose.

def _pom_artifact(artifact_fullname, artifact_path):
    return {
        'name': artifact_fullname + '.pom',
        'path': artifact_path,
        'transfer_deps': False,
        'target': False
    }


def _java_artifacts(artifact_fullname, artifact_type, artifact_path, transfer_deps):
    return [
        {
            'name': artifact_fullname + '.' + artifact_type,
            'path': artifact_path,
            'target': True
        },
        {
            'name': artifact_fullname + '.pom',
            'path': artifact_path,
            'transfer_deps': transfer_deps,
            'target': False
        },
        {
            'name': artifact_fullname + '-tests.jar',
            'path': artifact_path,
            'target': False
        },
        {
            'name': artifact_fullname + '-sources.jar',
            'path': artifact_path,
            'target': False
        },
        {
            'name': artifact_fullname + '-javadoc.jar',
            'path': artifact_path,
            'target': False
        }
    ]


def _untyped_artifacts(artifact_fullname, artifact_type, artifact_path, transfer_deps):
    return [
        {
            'name': artifact_fullname + '.' + artifact_type,
            'path': artifact_path,
            'transfer_deps': transfer_deps,
            'target': True
        },
        {
            'name': artifact_fullname + '.pom',
            'path': artifact_path,
            'transfer_deps': transfer_deps,
            'target': False
        }
    ]


def _findNodeValue(node, name):
    foundNode = node.find('{http://maven.apache.org/POM/4.0.0}' + name)
    if foundNode is None:
        return None
    return foundNode.text


def _download_file(from_repository, path, filename, length=16*1024):
    """
    Stores the path into the given filename.
    """
    if os.path.exists(filename):
        logging.debug('%s already downloaded', filename)

    if URL not in from_repository or not from_repository[URL]:
        raise ValueError('Repository missing url: ' + get_repository_shortname(from_repository))

    url = _append_url(from_repository[URL], path)
    logging.debug('downloading from %s', url)
    try:
        request = Request(url)
        if AUTHORIZATION in from_repository and from_repository[AUTHORIZATION]:
            logging.debug('authorization header added')
            request.add_header('Authorization', from_repository[AUTHORIZATION])
        elif AUTH_HEADER in from_repository and from_repository[AUTH_HEADER]:
            logging.debug('custom auth header added')
            request.add_header(from_repository[AUTH_HEADER], from_repository[AUTH_VALUE])
        else:
            logging.debug('no authorization configured')

        response = urlopen(request)
        with open(filename, 'wb') as file:
            shutil.copyfileobj(response, file, length)
    except Exception as ex:
        logging.debug('exception while downloading (expected): %s', ex)
        None


def _already_uploaded(to_repository, path):
    """
    Return True if the file was already uploaded.
    """
    if URL not in to_repository or not to_repository[URL]:
        raise ValueError('Repository missing upload url: ' + get_repository_shortname(to_repository))
    url = _append_url(to_repository[URL], path)

    if AUTHORIZATION in to_repository and to_repository[AUTHORIZATION]:
        logging.debug('authorization header added')
        headers = {'Authorization': to_repository[AUTHORIZATION]}
    elif AUTH_HEADER in to_repository and to_repository[AUTH_HEADER]:
        logging.debug('custom auth header added')
        headers = {to_repository[AUTH_HEADER]: to_repository[AUTH_VALUE]}
    else:
        logging.debug('no authorization configured')
        headers = {}

    try:
        response = requests.head(url, headers=headers)
        return response.ok
    except Exception as ex:
        logging.debug('exception while checking existence %s', ex)
        return False


def _upload_file(to_repository, path, filename):
    """
    Returns True if the file was uploaded
    """
    if not os.path.exists(filename):
        # we try to upload a file that was not downloaded (for example an artifact without
        # sources.) This is expected to happen and is not an error.
        logging.debug('missing file to upload, skipping %s', filename)
        return False

    if URL not in to_repository or not to_repository[URL]:
        raise ValueError('Repository missing upload url: ' + get_repository_shortname(to_repository))
    url = _append_url(to_repository[URL], path)

    logging.debug('uploading to ' + url)
    if AUTHORIZATION in to_repository and to_repository[AUTHORIZATION]:
        logging.debug('authorization header added')
        headers = {'Authorization': to_repository[AUTHORIZATION]}
    elif AUTH_HEADER in to_repository and to_repository[AUTH_HEADER]:
        logging.debug('custom auth header added')
        headers = {to_repository[AUTH_HEADER]: to_repository[AUTH_VALUE]}
    else:
        logging.debug('no authorization configured')
        headers = {}
    try:
        with open(filename, 'rb') as file:
            response = requests.put(url, files={filename: file}, headers=headers)
            if not response.ok:
                logging.error('error while uploading of %s: %s', path, response.text)
        return True
    except Exception as ex:
        logging.warn('exception while uploading %s', ex)
        return False


def _append_url(base_url, fragment):
    return base_url + fragment if base_url.endswith('/') else base_url + '/' + fragment
