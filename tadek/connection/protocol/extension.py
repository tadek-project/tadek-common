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

import sys

import message
from tadek.core import utils

__all__ = ["getExtension", "getExtensions"]

class UnsupportedProtocolExtensionError(Exception):
    '''
    A class of exceptions raised when some protocol extensions are not supported.
    '''
    # Message format
    _MSG_FORMAT = "Protocol extension is not supported: %s"

    def __init__(self, name):
        Exception.__init__(self, self._MSG_FORMAT % name)
        self.name = name


class ProtocolExtensionConflictError(Exception):
    '''
    A class of exceptions raised when a protocol extension class is in conflict
    with other.
    '''
    # Message format
    _MSG_FORMAT = "Protocol extension already registered: %s"

    def __init__(self, name):
        Exception.__init__(self, self._MSG_FORMAT % name)
        self.name = name


# The protocol extension class registry
_registry = {}

class MetaProtocolExtension(type):
    '''
    A meta class for protocol extensions.
    '''
    def __init__(cls, name, bases, attrs):
        if cls.name:
            if cls.name in _registry:
                raise ProtocolExtensionConflictError(cls.name)
            # Register request and response for the protocol extension
            message.registerRequest(message.MSG_TARGET_EXTENSION, cls.name,
                                    **(cls.requestParams or {}))
            message.registerResponse(message.MSG_TARGET_EXTENSION, cls.name,
                                     **(cls.responseParams or {}))
            # Register the protocol extension class
            _registry[cls.name] = cls


class ProtocolExtension:
    '''
    A base class for protocol extensions.
    '''
    __metaclass__ = MetaProtocolExtension

    #: A name of the protocol extension
    name = None
    #: A list of request parameters required by the protocol extension
    requestParams = None
    #: A list of response parameters required by the protocol extension
    responseParams = None

    def request(self, **params):
        '''
        Processes the given parameters just before sending a request.
        '''
        return params

    def response(self, **params):
        '''
        Processes the given request parameters just before sending a response.
        '''
        return True, {}


_loaded = False

def _loadExtensions():
    '''
    Loads all modules with protocol extensions.
    '''
    global _loaded
    _loaded = True
    name = __name__.rsplit('.', 1)[0]
    package = sys.modules[name]
    userdir = utils.ensureUserDir(name.rsplit('.', 1)[1])
    if userdir and userdir not in package.__path__:
        package.__path__.append(userdir)
    for module in utils.packageModules(package):
        if not utils.importModule(module):
            # TODO: Log the import error?
            pass

def getExtension(name):
    '''
    Gets an instance of a protocol extension of the given name.
    '''
    if not _loaded:
        _loadExtensions()
    try:
        return _registry[name]()
    except KeyError:
        raise UnsupportedProtocolExtensionError(name)

def getExtensions():
    '''
    Gets a list of names of all available protocol extensions.
    '''
    if not _loaded:
        _loadExtensions()
    return _registry.keys()

