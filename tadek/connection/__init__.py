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
import errno
import socket
import asyncore

#: Errors that should be ignored
MINOR_ERRNO = (
    "EAGAIN",
    "EWOULDBLOCK",
    "WSAEAGAIN",
    "WSAEWOULDBLOCK",
    "WSAEINVAL"
)
MINOR_ERRNO = tuple([getattr(errno, e) for e in MINOR_ERRNO
                                       if e in errno.errorcode.values()])

#: Errors that close a connection silently
CLOSING_ERRNO = (
    "ENOTCONN",
    "ECONNRESET",
    "ESHUTDOWN",
    "ECONNABORTED",
    "WSAENOTCONN",
    "WSAECONNRESET",
    "WSAESHUTDOWN",
    "WSAECONNABORTED"
)
CLOSING_ERRNO = tuple([getattr(errno, e) for e in CLOSING_ERRNO
                                       if e in errno.errorcode.values()])

def minorSocketError(error):
    '''
    Checks if the given socket error can be ignored.
    '''
    return error[0] in MINOR_ERRNO

def closingSocketError(error):
    '''
    Checks if the given socket error closes a connection.
    '''
    return error[0] in CLOSING_ERRNO

def processSocketError(error):
    '''
    Processes the given socket error and returns its string representation.
    '''
    description = error[1] if len(error.args) > 1 else os.strerror(error[0])
    return u"[Errno %d] %s" % (error[0], description)
 

class ConnectionError(Exception):
    '''
    Class representing errors which may occur during socket operations.
    '''
    pass

def run():
    '''
    Starts asyncore loop, which ends when all channels are closed.
    '''
    try:
        asyncore.loop(1)
    except socket.error, err:
        raise ConnectionError(processSocketError(err))

