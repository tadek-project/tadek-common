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

import time
import threading

from tadek.core.locale import escape
from tadek.connection import ConnectionError
from tadek.connection import protocol
from tadek.connection.client import Client, XmlClient

__all__ = ["Device", "OfflineDevice"]

class ConnectionThread(threading.Thread):
    '''
    A thread class for maintaining the connection loop.
    '''
    def __init__(self):
        threading.Thread.__init__(self, name="Connection Thread")

    def run(self):
        '''
        Maintains asynchronous connection. Should be called before any
        client-server communication (including connection setup) takes place.
        '''
        from tadek import connection
        connection.run()


class Device(object):
    '''
    Class for representing devices.
    '''
    clientClass = Client

    # Stores information about a connected device
    _info = None
    #: A thread object that maintain the connection loop common to all devices
    _connection = ConnectionThread()

    @classmethod
    def _ensureConnection(cls):
        '''
        Reactivates the connection thread if it terminated.
        '''
        if not cls._connection.isAlive():
            try:
                cls._connection = ConnectionThread()
                cls._connection.start()
            except Exception, err:
                raise ConnectionError("Connection failed with the error: %s",
                                      err)

    def __init__(self, name, address, port, description='', **params):
        '''
        Assigns a name and other parameters, and next initializes a related
        connection client.

        :param name: A name of the device
        :type name: string
        :param address: An IP address of the device
        :type address: string
        :param port: A port number of the device
        :type port: integer
        :param description: A description of the device
        :type description: string
        :param params: A dictionary with parameters
        :type params: dictionary
        '''
        self.client = self.clientClass()
        self.params = {
            "name" : name,
            "address" : address,
            "port" : port,
            "description": description
        }
        self.params.update(params)

    def __str__(self):
        return "<%s.%s('%s', %s:%d) at 0x%x>" % (self.__class__.__module__,
                                                 self.__class__.__name__,
                                             self.name, self.params["address"],
                                             self.params["port"], id(self))

    @property
    def name(self):
        '''
        Gets the device name.

        :return: A name of the device
        :rtype: string
        '''
        return str(self.params["name"])

    @property
    def address(self):
        '''
        Gets the device address a tuple (adress and port).

        :return: An address and a port of the device
        :rtype: tuple
        '''
        return str(self.params["address"]), int(self.params["port"])

    @property
    def description(self):
        '''
        Gets the device description.

        :return: A description of the device
        :rtype: string
        '''
        return str(self.params["description"])

    @property
    def version(self):
        '''
        Gets the device version.

        :return: A version of the device
        :rtype: string
        '''
        return self._info and self._info.version

    @property
    def locale(self):
        '''
        Gets the device locale.

        :return: A locale of the device
        :rtype: string
        '''
        return self._info and self._info.locale

    @property
    def extensions(self):
        '''
        Gets a list of protocol extensions supported by the device.

        :return: A list of protocol extensions
        :rtype: tuple
        '''
        if not self._info:
            return []
        return [ext for ext in protocol.getExtensions()
                    if ext in self._info.extensions]

    # Constants used by the connect() method:
    _connectMinAttempts = 3
    _connectMaxAttempts = 12
    _connectTimeout = 0.1
    _infoTimeout = 5.0

    def connect(self):      
        '''
        Initializes a connection with the device.
        '''
        if self.isConnected():
            return False
        self.client.connect(*self.address)
        self._ensureConnection()
        attempt = 0
        while ((not self.isConnected() or attempt < self._connectMinAttempts)
               and attempt < self._connectMaxAttempts):
            time.sleep(self._connectTimeout)
            attempt += 1
        if self.isConnected():
            try:
                self._info = self.getResponse(protocol.INFO_MSG_ID,
                                              self._infoTimeout)
                return True
            except:
                self.client.disconnect()
        raise ConnectionError("Connection refused")

    def disconnect(self):
        '''
        Closes connection with a device.
        '''
        if not self.isConnected():
            return False
        self._ensureConnection()
        try:
            self.client.disconnect()
            return True
        except Exception, err:
            raise ConnectionError("Error while disconnecting device: %s" % err)

    def isConnected(self):
        '''
        Returns a device connection status.

        :return: True if device is connected, False otherwise
        :rtype: boolean
        ''' 
        return self.client.isConnected()

# Asynchronous methods
    def request(self, target, name, params):
        '''
        Sends the given request of the specified parameters concerning
        the given accessible path.

        :param target: A name of the request target
        :type target: string
        :param name: A name of the request function
        :type name: string
        :param params: A dictionary with the request parameters
        :type params: dictionary
        :return: Id of the sent request
        :rtype: integer
        '''
        if not self.isConnected():
            raise ConnectionError("Device is not connected")
        request = protocol.create(protocol.MSG_TYPE_REQUEST,
                                  target, name, **params)
        self.client.request(request) 
        return request.id

    def requestAccessible(self, path, depth, name=True, description=False,
                          role=True, count=True, position=False, size=False,
                          text=False, value=False, actions=False, states=False,
                          attributes=False, relations=False, all=False):
        '''
        Sends a request for an accessible object of the given path. If depth is
        is equal -1, the incoming response will also contain descendants of
        the requested accessible object.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param depth: A number of child generations, -1 for infinity
        :type depth: integer
        :param name: If True then request for accessible name (True by default)
        :type name: boolean
        :param role: If True then request for accessible role (True by default)
        :type role: boolean
        :param count: If True then request for accessible child count
            (True by default)
        :type count: boolean
        :param position: If True then request for accessible position
            (False by default)
        :type position: boolean
        :param size: If True then request for accessible size (False by default)
        :type size: boolean
        :param text: If True then request for accessible text (False by default)
        :type text: boolean
        :param value: If True then request for accessible value
            (False by default)
        :type value: boolean
        :param actions: If True then request for accessible actions
            (False by default)
        :type actions: boolean
        :param states: If True then request for accessible states
            (False by default)
        :type states: boolean
        :param attributes: If True then request for accessible attributes
            (False by default)
        :type attributes: boolean
        :param relations: If True then request for accessible relations
            (False by default)
        :type relations: boolean
        :param all: If True then request for all possible accessible parameters
        :type all: boolean
        :return: Id of the sent request
        :rtype: integer
        '''
        include = []
        if name or all:
            include.append(u"name")
        if description or all:
            include.append(u"description")
        if role or all:
            include.append(u"role")
        if count or all:
            include.append(u"count")
        if position or all:
            include.append(u"position")
        if size or all:
            include.append(u"size")
        if text or all:
            include.append(u"text")
        if value or all:
            include.append(u"value")
        if actions or all:
            include.append(u"actions")
        if states or all:
            include.append(u"states")
        if attributes or all:
            include.append(u"attributes")
        if relations or all:
            include.append(u"relations")
        params = {
            "path": path,
            "depth": depth,
            "include": include
        }
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_GET, params)

    def requestSearchAccessible(self, path, method, name=None, description=None,
                                      role=None, index=None, count=None,
                                      action=None, relation=None, state=None,
                                      text=None, nth=0, **attrs):
        '''
        Sends a request for searching an accessible object starting from
        the given path and using the specified search method.

        :param path: A starting path for the searching of accessible object
        :type path: tadek.core.accessible.Path
        :param method: A search method of accessible
        :type method: string
        :param name: A name of searched accessible or None
        :type name: string or NoneType
        :param description: A description of searched accessible or None
        :type description: string or NoneType
        :param role: A role of searched accessible or None
        :type role: string or NoneType
        :param index: An index of searched accessible or None
        :type index: integer or NoneType
        :param count: A child count of searched accessible or None
        :type count: string or NoneType
        :param action: An action of searched accessible or None
        :type action: string or NoneType
        :param relation: A relation of searched accessible or None
        :type relation: string or NoneType
        :param state: A state of searched accessible or None
        :type state: string or NoneType
        :param text: Text of searched accessible or None
        :type text: string or NoneType
        :param nth: A nth matched accessible
        :type nth: integer
        :param attrs: Attributes of searched accessible
        :type attrs: dictionary
        :return: Id of the sent request
        :rtype: integer
        '''
        predicates = {
            "nth": nth
        }
        if name is not None:
            predicates["name"] = escape(name, self)
        if description is not None:
            predicates["description"] = escape(description, self)
        if role is not None:
            predicates["role"] = role
        if index is not None:
            predicates["index"] = index
        if count is not None:
            predicates["count"] = count
        if action is not None:
            predicates["action"] = action
        if relation is not None:
            predicates["relation"] = relation
        if state is not None:
            predicates["state"] = state
        if text is not None:
            predicates["text"] = escape(text, self)
        predicates.update(attrs)
        for attr, value in attrs.iteritems():
            predicates[attr] = escape(value, self)
        params = {
            "path": path,
            "method": method,
            "predicates": predicates
        }
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_SEARCH, params)

    def requestDoAccessible(self, path, action):
        '''
        Sends a request performing the given action on an accessible object of
        the specified path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param action: A name of the action to perform
        :type action: string
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "path": path,
            "action": action
        }
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_EXEC, params)

    def requestSetAccessible(self, path, text=None, value=None):
        '''
        Sends a request setting the given text or value in an accessible
        object of the specified path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param text: New text for the accessible object
        :type text: string
        :param value: A new value for the accessible object
        :type value: float
        :return: Id of the sent request
        :rtype: integer
        '''
        if text is None and value is None:
            raise ValueError("Text or value must be specified")
        params = {
            "path": path
        }
        if text is not None:
            params["text"] = escape(text, self)
        else:
            params["value"] = value
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_PUT, params)

    def requestMouseEvent(self, path, x, y, button, event):
        '''
        Sends a request generating a mouse event on an accessible object of
        the specified path at the given x and y coordinates using the specified
        mouse button.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param x: The absolute horizontal coordinate
        :type x: integer
        :param y: The absolute vertical coordinate
        :type y: integer
        :param button: The mouse button to use
        :type button: string
        :param event: The event to generate
        :type event: string
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "path": path,
            "coordinates": (x, y),
            "button": button,
            "event": event
        }
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_EXEC, params)
       
    def requestKeyboardEvent(self, path, key, modifiers=()):
        '''
        Generates a keyboard event of the given key code using the specified
        modifiers for an accessible object of the given path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param key: A code of the key
        :type key: integer
        :param modifiers:  Codes of used modifier keys
        :type modifiers: list
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "path": path,
            "keycode": key,
            "modifiers": modifiers
        }
        return self.request(protocol.MSG_TARGET_ACCESSIBILITY,
                            protocol.MSG_NAME_EXEC, params)

    def requestGetFile(self, path):
        '''
        Sends a request for content data of a file of the given path in
        the device file system.

        :param path: A path to the file
        :type path: string
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "path": path
        }
        return self.request(protocol.MSG_TARGET_SYSTEM,
                            protocol.MSG_NAME_GET, params)

    def requestSystemExec(self, command, wait=True):
        '''
        Sends a request executing the given command in the device system.

        :param command: A cammand to execute
        :type command: string
        :param wait: Wait for command process to terminate
        :type wait: boolean
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "command": command,
            "wait": wait
        }
        return self.request(protocol.MSG_TARGET_SYSTEM,
                            protocol.MSG_NAME_EXEC, params)

    def requestPutFile(self, path, data):
        '''
        Sends a request putting the given data in a file of the specified path
        in the device file system.

        :param path: A path to the file
        :type path: string
        :param data: New content data for the file
        :type data: string
        :return: Id of the sent request
        :rtype: integer
        '''
        params = {
            "path": path,
            "data": data
        }
        return self.request(protocol.MSG_TARGET_SYSTEM,
                            protocol.MSG_NAME_PUT, params)

    def requestExtension(self, name, **params):
        '''
        Sends a request defined by a protocol extension of the given name and
        the specified parameters.

        :param name: A name of a protocol extension
        :type name: string
        :param params: Parameters of a request
        :type params: dictionary
        :return: Id of the sent request
        :rtype: integer
        '''
        if name not in self.extensions:
            raise protocol.extension.UnsupportedProtocolExtensionError(name)
        return self.request(protocol.MSG_TARGET_EXTENSION, name,
                            protocol.getExtension(name).request(**params))

# Synchronous methods
    def getResponse(self, id, timeout=300):
        '''
        Gets a response of the given id from the client message queue.
        If timeout is specified, it blocks at most timeout seconds and returns
        None if no item was available within that time.

        :param id: The response id
        :type id: integer
        :param timeout: The time of blocking, 5 minutes by default
        :type timeout: float
        :return: A response of the given id or None
        :rtype: tadek.connection.protocol.Response
        '''
        response = self.client.response(id, timeout)
        if response is None:
            raise Exception("Timeout reached while waiting for response")
        return response

    def getAccessible(self, path, depth=0, **kwargs):
        '''
        Gathers an accessible object of the given path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param depth: A number of child generations, -1 for infinity
            (0 by default)
        :type depth: integer
        :param kwargs: A collection of keyword arguments of requestAccessible()
            method
        :type kwargs: dictionary
        :return: Requested accessible object or None if request failed
        :rtype: tadek.core.accessible.Accessible
        '''
        id = self.requestAccessible(path, depth=depth, **kwargs)
        response = self.getResponse(id)
        if not response.status:
            return None
        response.accessible.setDevice(self)
        return response.accessible

    def searchAccessible(self, path, method, **kwargs):
        '''
        Searches an accessible object starting from the given path and using
        the specified search method.

        :param path: A starting path for the searching of accessible object
        :type path: tadek.core.accessible.Path
        :param method: A search method of accessible object
        :type method: string
        :param kwargs: A collection of keyword arguments to
            requestSearchAccessible() method
        :type kwargs: dictionary
        :return: Searched accessible object or None if request failed
        :rtype: tadek.core.accessible.Accessible
        '''
        id = self.requestSearchAccessible(path, method=method, **kwargs)
        response = self.getResponse(id)
        if not response.status:
            return None
        response.accessible.setDevice(self)
        return response.accessible

    def doAccessible(self, path, action):
        '''
        Performs the given action on an accessible object specified by the path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param action: A name of the action to perform on the accessible object
        :type action: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestDoAccessible(path, action)
        response = self.getResponse(id)
        return response.status

    def setAccessible(self, path, text=None, value=None):
        '''
        Sets a new value or text in an accessible object of the given path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param text: New text to set in the accessible object
        :type text: string
        :param value: New value to set in the accessible object
        :type value: float
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestSetAccessible(path, text, value)
        response = self.getResponse(id)
        return response.status             

    def mouseEvent(self, path, x, y, button, event):
        '''
        Generates the given mouse event on an accessible object of the specified
        path at the given x and y coordinates using the specified mouse button.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param x: The absolute horizontal coordinate
        :type x: integer
        :param y: The absolute vertical coordinate
        :type y: integer
        :param button: The mouse button to use
        :type button: string
        :param event: The event to generate
        :type event: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestMouseEvent(path, x, y, button, event)
        response = self.getResponse(id)
        return response.status

    def keyboardEvent(self, path, key, modifiers=()):
        '''
        Generates a keyboard event for the given key code using the specified
        modifiers for an accessible object of the given path.

        :param path: A path to the accessible object
        :type path: tadek.core.accessible.Path
        :param key: A code of the key
        :type key: integer
        :param modifiers:  Codes of used modifier keys
        :type modifiers: list
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestKeyboardEvent(path, key, modifiers)
        response = self.getResponse(id)
        return response.status

    def getFile(self, path):
        '''
        Gets content data of a file of the given path in the device file system.

        :param path: A path to the file
        :type path: string
        :return: The file content data or None
        :rtype: string
        '''
        id = self.requestGetFile(path)
        response = self.getResponse(id)
        if response.status:
            return response.data
        return None

    def systemExec(self, command, wait=True):
        '''
        Executes the given command in the device system.

        :param command: A cammand to execute
        :type command: string
        :param wait: Wait for command process to terminate
        :type wait: boolean
        :return: The command execution status, output and error
        :rtype: tuple
        '''
        id = self.requestSystemExec(command, wait)
        response = self.getResponse(id)
        return response.status, response.stdout, response.stderr

    def putFile(self, path, data):
        '''
        Puts the given data in a file of the specified path in the device file
        system.

        :param path: A path to the file
        :type path: string
        :param data: New content data for the file
        :type data: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestPutFile(path, data)
        response = self.getResponse(id)
        return response.status

    def extension(self, name, **params):
        '''
        Performs a request defined by a protocol extension of the given name and
        the specified parameters, and get a device response.

        :param name: A name of a protocol extension
        :type name: string
        :param params: Parameters of a request
        :type params: dictionary
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        id = self.requestExtension(name, **params)
        response = self.getResponse(id)
        result = [response.status]
        for name in sorted(response.getParams()):
            if name != "status":
                result.append(getattr(response, name))
        return tuple(result) if len(result) > 1 else result[0]

    def getError(self, timeout=300):
        '''
        Gets an error from the client message queue.
        If timeout is specified, it blocks at most timeout seconds and returns
        None if no error was available within that time.

        :param id: The response id
        :type id: integer
        :param timeout: The time of blocking, 5 minutes by default
        :type timeout: float
        :return: A response of the given id or None
        :rtype: tadek.connection.protocol.Response
        '''
        error = self.client.error(timeout)
        if error is None:
            raise Exception("Timeout reached while waiting for error")
        return error


class OfflineDevice(Device):
    '''
    A class of offline devices that base on accessible tree dumped to XML files.
    '''
    clientClass = XmlClient

    def __init__(self, name, file, **params):
        '''
        Assigns a name and other parameters, and next initializes a related
        connection client.

        :param name: A name of the device
        :type name: string
        :param file: A path to the file containing an accessibe tree
        :type file: string
        :param params: A dictionary with parameters
        :type params: dictionary
        '''
        Device.__init__(self, name, file, 0)

    def connect(self):      
        '''
        Initializes a connection with the offline device.
        '''
        if self.isConnected():
            raise ConnectionError("Offline device already connected")
        else:
            self.client.connect(self.address[0])
            if self.isConnected():
                return True
            raise ConnectionError("Offline device could not connect")

    def disconnect(self):
        '''
        Closes a connection with the offline device.
        '''
        if self.isConnected():
            self.client.disconnect()
            return not self.isConnected()

