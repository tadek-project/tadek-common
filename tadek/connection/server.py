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
import socket
import asyncore
import asynchat

from tadek import connection
from tadek.connection import protocol

class Handler(asynchat.async_chat):
    '''
    A class for handling client requests on the server side.
    '''
    def __init__(self, socket, client):
        '''
        Initializes channel between client and server.

        :param socket: Socket on which communication takes place
        :type socket: socket.Socket
        :param client: Client address
        :type client: tuple containing client IP address and port
        '''
        asynchat.async_chat.__init__(self, socket)
        self.client = client
        self.set_terminator(protocol.MSG_TERMINATOR)

    def onRequest(self, data):
        '''
        Function used to handle request received as raw XML.

        :param data: Request data
        :type data: string
        :return: Request and related response instance
        :rtype: tuple
        '''
        request = protocol.parse(data, defaultClass=protocol.DefaultRequest)
        if isinstance(request, protocol.DefaultRequest):
            response = protocol.DefaultResponse(request.target, request.name,
                                                status=False)
        else:
            response = None
        return request, response

    def onClose(self):
        '''
        Function called when socket is closed.
        '''
        pass

    def onError(self, exception):
        '''
        Function called when error occurs.

        :param exception: Exception to handle with
        :type exception: Exception
        '''
        raise exception

    def collect_incoming_data(self, data):
        '''
        Function called when some data is read from socket.

        :param data: Read data
        :type data: string
        '''
        if data is not None:
            self._collect_incoming_data(data)

    def found_terminator(self):
        '''
        Function called when message terminator set by function set_terminator 
        is found.
        '''
        request, response = self.onRequest(self._get_data())
        if response is None:
            response = protocol.DefaultResponse(request.target, request.name,
                                                status=False)
        response.id = request.id
        self.push(''.join([response.marshal(), self.get_terminator()]))

    def handle_close(self):
        '''
        Function for handling close. Called when the socket is closed.
        '''
        try:
            self.onClose()
            if self.socket:
                self.close()
        except Exception, e:
            self.onError(e)
        finally:
            self.socket = None

    def handle_error(self):
        '''
        Method for handling uncaptured errors.
        '''
        t, err, tbinfo = asyncore.compact_traceback()[1:]
        error = Exception("%s:%s\n%s" % (t, err,
                                         tbinfo[1:-1].replace("] [", "\n")))
        self.onError(error)
        if isinstance(err, socket.error):
            if connection.closingSocketError(err):
                self.handle_close()
            elif connection.minorSocketError(err):
                pass
            else:
                error = connection.ConnectionError(
                                        connection.processSocketError(err))
                self.onError(error)


class Server(asyncore.dispatcher):
    '''
    A base class of servers.
    '''
    #: Class which is responsible for serving client.
    handlerClass = Handler

    def __init__(self, address):
        '''
        Starts a server.

        :param address: An address of the server as ("ip", port)
        :type address: tuple
        '''
        try:
            self.address = address
            asyncore.dispatcher.__init__(self)
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            if os.name == "posix":
                self.set_reuse_addr()
            self.bind(address)
            self.listen(0)
        except socket.error:
            self.disconnect()
            raise

    def handle_accept(self):
        '''
        Called on listening channels (passive openers) when a connection can be
        established with a new remote endpoint that has issued a connect() call
        for the local endpoint.
        '''
        channel, addr = self.accept()
        return self.handlerClass(channel, addr)

    def handle_close(self):
        '''
        Function for handling close. Called when the socket is closed.
        '''
        self.disconnect()

    def handle_error(self):
        '''
        Method for handling uncaptured errors.
        '''
        t, err, tbinfo = asyncore.compact_traceback()[1:]
        self.onError(Exception("%s:%s\n%s"
                                % (t, err, tbinfo[1:-1].replace("] [", "\n"))))
        if isinstance(err, socket.error):
            if connection.closingSocketError(err):
                pass
            elif connection.minorSocketError(err):
                return
            else:
                self.onError(connection.ConnectionError(
                                            connection.processSocketError(err)))
        self.disconnect()

    def disconnect(self):
        '''
        Stops the server from listening.
        '''
        try:
            self.onClose()
            if not self is None:
                self.close()
        except socket.error, err:
            self.onError(err)
        finally:
            self.socket = None

    def onClose(self):
        '''
        Function called when socket is closed.
        '''
        pass

    def onError(self, exception):
        '''
        Function called when error occurs.

        :param exception: Exception to handle with
        :type exception: Exception
        '''
        raise exception

