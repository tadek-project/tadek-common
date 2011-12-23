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
import sys

from tadek import models
from tadek import teststeps
from tadek import testcases
from tadek import testsuites
from tadek.core import locale
from tadek.core.structs import ErrorBox

_DIRS_MAP = {
    "models": models,
    "teststeps": teststeps,
    "testcases": testcases,
    "testsuites": testsuites
}

_LOCALE_DIR = "locale"

class NameConflictError(Exception):
    '''
    Raised when a name conflict module takes place inside some.
    '''
    def __init__(self, module, name):
        Exception.__init__(self, '.'.join([module.__name__, name]))


def add(path, enabled=True):
    '''
    Adds a location of models and test cases specified by the path.

    :param path: A path to a location directory
    :type path: string
    :param enabled: True if an added location should be enabled, False otherwise
    :type enabled: boolean
    '''
    path = os.path.abspath(path)
    if path in _cache:
        return None
    _cache[path] = enabled
    if enabled:
        return enable(path)
    return []

def remove(path):
    '''
    Removes a location of models and test cases specified by the path.

    :param path: A path to a location directory
    :type path: string
    '''
    path = os.path.abspath(path)
    if path not in _cache:
        return
    disable(path)
    del _cache[path]

def get(enabled=None):
    '''
    Gets a list of all locations.
    '''
    if enabled is None:
        return _cache.keys()
    elif enabled:
        return [path for path in _cache if _cache[path]]
    else:
        return [path for path in _cache if not _cache[path]]

def enable(path):
    '''
    Enables a location of models and test cases specified by the path.

    :param path: A path to a location directory
    :type path: string
    '''
    path = os.path.abspath(path)
    if path not in _cache:
        return None
    _cache[path] = True
    errors = []
    for dirname, module in _DIRS_MAP.iteritems():
        errors.extend(_addModuleDir(module, os.path.join(path, dirname)))
    # Add a corresponding locale
    locale.add(os.path.join(path, _LOCALE_DIR))
    if errors:
        disable(path)
    return errors

def disable(path):
    '''
    Disables a location of models and test cases specified by the path.

    :param path: A path to a location directory
    :type path: string
    '''
    path = os.path.abspath(path)
    for dirname, module in _DIRS_MAP.iteritems():
        _removeModuleDir(module, os.path.join(path, dirname))
    # Remove a corresponding locale
    locale.remove(os.path.join(path, _LOCALE_DIR))
    _cache[path] = False

def clear():
    '''
    Clears imported modules from all locations.
    '''
    for module in _DIRS_MAP.itervalues():
        _clearModule(module)

# A locations cache
_cache = {}


# Location directories oriented functions:

def getModels():
    '''
    Gets a dictionary containing all currently avalaible models modules.

    :return: A dictionary with models modules
    :rtype: dictionary
    '''
    content = _getModuleContent(models)
    content.pop("__init__", None)
    return content

def getSteps():
    '''
    Gets a dictionary containing all currently avalaible root test steps
    modules.

    :return: A dictionary with test steps modules
    :rtype: dictionary
    '''
    content = _getModuleContent(teststeps)
    content.pop("__init__", None)
    return content

def getCases():
    '''
    Gets a dictionary containing all currently avalaible root test cases
    modules.

    :return: A dictionary with test cases modules
    :rtype: dictionary
    '''
    content = _getModuleContent(testcases)
    content.pop("__init__", None)
    return content

def getSuites():
    '''
    Gets a dictionary containing all currently avalaible root test suites
    modules.

    :return: A dictionary with test suites modules
    :rtype: dictionary
    '''
    content = _getModuleContent(testsuites)
    content.pop("__init__", None)
    return content


_MODULE_EXTS = (".py", ".pyc", ".pyo")

def _getDirContent(dir, package=None):
    '''
    Gets content of the given directory.
    '''
    content = {}
    for file in sorted(os.listdir(dir)):
        name = None
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            name, ext = os.path.splitext(file)
            if ext not in _MODULE_EXTS or (package and name == "__init__"):
                continue
            name = '.'.join([package, name]) if package else name
        elif os.path.isdir(path):
            pkg = False
            for ext in _MODULE_EXTS:
                if os.path.exists(os.path.join(path, "__init__" + ext)):
                    pkg = True
                    break
            if not pkg:
                continue
            name = '.'.join([package, file]) if package else file
            content.update(_getDirContent(path, name))
            path = os.path.join(path, "__init__" + ext)
        if name and name not in content:
            content[name] = path
    return content

def _getModuleContent(module):
    '''
    Gets content of the given module from the specified directory.
    '''
    content = {}
    for path in module.__path__:
        for name, path in _getDirContent(path).iteritems():
            if name not in content:
                content[name] = path
    return content

def _addModuleDir(module, path):
    '''
    Adds a directory of the given path to the specified module object.
    '''
    errors = []
    if not os.path.isdir(path) or path is module.__path__:
        return errors
    content = _getModuleContent(module)
    for name in _getDirContent(path):
        try:
            if name in content:
                raise NameConflictError(module, name)
        except NameConflictError:
            errors.append(ErrorBox(name=name, path=path))
    if not errors:
        module.__path__.append(path)
    return errors

def _clearModule(module, path=None):
    '''
    Clears the imported module.
    '''
    patterns = []
    if not path:
        patterns.append(module.__name__ + '.')
    elif path in module.__path__:
        for name in _getDirContent(path):
            patterns.append('.'.join([module.__name__, name]))
    for name in sys.modules.keys():
        for pattern in patterns:
            if pattern in name:
                del sys.modules[name]
                break

def _removeModuleDir(module, path):
    '''
    Removes a directory of the given path from the specified module object.
    '''
    if path not in module.__path__ or path == module.__path__[0]:
        return
    _clearModule(module, path)
    module.__path__.remove(path)

