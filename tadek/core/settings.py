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

from tadek.core import config

_META_OPTION_NAME = "__settings__"
_META_OPTION_VALUE = '1'

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class SettingsSection:
    '''
    A class for wrapping settings sections.
    '''
    def __init__(self, name, section):
        self._name = name
        self._section = section

    def __iter__(self):
        '''
        Iterates over all settings option of the section.

        :return: Option
        :rtype: SettingsOption
        '''
        for option in config.get(self._name, self._section):
            if option != _META_OPTION_NAME:
                yield SettingsOption(self._name, self._section, option)

    def __getitem__(self, option):
        '''
        Gets the option from the settings section.

        :param option: A name of the option
        :type option: string
        :return: A settings option
        :rtype: SettingsOption
        '''
        return self.get(option)

    def __setitem__(self, option, value):
        '''
        Sets the value to the option from the settings section.

        :param option: A name of the option
        :type option: string
        :param value: A option value
        :type value: string
        '''
        SettingsOption(self._name, self._section, option).set(value)

    def get(self, option, default=None):
        '''
        Gets the option of the specified default value from the settings
        section.

        :param option: A name of the option
        :type option: string
        :param default: An optional argument that specifies a default value
        :type default: string or integer or boolean
        :return: A settings option
        :rtype: SettingsOption
        '''
        if option == _META_OPTION_NAME:
            return None
        return SettingsOption(self._name, self._section, option, default)

    def name(self):
        '''
        Returns a name of the settings section.

        :return: A name of the section
        :rtype: string
        '''
        return self._section

    def remove(self):
        '''
        Removes the settings section.
        '''
        config.remove(self._name, self._section)


class SettingsOption:
    '''
    A class for wrapping settings options.
    '''
    def __init__(self, name, section, option, default=None):
        self._name = name
        self._section = section
        self._option = option
        self._default = default

    def __eq__(self, value):
        '''
        Checks if a value of the option is equal to the given value.
        '''
        if isinstance(value, SettingsOption):
            return self.get() == value.get()
        else:
            return self.get() == value

    def __ne__(self, value):
        '''
        Checks if a value of the option is not equal to the given value.
        '''
        return not (self == value)

    def __str__(self):
        '''
        Returns a value of the settings option converted to string.
        '''
        return self.get() or ''

    def __nonzero__(self):
        '''
        Returns a value of the settings option converted to boolean.
        '''
        return self.getBool() or False

    def __int__(self):
        '''
        Returns a value of the settings option converted to integer.
        '''
        return self.getInt() or 0

    def __iter__(self):
        '''
        Returns a value of the settings option converted to list.
        '''
        value = self.getList()
        if value is not None:
            for i in value:
                yield i

    def name(self):
        '''
        Returns a name of the settings option.

        :return: The option name
        :rtype: string
        '''
        return self._option

    def get(self):
        '''
        Gets a value of the settings option. If the option does not exist
        the 'None' is returned.

        :return: A value of the option
        :rtype: string
        '''
        return config.get(self._name, self._section,
                          self._option, self._default)

    def getInt(self):
        '''
        Gets a value of the settings option converted to integer. If the option
        does not exist the 'None' is returned.

        :return: A value of the option
        :rtype: integer
        '''
        return config.getInt(self._name, self._section,
                             self._option, self._default)

    def getBool(self):
        '''
        Gets a value of the settings option converted to boolean. If the option
        does not exist the 'None' is returned.

        :return: A value of the option
        :rtype: boolean
        '''
        return config.getBool(self._name, self._section,
                              self._option, self._default)

    def getList(self):
        '''
        Gets a value of the settings option converted to list. If the option
        does not exist the 'None' is returned.

        :return: A value of the option
        :rtype: list
        '''
        return config.getList(self._name, self._section,
                              self._option, self._default)

    def set(self, value):
        '''
        Sets the value to the settings option.

        :param value: Value to set for option
        :type value: string or integer or boolean
        '''
        _setSettings(self._name, self._section)
        config.set(self._name, self._section, self._option, value)

    def remove(self):
        '''
        Removes the settings option.
        '''
        config.remove(self._name, self._section, self._option)


def _isSettings(name, section=None, option=None):
    '''
    Checks if the given configuration or section, or option is a settings.
    '''
    if option and option == _META_OPTION_NAME:
        return False
    if section:
        return config.get(name, section, _META_OPTION_NAME)== _META_OPTION_VALUE
    for section in config.get(name):
        if _isSettings(name, section):
            return True
    return False

def _setSettings(name, section):
    '''
    Sets the settings meta option in the given configuration section.
    '''
    config.set(name, section, _META_OPTION_NAME, _META_OPTION_VALUE)


def get(name=None, section=None, option=None, default=None, force=False):
    '''
    Returns different results depending on number of given arguments:
      - if settings name, section and option are given then returns
        a SettingsOption object representing the specified option,
      - if only settings name and section are given then returns
        a SettingsSection object representing the specified section,
      - if only settings name is given then returns a list of available sections
        in the configuration file,
      - if no argument is given then returns a list of available settings.

    :param name: A name of configuration
    :type name: string
    :param section: A name of the section
    :type section: string
    :param option: A name of the option
    :type option: string
    :param default: An optional argument that can specify a default value
    :type default: string
    :param force: Makes a configuration section to be a settings section
    :type force: boolean
    :return: A list of settings, SettingsSection or SettingsOption object
    :rtype: list or SettingsSection or SettingsOption
    '''
    if force and section:
        _setSettings(name, section)
    if option:
        if _isSettings(name, section, option):
            return SettingsOption(name, section, option, default)
        return default
    elif section:
        if _isSettings(name, section):
            return SettingsSection(name, section)
        return None
    elif name:
        sections = []
        for section in config.get(name):
            if force or _isSettings(name, section):
                sections.append(section)
        return sections
    else:
        names = []
        for name in config.get():
            if force or _isSettings(name):
                names.append(name)
        return names

def set(name, section, option=None, value=None, force=False):
    '''
    Sets different settings values depending on number of given arguments:
      - if settings section, option and value are given then sets the specified
        option to the given value,
      - if only settings section and option are given then adds the specified
        option to the section, if it does not exist,
      - if only settings section is given then adds the specified section to
        the configuration file, if it does not exist yet.

    :param name: The name of configuration
    :type name: string
    :param section: The name of the section
    :type section: string
    :param option: The name of the option
    :type option: string
    :param value: The new value of the specific option
    :type value: string or integer or boolean
    :param force: Makes a configuration section to be a settings section
    :type force: boolean
    :return: True if success, False otherwise
    :rtype: boolean
    '''
    if force or section not in config.get(name) or _isSettings(name, section):
        _setSettings(name, section)
        config.set(name, section, option, value)
        return True
    return False

remove = config.remove
reset = config.reset
reload = config.reload

