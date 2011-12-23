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

from tadek.core import constants
from tadek.core import accessible

__all__ = ["Model"]

class Model(object):
    '''
    A base class of all testing models.
    '''
    # The root element of the model
    root = None

    def __getattr__(self, attr):
        if hasattr(self.root, attr):
            return getattr(self.root, attr)
        raise AttributeError("Type model '%s' has no attribute '%s'"
                              % (self.__class__.__name__, attr))

# Mouse events:
    def clickMouseAt(self, device, x, y, button="LEFT"):
        '''
        Simulates a mouse click at the given x and y coordinates.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param x: A left-hand oriented horizontal coordinate
        :type x: integer
        :param y: A left-hand oriented vertical coordinate
        :type y: integer
        :param button: A mouse button simulating the event
        :type button: string
        :return: Event completion status
        :rtype: boolean
        '''
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError
        return device.mouseEvent(accessible.Path(0), x, y, button, "CLICK")

    def doubleClickMouseAt(self, device, x, y, button="LEFT"):
        '''
        Simulates a mouse double-click at the given x and y coordinates.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param x: A left-hand oriented horizontal coordinate
        :type x: integer
        :param y: A left-hand oriented vertical coordinate
        :type y: integer
        :param button: A mouse button simulating the event
        :type button: string
        :return: Event completion status
        :rtype: boolean
        '''
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, "DOUBLE_CLICK")

    def pressMouseAt(self, device, x, y, button="LEFT"):
        '''
        Simulates a mouse press at the given x and y coordinates.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param x: A left-hand oriented horizontal coordinate
        :type x: integer
        :param y: A left-hand oriented vertical coordinate
        :type y: integer
        :param button: A mouse button simulating the event
        :type button: string
        :return: Event completion status
        :rtype: boolean
        '''
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError
        return device.mouseEvent(accessible.Path(0), x, y, button, "PRESS")

    def releaseMouseAt(self, device, x, y, button="LEFT"):
        '''
        Simulates a mouse release at the given x and y coordinates.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param x: A left-hand oriented horizontal coordinate
        :type x: integer
        :param y: A left-hand oriented vertical coordinate
        :type y: integer
        :param button: A mouse button simulating the event
        :type button: string
        :return: Event completion status
        :rtype: boolean
        '''
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError
        return device.mouseEvent(accessible.Path(0), x, y, button, "RELEASE")

    def moveMouseTo(self, device, x, y):
        '''
        Simulates a mouse absolute motion to the given x and y coordinates.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param x: A left-hand oriented horizontal coordinate
        :type x: integer
        :param y: A left-hand oriented vertical coordinate
        :type y: integer
        :return: Event completion status
        :rtype: boolean
        '''
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError
        return device.mouseEvent(accessible.Path(0), x, y,
                                 "LEFT", "ABSOLUTE_MOTION")

# System commands
    def systemCommand(self, device, command, wait=True):
        '''
        Executes the given command in a test system and returns a return code,
        output and error.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param command: The command to execute
        :type command: string
        :param wait: Wait for command process to terminate, True by default
        :type wait: boolean
        :return: The command execution status, output and error
        :rtype: tuple
        '''
        return device.systemExec(command, wait=wait)

    def getFile(self, device, path):
        '''
        Gets file content data of the given path in a test system.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param path: A path to the file
        :type path: string
        :return: The file content data or None
        :rtype: string
        '''
        return device.getFile(path)

    def sendFile(self, device, path, data):
        '''
        Sends the given file content data of the specified path in a test
        system.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param path: A path to the file
        :type path: string
        :param data: New content data for the file
        :type data: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return device.putFile(path, data)

# Keyboard events:
    def generateKey(self, device, key, modifiers=()):
        '''
        Generates a keyboard event for the given key.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param key: A key code or string representation
        :type key: integer or string
        :param modifiers: A list of modifier key codes or names
        :type modifiers: list or tuple
        :return: Event completion status
        :rtype: boolean
        '''
        if isinstance(key, basestring):
            key = constants.KEY_SYMS.get(key) or ord(key)
        codes = []
        for mkey in modifiers:
            if isinstance(mkey, basestring):
                mkey = constants.KEY_CODES.get(mkey)
            codes.append(mkey)
        return device.keyboardEvent(accessible.Path(0), key, codes)

    def keyUp(self, device):
        '''
        Simulates the keyboard Up key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "UP")

    def keyDown(self, device):
        '''
        Simulates the keyboard Down key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "DOWN")

    def keyLeft(self, device):
        '''
        Simulates the keyboard Left key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "LEFT")

    def keyRight(self, device):
        '''
        Simulates the keyboard Right key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "RIGHT")

    def keyEnter(self, device):
        '''
        Simulates the keyboard Enter/Return key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "ENTER")

    def keyEscape(self, device):
        '''
        Simulates the keyboard Escape key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "ESCAPE")

    def keyTab(self, device):
        '''
        Simulates the keyboard Tab key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "TAB")

    def keyBackspace(self, device):
        '''
        Simulates the keyboard Backspace key event.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Event completion status
        :rtype: boolean
        '''
        return self.generateKey(device, "BACKSPACE")

    def protocolExtension(self, device, name, **params):
        '''
        Performs an operation defined by a protocol extension of the given name
        and parameters on the specified device.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param name: A name of the protocol extension
        :type name: string
        :param params: Parameters of the protocol extension
        :type params: dictionary
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return device.extension(name, **params)

