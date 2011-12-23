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

import socket
import asyncore
import asynchat
import threading
from traceback import format_exc
from xml.etree import cElementTree as etree

from tadek import connection
from tadek.connection import protocol
from tadek.core import queue
from tadek.core.accessible import Path, Accessible
from tadek.core.utils import decode

class Error(Exception, queue.QueueItem):
    '''
    A base class of items representing client error messages.
    '''
    id = protocol.ERROR_MSG_ID
    traceback = None

    def __init__(self, msg):
        queue.QueueItem.__init__(self, self.id)
        if isinstance(msg, Exception):
            self.traceback = format_exc()
        Exception.__init__(self, msg)
        self.msg = decode(msg)

    def __unicode__(self):
        return self.msg

class ClosingError(Error):
    '''
    A class of items representing errors that cause closing a connection.
    '''
    pass

class ConnectionLostError(ClosingError):
    '''
    A class of items representing a connection lost error.
    '''
    def __init__(self):
        Error.__init__(self, "Lost connection error")

class ConnectionRefusedError(ClosingError):
    '''
    A class of items representing errors that prevented a client from
    connecting to a daemon.
    '''
    def __init__(self, msg):
        Error.__init__(self, msg)


class Client(asynchat.async_chat):
    '''
    A base class of clients.
    '''
    queueClass = queue.Queue

    #: Dictionary that binds socket error codes to human readable descriptions
    errorStrs = {
        10061: "Host is up, but it is not listening on specified port",
        111:   "Host is up, but it is not listening on specified port",
        10049: "Address is not available",
        125:   "Address is not available"
    }

    def __init__(self):
        '''
        Only initializes client (without connecting).
        '''
        asynchat.async_chat.__init__(self)
        self._mutex = threading.RLock()
        self.messages = self.queueClass()
        self.set_terminator(protocol.MSG_TERMINATOR)

    def connect(self, address, port):
        '''
        Function for connecting to server.
        '''
        try:
            if not self.socket:
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            asynchat.async_chat.connect(self, (address, port))
        except socket.error, err:
            if not connection.minorSocketError(err):
                self.messages.put(Error(err))

    def disconnect(self):
        '''
        Closes connection to a server.
        '''
        try:
            if self.socket:
                self._mutex.acquire()
                try:
                    self.close()
                finally:
                    self._mutex.release()
        except socket.error, err:
            self.messages.put(Error(connection.processSocketError(err)))
        finally:
            self.socket = None

    def isConnected(self):
        '''
        Indicates whether client is connected or not.
        '''
        self._mutex.acquire()
        try:
            return self.connected
        finally:
            self._mutex.release()

    def handle_connect(self):
        '''
        Called when the active openers socket actually makes a connection.
        '''
        pass

    def handle_close(self):
        '''
        Function for handling close. Called when the socket is closed.
        '''
        self.disconnect()
        self.messages.put(ConnectionLostError())

    def collect_incoming_data(self, data):
        '''
        Function called when some data is read from socket.

        :param data: Read data.
        :type data: string
        '''
        if data != None:
            self._collect_incoming_data(data)

    def found_terminator(self):
        '''
        Function called when message terminator set by function set_terminator
        is found.
        '''
        self.messages.put(protocol.parse(self._get_data(),
                                         defaultClass=protocol.DefaultResponse))

    def handle_write(self):
        '''
        Function for thread-safe handling a write event.
        '''
        self._mutex.acquire()
        try:
            asynchat.async_chat.handle_write(self)
        finally:
            self._mutex.release()

    def handle_error(self):
        '''
        Method for handling uncaptured errors.
        '''
        err = asyncore.compact_traceback()[2]
        error = Error(err)
        if isinstance(err, socket.error):
            if connection.closingSocketError(err):
                self.handle_close()
                return
            elif connection.minorSocketError(err):
                self.disconnect()
                return
            elif err[0] in (10060, 110):
                #WSATIMEDOUT error keeps occurring if socket isn't closed
                self.disconnect()
            elif err[0] in self.errorStrs:
                error = ConnectionRefusedError(self.errorStrs[err[0]])
                self.disconnect()
            else:
                error = ConnectionRefusedError(
                                    connection.processSocketError(err))
                self.disconnect()
        self.messages.put(error)

    def request(self, request):
        '''
        Sends the given request to a server connected to.

        :param request: A request to send
        :type request: tadek.connection.protocol.Request
        '''
        self._mutex.acquire()
        try:
            self.push(''.join([request.marshal(), self.get_terminator()]))
        except Exception, err:
            self.messages.put(Error(err))
        finally:
            self._mutex.release()

    def response(self, id, timeout=None):
        '''
        Subsequent calls of this method return queued server responses in order
        of reception.

        :param id: ID of the response to get
        :type id: integer
        :return: A fist response from the message queue
        :rtype: tadek.connection.protocol.Response
        '''
        return self.messages.get(id, timeout=timeout)

    def error(self, timeout=None):
        '''
        Subsequent calls of this method return queued errors in order
        of reception.

        :return: A fist error from the message queue
        :rtype: tadek.connection.protocol.Response
        '''
        return self.messages.get(protocol.ERROR_MSG_ID, timeout=timeout)


class XmlClient(object):
    '''
    A class of fake clients used to serve accessible from dumped accessible
    trees.
    '''
    queueClass = queue.Queue

    def __init__(self):
        self._root = None
        self.messages = self.queueClass()

    def connect(self, file):
        '''
        Loads an accessible tree from the given file.

        :param file: A name of the XML file to load
        :type file: string
        '''
        def setPath(acc, parentPath=None):
            if parentPath is None:
                acc.path = Path()
            else:
                acc.path = parentPath.child(acc.index)
            for child in acc.children():
                setPath(child, acc.path)

        try:
            element = etree.ElementTree(file=file).getroot()
            acc = Accessible.unmarshal(element)
            if not acc.path.tuple:
                self._root = acc
            else:                
                self._root = Accessible(Path(), children=(acc,))
            acc.index = 0
            setPath(self._root)
        except Exception, err:
            self.messages.put(Error(err))

    def disconnect(self):
        '''
        Clears the element tree loaded using connect(). Changes the state
        to disconnected.
        '''
        self._root = None

    def isConnected(self):
        '''
        Indicates whether client is connected to some file.

        :return: Current connection state
        :rtype: boolean
        '''
        return self._root is not None

    def request(self, request):
        '''
        Handles requests by generating appropriate response based on
        the accessible tree loaded from a connected dump file.

        :param request: A request to handle
        :type request: tadek.connection.protocol.Request
        '''
        def getAccessible(path):
            '''
            Gets an accessible of the given path.
            '''
            # TODO
            #if not path.tuple:
            #    # Create a fake accessible representing the root
            #    return Accessible(self._root.path.parent() or Path(),
            #                      children=(self._root,))
            #n = len(self._root.path.tuple)
            #if len(path.tuple) < n or path.tuple[:n] != self._root.path.tuple:
            #    return None
            acc = self._root
            if acc.path == path:
                return acc
            try:
                #for idx in path.tuple[n:]:
                for idx in path.tuple:
                    if idx >= acc.count:
                        return None
                    i = 0
                    for child in acc.children():
                        if i == idx:
                            acc = child
                            break
                        i += 1
                    if i != idx:
                        return None
            except Exception, err:
                self.messages.put(Error(err))
                acc = None
            return acc
        
        extras = {}
        if self._root is None:
            self.messages.put(Error("XML client is not connected"))
        elif request.target == protocol.MSG_TARGET_ACCESSIBILITY:
            if request.name == protocol.MSG_NAME_GET:
                accessible = getAccessible(request.path)
                extras = {
                    "status": accessible is not None,
                    "accessible": accessible or Accessible(Path())
                }
            elif request.name == protocol.MSG_NAME_SEARCH:
                acc = getAccessible(request.path)
                # TODO: Currently not used
            elif request.name == protocol.MSG_NAME_PUT:
                extras = {
                    "status": False
                }
            elif request.name == protocol.MSG_NAME_EXEC:
                extras = {
                    "status": False
                }
        elif request.target == protocol.MSG_TARGET_SYSTEM:
            if request.name == protocol.MSG_NAME_GET:
                extras = {
                    "status": False,
                    "data": ''
                }
            elif request.name == protocol.MSG_NAME_PUT:
                extras = {
                    "status": False
                }
            elif request.name == protocol.MSG_NAME_EXEC:
                extras = {
                    "status": False,
                    "stdout": '',
                    "stderr": ''
                }
        if extras:
            response = protocol.create(protocol.MSG_TYPE_RESPONSE,
                                       request.target, request.name,
                                       **extras)
        else:
            response = protocol.DefaultResponse(request.target,
                                                request.name,
                                                status=False)
        response.id = request.id
        self.messages.put(response)

    def response(self, id, timeout=None):
        '''
        Subsequent calls of this method return queued responses of the given ID
        in order of reception.

        :param id: ID of the response to get
        :type id: integer
        :return: A fist response from the message queue
        :rtype: tadek.connection.protocol.Response
        '''
        return self.messages.get(id, block=False)

    def error(self, timeout=None):
        '''
        Subsequent calls of this method return queued errors in order
        of reception.

        :return: A fist error from the message queue
        :rtype: tadek.connection.protocol.Response
        '''
        return self.messages.get(protocol.ERROR_MSG_ID, block=False)

