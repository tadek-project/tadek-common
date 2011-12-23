################################################################################
##                                                                            ##
## This file is a part of TADEK.                                              ##
##                                                                            ##
## TADEK - Test Automation in a Distributed Environment                       ##
## (http://tadek.comarch.com)                                                 ##
##                                                                            ##
## Copyright (C) 2011 Comarch S.A.                                            ##
## All rights reserved.                                                       ##
##                                                                            ##
## TADEK is free software for non-commercial purposes. For commercial ones    ##
## we offer a commercial license. Please check http://tadek.comarch.com for   ##
## details or write to tadek-licenses@comarch.com                             ##
##                                                                            ##
## You can redistribute it and/or modify it under the terms of the            ##
## GNU General Public License as published by the Free Software Foundation,   ##
## either version 3 of the License, or (at your option) any later version.    ##
##                                                                            ##
## TADEK is distributed in the hope that it will be useful,                   ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
## GNU General Public License for more details.                               ##
##                                                                            ##
## You should have received a copy of the GNU General Public License          ##
## along with TADEK bundled with this file in the file LICENSE.               ##
## If not, see http://www.gnu.org/licenses/.                                  ##
##                                                                            ##
## Please notice that Contributor Agreement applies to any contribution       ##
## you make to TADEK. The Agreement must be completed, signed and sent        ##
## to Comarch before any contribution is made. You should have received       ##
## a copy of Contribution Agreement along with TADEK bundled with this file   ##
## in the file CONTRIBUTION_AGREEMENT.pdf or see http://tadek.comarch.com     ##
## or write to tadek-licenses@comarch.com                                     ##
##                                                                            ##
################################################################################

import os
import logging
import logging.handlers

import config
import settings
import utils

# Configuration
_CONFIG_NAME = "log"
_CONFIG_FILE_HANDLER = "FileHandler"
_CONFIG_STREAM_HANDLER = "StreamHandler"

_LOG_DIR_NAME = "log"
_LOG_FILE_EXT = ".log"

# Default logger attributes
_DEFAULT_MAXBYTES = 2097152 # 2 MB
_DEFAULT_BACKUPS = 10
_DEFAULT_LEVEL = logging.WARNING
_DEFAULT_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


class FakeLogger(object):
    '''
    A class of fake loggers.
    '''
    def __getattr__(self, name):
        return self.log

    def log(self, *args, **kwargs):
        pass


def getLogger(name=None):
    '''
    Returns a logger of the given name with two handlers: 
     - logging.handlers.RotatingFileHandler,
     - logging.StreamHandler.
    
    :param name: A name of the Logger object
    :type name: string
    :return: A logger object
    :rtype: logging.Logger
    '''
    name = name or config.getProgramName()
    if not name:
        return FakeLogger()
    logdir = utils.ensureUserDir(_LOG_DIR_NAME)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # RotatingFileHandler
    logFile = os.path.join(logdir, name + _LOG_FILE_EXT)
    bytes = settings.get(_CONFIG_NAME, _CONFIG_FILE_HANDLER, "maxbytes",
                         _DEFAULT_MAXBYTES, force=True).getInt()
    backups = settings.get(_CONFIG_NAME, _CONFIG_FILE_HANDLER, "backups",
                           _DEFAULT_BACKUPS, force=True).getInt()
    level = settings.get(_CONFIG_NAME, _CONFIG_FILE_HANDLER, "level", 
                         _DEFAULT_LEVEL, force=True).getInt()
    format = settings.get(_CONFIG_NAME, _CONFIG_FILE_HANDLER, "format",
                          _DEFAULT_FORMAT, force=True).get()
    handler = logging.handlers.RotatingFileHandler(logFile, maxBytes=bytes,
                                                   backupCount=backups)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    # StreamHandler
    level = settings.get(_CONFIG_NAME, _CONFIG_STREAM_HANDLER, "level",
                         _DEFAULT_LEVEL, force=True).getInt()
    format = settings.get(_CONFIG_NAME, _CONFIG_STREAM_HANDLER, "format",
                          _DEFAULT_FORMAT, force=True).get()
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    return logger

_handler = getLogger()

#: Function to log DEBUG information
debug = _handler.debug
#: Function to log INFO information
info = _handler.info
#: Function to log WARNING information
warning = _handler.warning
#: Function to log ERROR information
error = _handler.error
#: Function to log ERROR information with traceback
exception = _handler.exception
#: Function to log CRITICAL information
critical = _handler.critical

del _handler
del config
del logging
del os

