################################################################################
##                                                                            ##
## This file is a part of TADEK.                                              ##
##                                                                            ##
## TADEK - Test Automation in a Distributed Environment                       ##
## (http://tadek.comarch.com)                                                 ##
##                                                                            ##
## Copyright (C) 2011,2012 Comarch S.A.                                       ##
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
import shutil
import ConfigParser

#import tadek

# The project name
NAME = "tadek"

# The version number
VERSION = "1.0.0"

# The version string
VERSION_STRING = "%%prog (TADEK) version %s" % VERSION

# A directory with project data
DATA_DIR = "data"

if os.path.isdir(os.path.join(os.path.pardir, DATA_DIR)):
    # Source
    DATA_DIR = os.path.join(os.path.pardir, DATA_DIR)
    CONF_DIR = os.path.join(DATA_DIR, "config")
    DOC_DIR = os.path.join(DATA_DIR, "doc")
elif os.name == "nt":
    # Windows
    DATA_DIR = os.path.join(os.getenv("PROGRAMFILES", ''), NAME.upper())
    CONF_DIR = os.path.join(DATA_DIR, "config")
    DOC_DIR = os.path.join(DATA_DIR, "doc")
elif os.name == "posix":
    # POSIX
    DATA_DIR = os.path.join("/usr/share", NAME)
    CONF_DIR = os.path.join("/etc", NAME)
    DOC_DIR = os.path.join("/usr/share/doc", NAME)
else:
    if os.path.isdir(DATA_DIR):
        DATA_DIR = os.path.abspath(DATA_DIR)
    CONF_DIR = os.path.join(DATA_DIR, "config")
    DOC_DIR = os.path.join(DATA_DIR, "doc")

# A user directory for project data
if os.name == "nt":
    # Windows
    USER_DIR = os.path.join(os.getenv("appdata", ''), NAME)
else:
    # POSIX
    USER_DIR = os.path.join(os.getenv("HOME", ''), '.' + NAME)

# Configuration constants
_CONF_FILE_EXT = ".conf"
_CONF_COMMON_NAME = "common"
# A root directory for user configuration
_USER_CONF_DIR = os.path.join(USER_DIR, "config")

# A current run program name
_programName = None

def getProgramName():
    '''
    Gets a name of the current program.

    :return: A name of the current program
    :rtype: string
    '''
    global _programName
    return _programName

def setProgramName(name):
    '''
    Sets a name of the current program.

    :param name: A name of current program
    :type name: string
    '''
    global _programName, _configDirs
    _programName = name
    _configDirs = None
    reload()


class Config(object):
    '''
    A class for managing configuration files in .ini format.
    '''
    # The items separator in lists
    _LIST_ITEM_SEPARATOR = ','

    def __init__(self, filename, dirname):
        self.file = os.path.join(_USER_CONF_DIR, dirname, filename)
        self._readbuf = ConfigParser.ConfigParser()
        self._readbuf.read([os.path.join(CONF_DIR, dirname, filename),
                            self.file])
        self._writebuf = ConfigParser.ConfigParser()
        self._writebuf.read(self.file)

    def update(self, file):
        '''
        Updates the configuration using the given file.

        :param file: A file path
        :type file: string
        '''
        #self.file = file
        self._readbuf.read(file)
        self._writebuf.read(file)

    def hasSection(self, section):
        '''
        Checks if the given section exists in the configuration.

        :param section: A name of the section
        :type section: string
        :return: True if the section exists, False otherwise
        :rtype: boolean
        '''
        return self._readbuf.has_section(section)

    def getSections(self):
        '''
        Gets a list of available sections in the configuration.

        :return: A list of section names
        :rtype: list
        '''
        return self._readbuf.sections()

    def addSection(self, section):
        '''
        Adds the given section to the configuration if the section does not
        exist yet.

        :param section: A name of the adding section
        :type section: string
        '''
        if not self.hasSection(section):
            self._readbuf.add_section(section)
            self._writebuf.add_section(section)

    def removeSection(self, section):
        '''
        Removes the given section from the configuration if the section already
        exists.

        :param section: A name of the removing section
        :type section: string
        '''
        if self.hasSection(section):
            self._readbuf.remove_section(section)
            if self._writebuf.has_section(section):
                self._writebuf.remove_section(section)

    def hasOption(self, section, option):
        '''
        Checks if the given option exists in the specified configuration
        section.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :return: True if the option exist, False otherwise
        :rtype: boolean
        '''
        return self._readbuf.has_option(section, option)

    def getOptions(self, section):
        '''
        Gets a list of available option in the given configuration section.

        :param section: A name of the section
        :type section: string
        :return: A list of option names
        :rtype: list
        '''
        if self.hasSection(section):
            return self._readbuf.options(section)
        return []

    def addOption(self, section, option):
        '''
        Adds the given option to the specified configuration section.

        :param section: A name of the section
        :type section: string
        :param option: A name of the adding option
        :type option: string
        '''
        if not self.hasSection(section):
            self.addSection(section)
        if not self.hasOption(section, option):
            self.setValue(section, option, '')

    def removeOption(self, section, option):
        '''
        Removes the given option from the specified configuration section.

        :param section: A name of the section
        :type section: string
        :param option: A name of the removing option
        :type option: string
        '''
        if self.hasOption(section, option):
            self._readbuf.remove_option(section, option)
            if self._writebuf.has_option(section, option):
                self._writebuf.remove_option(section, option)

    def getValue(self, section, option):
        '''
        Gets an option value of the given configuration section. If the option
        does not exist the 'None' is returned.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :return: A value of the specified option
        :rtype: string
        '''
        if not self.hasOption(section, option):
            return None
        return self._readbuf.get(section, option, raw=True)

    def getIntValue(self, section, option):
        '''
        Gets the option value converted to integer of the given configuration
        section. If the option does not exist the 'None' is returned.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :return: A value of the specified option
        :rtype: integer
        '''
        if not self.hasOption(section, option):
            return None
        try:
            return self._readbuf.getint(section, option)
        except ValueError:
            return None

    def getBoolValue(self, section, option):
        '''
        Gets an option value converted to boolean of the given configuration
        section. If the option does not exist the 'None' is returned.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :return: A value of the specified option
        :rtype: boolean
        '''
        if not self.hasOption(section, option):
            return None
        try:
            return self._readbuf.getboolean(section, option)
        except ValueError:
            return None

    def getListValue(self, section, option):
        '''
        Gets an option value converted to list of the given configuration
        section. If the option does not exist the 'None' is returned.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :return: A value of the specified option
        :rtype: list
        '''
        value = self.getValue(section, option)
        if value is None:
            return None
        if not value:
            return []
        return value.split(self._LIST_ITEM_SEPARATOR)

    def setValue(self, section, option, value):
        '''
        Sets the given option value in the specified configuration section.
        The section will be created automatically if it does not exist.

        :param section: A name of the section
        :type section: string
        :param option: A name of the option
        :type option: string
        :param value: The new value
        :type value: string
        '''
        if not self.hasSection(section):
            self.addSection(section)
        if isinstance(value, (list, tuple)):
            value = [str(i) for i in value]
            value = self._LIST_ITEM_SEPARATOR.join(value)
        self._readbuf.set(section, option, str(value))
        if not self._writebuf.has_section(section):
            self._writebuf.add_section(section)
        self._writebuf.set(section, option, str(value))

    def write(self):
        '''
        Writes configuration to a file in user configuration location.
        '''
        fd = None
        try:
            fd = open(self.file, 'w')
            self._writebuf.write(fd)
        finally:
            if fd:
                fd.close()


# A list of all available configuration directories
_configDirs = None
# The configuration cache
_configCache = None

def _initDirs():
    '''
    Initializes the configuration directory list.
    '''
    global _configDirs
    dirs = []
    if _programName:
        dirs.append(os.path.join(_USER_CONF_DIR, _programName))
        dirs.append(os.path.join(CONF_DIR, _programName))
    dirs.append(os.path.join(_USER_CONF_DIR, _CONF_COMMON_NAME))
    dirs.append(os.path.join(CONF_DIR, _CONF_COMMON_NAME))
    _configDirs = []
    for i, d in enumerate(dirs):
        if not (i % 2 or os.path.isdir(d)):
            try:
                os.makedirs(d, mode=0755)
            except IOError:
                pass
        if os.path.isdir(d):
            _configDirs.append(d)


def _loadConfigs():
    '''
    Loads all available configurations.
    '''
    global _configDirs, _configCache
    if _configDirs is None:
        _initDirs()
    _configCache = {}
    for d in _configDirs:
        for f in os.listdir(d):
            if f.endswith(_CONF_FILE_EXT):
                name = os.path.splitext(f)[0]
                if name not in _configCache:
                    _configCache[name] = Config(f, os.path.basename(d))

def _getConfigCache():
    '''
    Returns the configuration cache as a dictionary.
    '''
    if _configCache is None:
        _loadConfigs()
    return _configCache

def _getConfig(name, force=True):
    '''
    Returns configuration cached in a dictionary of the given name.
    '''
    configs = _getConfigCache()
    if name not in configs:
        if not force:
            return None
        configs[name] = Config(name + _CONF_FILE_EXT,
                               getProgramName() or _CONF_COMMON_NAME)
    return configs[name]

def update(name, file):
    '''
    Updates configuration of the given name using the specified file.

    :param name: A name of configuration
    :type name: string
    :param file: A path to the file
    :type file: string
    '''
    _getConfig(name).update(file)

def get(name=None, section=None, option=None, default=None):
    '''
    Returns different results depending on number of given arguments:
      - if configuration name, section and option are given then returns a value
        of the specified option,
      - if only configuration name and section are given then returns a list of
        options for the specified section,
      - if configuration name is given then returns a list of available sections
        in the configuration file,
      - if no argument is given then returns a list of available configurations.

    :param name: A name of configuration
    :type name: string
    :param section: A name of the section
    :type section: string
    :param option: A name of the option
    :type option: string
    :param default: An optional argument that can specify a default value
    :type default: string
    :return: A value of the specified option or list of options or sections
        or configurations
    :rtype: string or list
    '''
    if not name:
        return _getConfigCache().keys()

    config = _getConfig(name, force=False)
    if option:
        value = None
        if config:
            value = config.getValue(section, option)
        return value if value is not None else default
    elif section:
        if config:
            return config.getOptions(section)
        return []
    else:
        if config:
            return config.getSections()
        return []

def getInt(name, section, option, default=None):
    '''
    Returns a value converted to integer of the specified option.

    :param name: A name of configuration
    :type name: string
    :param section: A name of the section
    :type section: string
    :param option: A name of the option
    :type option: string
    :param default: An optional argument that can specify a default value
    :type default: integer
    :return: A value of the specified option
    :rtype: integer
    '''
    value = None
    config = _getConfig(name, force=False)
    if config:
        value = config.getIntValue(section, option)
    return value if value is not None else default

def getBool(name, section, option, default=None):
    '''
    Returns a value converted to integer of the specified option.

    :param name: A name of configuration
    :type name: string
    :param section: A name of the section
    :type section: string
    :param option: A name of the option
    :type option: string
    :param default: An optional argument that can specify a default value
    :type default: boolean
    :return: A value of the specified option
    :rtype: boolean
    '''
    value = None
    config = _getConfig(name, force=False)
    if config:
        value = config.getBoolValue(section, option)
    return value if value is not None else default

def getList(name, section, option, default=None):
    '''
    Returns a value converted to list of the specified option.

    :param name: A name of configuration
    :type name: string
    :param section: A name of the section
    :type section: string
    :param option: A name of the option
    :type option: string
    :param default: An optional argument that can specify a default value
    :type default: list
    :return: A value of the specified option
    :rtype: list
    '''
    value = None
    config = _getConfig(name, force=False)
    if config:
        value = config.getListValue(section, option)
    return value if value is not None else default

def set(name, section=None, option=None, value=None):
    '''
    Sets different values depending on number of given arguments:
      - if configuration name, section, option and value are given then sets
        the specified option to the given value,
      - if only configuration name, section and option are given then adds
        the specified option to the configuration file, if it does not exist,
      - if only configuration name and section are given then adds the specified
        section to the configuration file, if it does not exist yet,
      - if only configuration name is given then creates the specified
        configuration file, if it does not exist yet.

    :param name: The name of configuration
    :type name: string
    :param section: The name of the section
    :type section: string
    :param option: The name of the option
    :type option: string
    :param value: The new value of the specific option
    :type value: string or integer or boolean
    '''
    config = _getConfig(name)
    if value is not None:
        config.setValue(section, option, value)
    elif option:
        config.addOption(section, option)
    elif section:
        config.addSection(section)
    config.write()

def remove(name, section=None, option=None):
    '''
    Removes either option or section or whole user configuration:
      - if configuration name, section and option are given then removes
        the specified option from the given section, if it already exists,
      - if only configuration name and section are given then removes
        the specified section from the configuration file, if it already exists,
      - if only configuration name is given then removes the specified
        configuration file, if it already exists.

    :param name: The name of configuration
    :type name: string
    :param section: The name of the section
    :type section: string
    :param option: The name of the option
    :type option: string
    '''
    config = _getConfig(name)
    if not config:
        return
    if option:
        config.removeOption(section, option)
    elif section:
        config.removeSection(section)
    elif config:
        del _getConfigCache()[name]
        try:
            if os.path.isfile(config.file):
                os.remove(config.file)
        except IOError:
            pass
        config = None
    if config:
        config.write()

def reset():
    '''
    Resets (removes recursively) user configuration.
    '''
    global _configDirs
    shutil.rmtree(_USER_CONF_DIR, True)
    _configDirs = None
    reload()

def reload():
    '''
    Reloads all configuration files.
    '''
    global _configCache
    _configCache = None

