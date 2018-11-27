# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import logging

def init_logging(filepath, level=logging.DEBUG):
    """
    Initialize the logging module for the application.

    :param filepath: path to the logfile
    """
    logger = logging.getLogger()
    logger.setLevel(level)

    # create a file handler for all levels
    fh = logging.FileHandler(filepath)
    fh.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # create a console handler for the error messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)
