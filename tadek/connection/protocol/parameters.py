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

from tadek.core.accessible import Path, Accessible
from tadek.core.utils import decode

__all__ = ["ParameterError", "MessageParameter",
           "UnicodeParameter", "IntParameter", "FloatParameter",
           "BooleanParameter", "ListParameter", "ChoiceParameter",
           "ParameterSet", "PathParameter", "AccessibleParameter"]

class ParameterError(Exception):
    '''
    A class of exceptions raised by massage parameter classes.
    '''
    _MSG_FORMAT = "Illegal value type: %s"

    def __init__(self, msg=None, value=None):
        msg = msg or self._MSG_FORMAT
        if value is not None:
            msg %= type(value).__name__
        Exception.__init__(self, msg)
    


class MessageParameter(object):
    '''
    A base class for message parameters.
    '''
    # The type of a message parameter
    type = None

    def validate(self, value):
        if not isinstance(value, self.type):
            raise ParameterError(value=value)

    def marshal(self, element, value):
        element.text = decode(value)

    def unmarshal(self, element):
        return self.type(element.text)


class UnicodeParameter(MessageParameter):
    '''
    A class of unicode message parameters.
    '''
    type = unicode

    def validate(self, value):
        if not isinstance(value, basestring):
            raise ParameterError(value=value)

    def unmarshal(self, element):
        return self.type(element.text) if element.text else u''


class IntParameter(MessageParameter):
    '''
    A class of integer message parameters.
    '''
    type = int

    def validate(self, value):
        if not isinstance(value, int) and not isinstance(value, long):
            raise ParameterError(value=value)


class FloatParameter(MessageParameter):
    '''
    A class of float message parameters.
    '''
    type = float


class BooleanParameter(MessageParameter):
    '''
    A message boolen parameter class.
    '''
    type = bool

    def unmarshal(self, element):
        value = element.text
        if value and value.lower() == "true":
            return True
        elif value and value.lower() == "false":
            return False
        raise ParameterError(value=value)


class ListParameter(MessageParameter):
    '''
    A class of list or tuple message parameters.
    '''
    type = tuple

    def __init__(self, iparam, iname="item", length=None):
        MessageParameter.__init__(self)
        if not isinstance(iparam, MessageParameter):
            raise ParameterError("Invalid parameter type: %s", iparam)
        self._iname = iname
        self._iparam = iparam
        self._length = length

    def validate(self, value):
        if not isinstance(value, tuple) and not isinstance(value, list):
            raise ParameterError(value=value)
        if self._length is not None and len(value) != self._length:
            raise ParameterError("Invalid list length: %d" % len(value))
        for item in value:
            self._iparam.validate(item)

    def marshal(self, element, value):
        for item in value:
            self._iparam.marshal(etree.SubElement(element, self._iname), item)

    def unmarshal(self, element):
        value = []
        for item in element.getchildren():
            if item.tag != self._iname:
                raise ParameterError("Invalid list item name: %s" % item.tag)
            value.append(self._iparam.unmarshal(item))
        return self.type(value)


class ChoiceParameter(UnicodeParameter):
    '''
    A class of choice message parameters.
    '''
    def __init__(self, *choices):
        UnicodeParameter.__init__(self)
        if not choices:
            raise ParameterError("At least one choice value required")
        for choice in choices:
            if not isinstance(choice, self.type):
                raise ParameterError("Illegal choice value type: %s", choice)
        self._choices = choices

    def validate(self, value):
        UnicodeParameter.validate(self, value)
        if value not in self._choices:
            ParameterError("Illegal choice value: %s" % value)


class ParameterSet(MessageParameter):
    '''
    A class for representing sets of optional parameters.
    '''
    type = dict

    def __init__(self, default, **params):
        if not isinstance(default, MessageParameter):
            raise ParameterError("Invalid default parameter type: %s", default)
        for param in params.itervalues():
            if not isinstance(param, MessageParameter):
                raise ParameterError("Invalid parameter type: %s", param)
        MessageParameter.__init__(self)
        self._default = default
        self._params = params

    def validate(self, value):
        MessageParameter.validate(self, value)
        for name, val in value.iteritems():
            if name in self._params:
                self._params[name].validate(val)
            else:
                self._default.validate(val)

    def marshal(self, element, value):
        for name, val in value.iteritems():
            if name in self._params:
                self._params[name].marshal(etree.SubElement(element, name), val)
            else:
                self._default.marshal(etree.SubElement(element, name), val)

    def unmarshal(self, element):
        params = {}
        for param in element.getchildren():
            name = param.tag
            if name in self._params:
                params[name] = self._params[name].unmarshal(param)
            else:
                params[name] = self._default.unmarshal(param)
        return params


class PathParameter(MessageParameter):
    '''
    A class of accessible path message parameters.
    '''
    type = Path

    def marshal(self, element, value):
        value.marshal(element)

    def unmarshal(self, element):
        return self.type.unmarshal(element)


class AccessibleParameter(MessageParameter):
    '''
    A class for representing accessible message parameters
    '''
    type = Accessible

    def marshal(self, element, value):
        elem = value.marshal()
        element[:] = elem.getchildren()

    def unmarshal(self, element):
        return self.type.unmarshal(element)

