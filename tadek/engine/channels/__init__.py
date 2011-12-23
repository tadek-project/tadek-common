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

from tadek.core import settings
from tadek.core import utils

__all__ = ["TestResultChannel", "TestResultFileChannel",
           "TestResultChannelError", "register", "add", "remove", "get"]

CONFIG_NAME = "channels"

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TestResultChannelError(Exception):
    '''
    A base exception class for result channels errors.
    '''
    def __init__(self, message):
        Exception.__init__(self, message)


class TestResultChannel:
    '''
    A base class for result channels.
    '''
    #: A flag for determining if a channel is active
    _active = False

    def __init__(self, name, enabled=True, verbose=False, **params):
        self.name = name
        self._enabled = enabled
        self._verbose = verbose

    def isEnabled(self):
        '''
        Returns True if the channel is enabled currently, False otherwise.

        :return: True if the channel is enabled, False otherwise
        :rtype: boolean
        '''
        return bool(self._enabled)

    def setEnabled(self, enabled):
        '''
        Sets if the channel should be enabled or not.

        :param enabled: True if the channel is enabled, False otherwise
        :type enabled: boolean
        '''
        self._enabled = enabled

    def isVerbose(self):
        '''
        Returns True if the channel is in verbose mode currently,
        False otherwise.

        :return: True if the channel is in verbose mode, False otherwise
        :rtype: boolean
        '''
        return bool(self._verbose)

    def setVerbose(self, verbose):
        '''
        Sets if the channel should be in verbose mode or not.

        :param verbose: True if the channel is in verbose mode, False otherwise
        :type verbose: boolean
        '''
        self._verbose = verbose

    def isActive(self):
        '''
        Returns True if the channel is active (its startTest() or stopTest()
        was called at least once) currently, False otherwise.

        :return: True if the channel is active, False otherwise
        :rtype: boolean
        '''
        return self._active

    def setActive(self, active):
        '''
        Sets if the channel should be active or not.

        :param active: True if the channel should is active, False otherwise
        :type active: boolean
        '''
        self._active = active

    def start(self, result):
        '''
        Used to signal begining of tests execution.
        This method is intended to be overridden by subclasses.

        :param result: A test result container
        :type result: TestResultContainer
        '''
        pass

    def stop(self):
        '''
        Used to signal end of tests execution.
        This method is intended to be overridden by subclasses.
        '''
        pass

    def startTest(self, result, device):
        '''
        Processes a test start execution.
        This method is intended to be overridden by subclasses.

        :param result: A test result to process
        :type result: TestResultBase
        :param device: A related device execution result
        :type device: DeviceExecResult
        '''
        self.setActive(True)

    def stopTest(self, result, device):
        '''
        Processes a test stop execution.
        This method is intended to be overridden by subclasses.

        :param result: A test result to process
        :type result: TestResultBase
        :param device: A related device execution result
        :type device: DeviceExecResult
        '''
        self.setActive(True)


class TestResultFileChannel(TestResultChannel):
    '''
    A base class for readable result channels.
    '''
    # The default channel target file name
    _DEFAULT_FILE_NAME = "tadek_results"
    # The default channel target file extension
    _DEFAULT_FILE_EXT = ''

    # A path to the channel target file
    _filePath = None
    # An extension of the channel target file
    _fileExt = None

    def __init__(self, name, filename=None, extension=None,
                       dirname='',  unique=True, **params):
        TestResultChannel.__init__(self, name, **params)
        self._fileName = filename or self._DEFAULT_FILE_NAME
        if not self.fileExt():
            if extension is None:
                extension = (os.path.splitext(str(filename))[1]
                             or self._DEFAULT_FILE_EXT)
            self.setFileExt(extension)
        self._dirName = dirname
        self._unique = unique

    def fileExt(self):
        '''
        Return extension of file name which can be used to filter
        possible files to load.

        :return: The file extension
        :rtype: string
        '''
        return str(self._fileExt)

    def setFileExt(self, ext):
        '''
        Return extension of file name which can be used to filter
        possible files to load.

        :return: The file extension
        :rtype: string
        '''
        self._fileExt = ext

    def filePath(self):
        '''
        Gets a path to the channel target file.
        '''
        return self._filePath

    def setFilePath(self, path):
        '''
        Sets a path to the channel target file.
        '''
        self._filePath = path

    def start(self, result):
        '''
        Sets a path to the channel target file.

        :param result: A test result container
        :type result: TestResultContainer
        '''
        TestResultChannel.start(self, result)
        if isinstance(self._fileName, (basestring, settings.SettingsOption)):
            fileName, fileExt = os.path.splitext(str(self._fileName))
            if not fileExt:
                fileExt = str(self._fileExt)
            fileName += fileExt
            if bool(self._unique):
                fileName = utils.uniqueFile(fileName)
            dirName = os.path.abspath(str(self._dirName))
            self.setFilePath(os.path.join(dirName, fileName))
        else:
            self.setFilePath(self._fileName)

    def read(self, file):
        '''
        Reads test results from the given file.
        This function should be reimplemented in derived classes.

        :param file: File from which a channel should load results
        :type file: string or file object
        '''
        self.setFilePath(file)


class CoreDumpsChannel:
    '''
    A channel-like class for caching core dumps.
    '''
    name = "coredumps"

    def __init__(self):
        section = settings.get(CONFIG_NAME, self.name, force=True)
        self._enabled = section["enabled"]
        self._dirs = section["dirs"]
        self._pattern = section["pattern"]
        self._recursive = section["recursive"]
        self._links = section["links"]

    def isEnabled(self):
        '''
        Returns True if the core dumps channel is enabled, False otherwise.

        :return: True if the channel is enabled, False otherwise
        :rtype: boolean
        '''
        return bool(self._enabled)

    def setEnabled(self, enabled):
        '''
        Sets if the core dumps channel should be enabled.

        :param enabled: True if the channel should be enabled, False otherwise
        :type enabled: boolean
        '''
        self._enabled = enabled

    def _cache(self, device):
        '''
        Gets a core dumps cache for the given device.
        '''
        cache = self._caches.get(id(device))
        if cache is None:
            self._caches[id(device)] = cache = {}
            self._update(device, cache, take=True)
        return cache

    def _update(self, device, cache, take=False):
        '''
        Updates the given core dumps cache using the specified device.
        '''
        coreDumps = []
        for dirpath in set(self._dirs):
            status, cores = device.extension("dirfiles",
                                           path=str(dirpath),
                                           pattern=str(self._pattern),
                                           recursive=bool(self._recursive),
                                           links=bool(self._links))
            if status:
                coreDumps.extend(cores)
        cores = cache.keys()
        for core in coreDumps:
            found = False
            while core in cores:
                c = cores.pop(cores.index(core))
                if core.mtime == c.mtime and core.size == c.size:
                    found = True
                    break
            if not found:
                cache[core] = take

    def start(self, result):
        '''
        Intializes the core dumps caching.
        '''
        self._caches = {}

    def stop(self):
        '''
        Closes the internal core dumps caches.
        '''
        for cache in self._caches.itervalues():
            for core in cache:
                cache[core] = True

    def startTest(self, result, device):
        '''
        Gets a list of all not taken yet cores dumped on the given device.
        '''
        cache = self._cache(device)
        self._update(device, cache)
        result.cores = [core for core, taken in cache.iteritems() if not taken]

    def stopTest(self, result, device):
        '''
        Takes a list of all available (not taken yet) core dumps stored
        in a cache associated with the device excluding the given list.
        '''
        exclude = [id(core) for core in result.cores]
        result.cores = []
        cache = self._cache(device)
        self._update(device, cache)
        for core, taken in cache.iteritems():
            if taken or id(core) in exclude:
                continue
            cache[core] = True
            result.cores.append(core)


# A cache for registered channel classes
_registry = {}

def register(cls):
    '''
    Registers the given channel class.
    This function should be called from channel class module
    in order to use channels of this class as a result channel.

    If channel class is not a subclass of TestResultChannel
    TypeError exception is raised.
    When channel class is already registered return False,
    otherwise return True


    :param cls: Channel class to register
    :type cls: TestResultChannel
    :return: True or False
    :rtype: bool
    '''
    if not issubclass(cls, TestResultChannel):
        raise TypeError("Invalid channel class: %s" % cls.__name__)
    if cls.__name__ in _registry:
        return False
    _registry[cls.__name__] = cls
    return True

# A cache for predefined channels
_cache = {}

def add(cls, name, **params):
    '''
    Adds the given predefined channel.
    If channel class is not a subclass of TestResultChannel
    TypeError exception is raised.
    If channel is already added ValueError exception is raised.

    :param channel: Channel
    :type channel: TestResultChannel subclass instance
    '''
    if isinstance(cls, basestring):
        if cls in _registry:
            cls = _registry[cls]
        else:
            raise TypeError("Invalid channel class name: %s" % cls)
    elif not issubclass(cls, TestResultChannel):
        raise TypeError("Invalid channel class: %s" % cls.__name__)
    if name in _cache:
        raise ValueError("Channel with such a name already exists: %s" % name)
    _cache[name] = (cls, params)

def remove(name):
    '''
    Removes a predefined channel of the given name.

    :param name: Name of channel to remove
    :type name: string
    :return: Removed channel
    :rtype: TestResultChannel
    '''
    return _cache.pop(name, None)


_initialized = False

def _package():
    '''
    Gets an initialized package with result channel modules.
    '''
    global _initialized
    package = sys.modules[__name__]
    if not _initialized:
        _initialized = True
        userdir = utils.ensureUserDir(__name__.rsplit('.', 1)[1])
        if userdir:
            package.__path__.append(userdir)
    return package

def _get():
    '''
    Gets channels defined in the settings.
    '''
    channels = []
    modules = iter(utils.packageModules(_package()))
    for name in settings.get(CONFIG_NAME, force=True):
        if name in _cache:
            # A name of the channel conflicts with some predefined channel
            continue
        params = {}
        section = settings.get(CONFIG_NAME, name, force=True)
        for option in section:
            params[option.name().lower()] = option
        clsname = params.pop("class", None)
        if clsname is None:
            continue
        clsname = clsname.get()
        while clsname not in _registry:
            try:
                while not utils.importModule(modules.next()):
                    pass
            except StopIteration:
                break
        if clsname in _registry:
            channels.append(_registry[clsname](name, **params))
    return channels

def get():
    '''
    Gets a list of channels manually added and channels defined in settings.

    :return: A list of channels
    :rtype: list
    '''
    channels = []
    for name, (cls, params) in _cache.iteritems():
        channels.append(cls(name, **params))
    channels.extend(_get())
    return channels

