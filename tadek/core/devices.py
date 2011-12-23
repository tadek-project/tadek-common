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

from tadek.core import settings
from tadek.connection.device import Device

#: A name of device configuration
CONFIG_NAME = "devices"

#: A default device IP address
DEFAULT_IP = "127.0.0.1"
#: A default device port number
DEFAULT_PORT = 8089

# The device cache
_cache = None

def reset():
    '''
    Resets the device cache.
    '''
    global _cache
    _cache = None

def load(type=None):
    '''
    Loads all configured devices using the given device type.

    :param type: A device class
    :type type: type
    '''
    global _cache
    if _cache is None:
        _cache = {}
    devices = []
    for name in settings.get(CONFIG_NAME, force=True):
        devices.append(name)
        if name in _cache:
            continue
        params = {}
        for option in settings.get(CONFIG_NAME, name, force=True):
            params[option.name()] = option
        try:
            _add(name, type or Device, **params)
        except:
            # FIXME: Log the error?
            pass
    for name in _cache.keys():
        if name not in devices:
            del _cache[name]

def all():
    '''
    Returns a list of all available devices.

    :return: A list of devices
    :rtype: list
    '''
    if _cache is None:
        load()
    return _cache.values()

def get(name):
    '''
    Gets a device of the given name or of the given client.

    :param name: A name of a device
    :type name: string
    :return: A device if it exists, None otherwise
    :rtype: tadek.connection.device.Device
    '''
    if _cache is None:
        load()
    return _cache.get(name)

def add(name, type=None, address=None, port=None, **params):
    '''
    Adds a new device of the specified name and parameters.

    :param name: A name of a device
    :type name: string
    :param type: A type of a device or None
    :type type: type
    :param params: A dictionary with device optional parameters
    :type params: dictionary
    :return: An added device
    :rtype: tadek.connection.device.Device
    '''
    if _cache is None:
        load(type)
    if name in _cache:
        return _cache[name]
    params["address"] = address or DEFAULT_IP
    params["port"] = port or DEFAULT_PORT
    for option in _section(name, **params):
        params[option.name()] = option
    return _add(name, type or Device, **params)

def remove(name):
    '''
    Removes a device of the given name.

    :param name: A name of a removed device
    :type name: string
    :return: A removed device
    :rtype: tadek.connection.device.Device
    '''
    if _cache is None:
        load()
    if name not in _cache:
        return None
    device = _cache.pop(name)
    settings.remove(CONFIG_NAME, name)
    return device

def update(name, **params):
    '''
    Updates device parameters of the given name.

    :param name: A name of a updated device
    :type name: string
    :param params: A dictionary with device parameters
    :type params: dictionary
    :return: An updated device
    :rtype: tadek.connection.device.Device
    '''
    if _cache is None:
        load()
    if name not in _cache:
        return None
    device = _cache[name]
    section = _section(name, **params)
    for param in params:
        device.params[param] = section[param]
    return device

def _add(name, type, **params):
    '''
    Adds a created device of the given parameters to the device cache.
    '''
    device = type(name, **params)
    _cache[name] = device
    return device

def _section(name, **params):
    '''
    Returns settings section representing a device given by its parameters.
    '''
    section = settings.get(CONFIG_NAME, name, force=True)
    for param, value in params.iteritems():
        section[param] = value
    return section

