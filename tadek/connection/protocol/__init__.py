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

from xml.etree import cElementTree as etree

import message
from message import *
from extension import *

__all__ = ["create", "parse"]

def create(type, target, name, **params):
    '''
    Creates an instance representing a message of given type, target, name with
    the specified parameters.
    '''
    msgcls = message.getMessageClass(type, target, name, *params)
    return msgcls(**params)


# Valid XML control characters
_XML_VALID_CTRLS = ('\t', '\n', '\r')

def parse(data, defaultClass=None):
    '''
    Parses the given message data and returns an instance representing
    the message.
    '''
    try:
        msg = etree.fromstring(data)
    except SyntaxError:
        # The message contains invalid XML characters
        msg = etree.fromstring(''.join([c for c in data 
                                    if ord(c) > 31 or c in _XML_VALID_CTRLS]))
    msg = msg[0]
    id = int(msg.get("id"))
    type = msg.tag
    target = msg.findtext("target")
    name = msg.findtext("name")
    elems = {}
    for elem in msg.find("params").getchildren():
        elems[elem.tag] = elem
    try:
        msgcls = message.getMessageClass(type, target, name, *elems)
        params = {}
        for nm, elem in elems.iteritems():
            param = msgcls.getParam(nm)
            params[nm] = param.unmarshal(elem)
        msg = msgcls(**params)
    except (message.UnsupportedMessageError, message.ParameterError):
        if defaultClass is None or defaultClass.type != type:
            raise UnsupportedMessageError(type, target, name, *elems)
        params = {}
        for nm in defaultClass.getParams():
            param = defaultClass.getParam(nm)
            params[nm] = param.unmarshal(elems[nm])
        msg = defaultClass(target, name, **params)
    msg.id = id
    return msg

