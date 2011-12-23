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

import threading
from xml.etree import cElementTree as etree

from tadek.core import constants
from tadek.core.queue import QueueItem

from parameters import *

__all__ = ["UnsupportedMessageError", "DefaultRequest", "DefaultResponse"]

# Available messages types:
MSG_TYPE_REQUEST = u"request"
MSG_TYPE_RESPONSE = u"response"

# Available message targets
MSG_TARGET_ACCESSIBILITY = u"a11y"
MSG_TARGET_SYSTEM = u"sys"
MSG_TARGET_EXTENSION = u"ext"

# Available message names
MSG_NAME_GET = u"get"
MSG_NAME_SEARCH = u"search"
MSG_NAME_PUT = u"put"
MSG_NAME_EXEC = u"exec"
MSG_NAME_INFO = u"info"

# Available search methods
MHD_SEARCH_SIMPLE = u"simple"
MHD_SEARCH_BACKWARDS = u"backwards"
MHD_SEARCH_DEEP = u"deep"

#: The message terminator for the protocol
MSG_TERMINATOR = "<>"

#: A deafult id for messages
DEFAULT_MSG_ID = 0
ERROR_MSG_ID = -1
INFO_MSG_ID = -2

# Add constants to __all__
for nm, val in globals().items():
    if ("MSG_" in nm or nm.startswith("MHD_SEARCH_")):
        __all__.append(nm)
del nm, val

_id = DEFAULT_MSG_ID
_lock = threading.RLock()

def _getID():
    '''
    Gets an unique message id.
    '''
    global _id
    _lock.acquire()
    try:
        _id += 1
        id = _id
    finally:
        _lock.release()
    return id


class MessageClassConflictError(Exception):
    '''
    A class of exceptions raised when a message class is in conflict with other.
    '''
    # Message format
    _MSG_FORMAT = "Message class already registered: type=%(type)s, "\
                  "target=%(target)s, name=%(name)s, params=(%(params)s)"

    def __init__(self, type, target, name, *params):
        msg = self._MSG_FORMAT % {"type": type, "target": target, "name": name,
                                  "params": ", ".join(sorted(params))}
        Exception.__init__(self, msg)
        self.type = type
        self.target = target
        self.name = name
        self.params = params


class UnsupportedMessageError(Exception):
    '''
    A class of exceptions raised when a message is not supported.
    '''
    # Message format
    _MSG_FORMAT = "Unsupported message class: type=%(type)s, "\
                  "target=%(target)s, name=%(name)s, params=(%(params)s)"

    def __init__(self, type, target, name, *params):
        msg = self._MSG_FORMAT % {"type": type, "target": target, "name": name,
                                  "params": ", ".join(sorted(params))}
        Exception.__init__(self, msg)
        self.type = type
        self.target = target
        self.name = name
        self.params = params


class Message(QueueItem):
    '''
    A base class defining protocol messages.
    '''
    id = None
    # Message classification
    type = None
    target = None
    name = None

    @classmethod
    def getParam(cls, name):
        '''
        Gets a parameter instance of the given name
        '''
        param = getattr(cls, name, None)
        if param is None or not isinstance(param, MessageParameter):
            raise ParameterError("Invalid parameter name: %s", name)
        return param
    
    @classmethod
    def getParams(cls):
        '''
        Gets a list of parameter names for the message type.
        '''
        return [attr for attr in dir(cls)
                     if isinstance(getattr(cls, attr), MessageParameter)]

    def __init__(self, **params):
        if not self.type or not self.target or not self.name:
            raise NotImplementedError
        QueueItem.__init__(self, self.id if self.id is not None else _getID())
        # Validate the given parameters
        for name in self.getParams():
            param = self.getParam(name)
            try:
                value = params[name]
            except KeyError:
                raise ParameterError("Not specified parameter: %s" % name)
            else:
                param.validate(value)
                setattr(self, name, value)

    def marshal(self):
        '''
        Marshals the message.
        '''
        msg = etree.Element("tadek")
        elem = etree.SubElement(msg, self.type, id=str(self.id))
        etree.SubElement(elem, "target").text = self.target
        etree.SubElement(elem, "name").text = self.name
        params = etree.SubElement(elem, "params")
        for name in self.getParams():
            param = self.getParam(name)
            param.marshal(etree.SubElement(params, name), getattr(self, name))
        return etree.tostring(msg, constants.ENCODING)


class Request(Message):
    '''
    A base class for request messages.
    '''
    type = MSG_TYPE_REQUEST

class DefaultRequest(Request):
    '''
    A default class for request messages.
    '''
    def __init__(self, target, name, **params):
        self.target = target
        self.name = name
        Request.__init__(self, **params)


class Response(Message):
    '''
    A base class for response messages.
    '''
    id = DEFAULT_MSG_ID
    type = MSG_TYPE_RESPONSE
    # Parameters:
    status = BooleanParameter()

class DefaultResponse(Response):
    '''
    A default class for response messages.
    '''
    def __init__(self, target, name, **params):
        self.target = target
        self.name = name
        Response.__init__(self, **params)


_idx = 0
# The message class registry
_registry = {}

def _getRegistryKey(type, target, name, *params):
    '''
    Gets a registry key for a message class of the given attributes.
    '''
    key = '_'.join([type, target, name])
    if params:
        key = '__'.join([key, '_'.join(sorted(params))])
    return key


def getMessageClass(type, target, name, *params):
    '''
    Gets a message class of the given attributes.
    '''
    key = _getRegistryKey(type, target, name, *params)
    try:
        return _registry[key]
    except KeyError:
        raise UnsupportedMessageError(type, target, name, *params)


def _register(base, target, name, **attrs):
    '''
    Registers a new message class, a subclass of the given message base class
    and the specified attributes.
    '''
    global _idx
    _idx += 1
    if (not issubclass(base, Message) or
        base.type not in (MSG_TYPE_REQUEST, MSG_TYPE_RESPONSE)):
        raise TypeError("Invalid type of the message base class: %s" % base)
    attrs.update({"target": target, "name": name})
    parts = [name, target, base.type, str(_idx)]
    cls = type(''.join([str(s.capitalize()) for s in parts]), (base,), attrs)
    params = cls.getParams()
    key = _getRegistryKey(base.type, target, name, *params)
    if key in _registry:
        raise MessageClassConflictError(base.type, target, name, *params)
    _registry[key] = cls
    return cls


def registerRequest(target, name, **attrs):
    '''
    Registers a new request class of the specified attributes.
    '''
    return _register(Request, target, name, **attrs)


def registerResponse(target, name, **attrs):
    '''
    Registers a new response class of the specified attributes.
    '''
    return _register(Response, target, name, **attrs)


# Get accessibility
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_GET,
                path=PathParameter(),
                depth=IntParameter(),
                include=ListParameter(UnicodeParameter(), iname="attr")
)
registerResponse(MSG_TARGET_ACCESSIBILITY, MSG_NAME_GET,
                 accessible=AccessibleParameter()
)

# Search accessibility
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_SEARCH,
                path=PathParameter(),
                method=ChoiceParameter(MHD_SEARCH_SIMPLE,
                                       MHD_SEARCH_BACKWARDS,
                                       MHD_SEARCH_DEEP),
                predicates=ParameterSet(UnicodeParameter(),
                                        name=UnicodeParameter(),
                                        description=UnicodeParameter(),
                                        role=UnicodeParameter(),
                                        index=IntParameter(),
                                        count=IntParameter(),
                                        action=UnicodeParameter(),
                                        relation=UnicodeParameter(),
                                        state=UnicodeParameter(),
                                        text=UnicodeParameter(),
                                        nth=IntParameter())
)
registerResponse(MSG_TARGET_ACCESSIBILITY, MSG_NAME_SEARCH,
                 accessible=AccessibleParameter()
)

# Put accessibility text & value
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_PUT,
                path=PathParameter(),
                text=UnicodeParameter()
)
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_PUT,
                path=PathParameter(),
                value=FloatParameter()
)
registerResponse(MSG_TARGET_ACCESSIBILITY, MSG_NAME_PUT)

# Execute accessibility action, keyboard & mouse event
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_EXEC,
                path=PathParameter(),
                action=UnicodeParameter()
)
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_EXEC,
                path=PathParameter(),
                keycode=IntParameter(),
                modifiers=ListParameter(IntParameter(), iname="key")
)
registerRequest(MSG_TARGET_ACCESSIBILITY, MSG_NAME_EXEC,
                path=PathParameter(),
                button=UnicodeParameter(),
                event=UnicodeParameter(),
                coordinates=ListParameter(IntParameter(), length=2)
)
registerResponse(MSG_TARGET_ACCESSIBILITY, MSG_NAME_EXEC)

# Get system
registerRequest(MSG_TARGET_SYSTEM, MSG_NAME_GET,
                path=UnicodeParameter()
)
registerResponse(MSG_TARGET_SYSTEM, MSG_NAME_GET,
                 data=UnicodeParameter()
)

# Put system 
registerRequest(MSG_TARGET_SYSTEM, MSG_NAME_PUT,
                path=UnicodeParameter(),
                data=UnicodeParameter()
)
registerResponse(MSG_TARGET_SYSTEM, MSG_NAME_PUT)

# Execute system
registerRequest(MSG_TARGET_SYSTEM, MSG_NAME_EXEC,
                command=UnicodeParameter(),
                wait=BooleanParameter()
)
registerResponse(MSG_TARGET_SYSTEM, MSG_NAME_EXEC,
                 stdout=UnicodeParameter(),
                 stderr=UnicodeParameter()
)

# Info system
registerResponse(MSG_TARGET_SYSTEM, MSG_NAME_INFO,
                 id=INFO_MSG_ID,
                 version=UnicodeParameter(),
                 locale=UnicodeParameter(),
                 extensions=ListParameter(UnicodeParameter(), iname="name")
)

