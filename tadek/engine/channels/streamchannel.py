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

import re
import sys
import datetime

from tadek.core import utils
from tadek.engine.testresult import TestStepResult, TestCaseResult
from tadek.engine.channels import register, TestResultChannel

__all__ = ["StreamChannel"]

#: A format of a mapping (dict) key
MAPPING_KEY_SYMBOL = u"#key"
#: A format of a mapping (dict) value
MAPPING_VALUE_SYMBOL = u"#value"

def _convertDate(dt):
    '''
    Coverts the given date to the text representation.
    '''
    if isinstance(dt, (float, int, long)):
        return utils.DATE_TIME_SEPARATOR.join(utils.localTime(dt))
    return utils.timeToString(dt)

def _convertTime(dt):
    '''
    Coverts the given time to the text representation.
    '''
    if isinstance(dt, (float, int, long)):
        return utils.localTime(dt)[1]
    return utils.timeToString(dt).split(utils.DATE_TIME_SEPARATOR)[1]

#:Default extra conversion types
_CONVERSION_TYPES = {
    'U': utils.decode,
    'D': _convertDate,
    'T': _convertTime,
    'R': utils.runTimeToString,
    'S': utils.sizeToString
}

def _placeHolders(formatter):
    '''
    Finds in the given formatter all place holders and related converion types.
    '''
    return re.findall("%\((#?\w+?|device\.\w+?)\)([a-zA-Z])", formatter)

def _placeHoldersNames(formatter):
    '''
    Returns a set of unique names of place holders in the given formatter.
    '''
    return set([n for n, t in _placeHolders(formatter)])

def _formatData(formatter, attrs, extras):
    '''
    Formats output data from the given formatter and attributes using the extra
    conversion types.
    '''
    extras.update(_CONVERSION_TYPES)
    for name, type in _placeHolders(formatter):
        if type not in extras:
            continue
        formatter = formatter.replace(u"%%(%s)%s" % (name, type),
                                      extras[type](attrs[name]))
    return formatter % attrs
    

class StreamChannel(TestResultChannel):
    '''
    A class for writing test results to a stream.
    '''
    #: A text representation of the separator
    SEPARATOR = 20 * u'-'

    #: Extra conversion types
    _conversionTypes = {}

    #: Output formats for the channel simple mode
    _simpleFormats = {
        # Test start header (required)
        "start" : u"%(date)T [%(device.name)U] START %(id)s\n",
        # Test step (required)
        "step"  : u'',
        # Test case (required)
        "case"  : u'',
        # Test suite (required)
        "suite" : u'',
        # Test stop header (required)
        "stop"  : u"%(date)T [%(device.name)U] STOP  %(id)s "
                   "[%(device.status)s]\n",
        # Core dumps (required)
        #         (core dump, separator, prefix, suffix) 
        "cores" : (u"Core dump: %(path)s", u"\n\t", u'\t', u'\n'),
        # Errors (required)
        #         (error, separator, prefix, suffix)
        "errors": (u"%s", u'\n', u'', u'\n'),
    }

    #: Output formats for the channel simple mode
    _verboseFormats = {
        # Test start header (required)
        "start": u"%(date)D %(separator)s START %(separator)s\n"
                 u"\t%(device.name)U: [%(device.address)s] "
                 u"%(device.description)U\n",
        # Test step (required)
        "step" : u"\tTest step ID: %(id)s\n"
                  "\tFunction: %(func)s%(args)s\n"
                  "\tPath: %(path)s%(attrs)s\n",
        # Test case (required)
        "case" : u"\tTest case ID: %(id)s\n"
                  "\tPath: %(path)s%(attrs)s\n",
        # Test suite (required)
        "suite": u"\tTest suite ID: %(id)s\n"
                  "\tPath: %(path)s%(attrs)s\n",
        # Test attributes
        #        (attribute, separator, prefix, suffix)
        #        #key - a attribute name
        #        #value - a attribute value
        "attrs": (u"%(" + MAPPING_KEY_SYMBOL + u")s: %(" + MAPPING_VALUE_SYMBOL
                   + u")r", u"\n\t\t", u"\n\t\t", u''),
        # Test step arguments
        #        (argument, separator, prefix, suffix)
        #        #key - a argument name
        #        #value - a argument value
        "args" : (u"%(" + MAPPING_KEY_SYMBOL + u")s=%(" + MAPPING_VALUE_SYMBOL
                   + u")r", u", ", u'(', u')'),
        # Test stop header (required)
        "stop" : u"%(date)D %(separator)s STOP %(separator)s "
                 u"[%(device.status)s]\n\t%(device.name)U: "
                 u"[%(device.address)s] %(device.description)U\n",
        # Core dumps (required)
        #         (core dump, separator, prefix, suffix) 
        "cores" : (u"Core dump: %(mtime)D [%(path)s] %(size)S",
                   u"\n\t", u'\t', u'\n'),
        # Errors (required)
        #         (error, separator, prefix, suffix)
        "errors": (u"%s", u'\n', u'', u'\n'),
    }

    def __init__(self, name, stream=None, encoding=None, **params):
        TestResultChannel.__init__(self, name, **params)
        self._stream = stream or sys.stderr
        self._encoding = encoding or getattr(self._stream, "encoding", None)

    def _basicAttrs(self, device):
        '''
        Returns a dictionary with basic (pre-defineed) attributes.
        '''
        dt = device.date
        if device.time:
            dt += datetime.timedelta(seconds=device.time)
        return {
            "date": dt,
            "separator": self.SEPARATOR
        }

    def _deviceAttrs(self, device):
        '''
        Returns a dictionary with attributes of the given device result.
        '''
        attrs = {
            "device.name": device.name,
            "device.address": ':'.join([device.address, str(device.port)]),
            "device.description": device.description or '',
            "device.status": device.status,
            "device.date": device.date
        }
        if device.time:
            attrs["device.time"] = device.time
        attrs.update(self._basicAttrs(device))
        return attrs

    def _format(self, source, formatter, formatters, kwargs):
        '''
        Formats output data using the given formatters and the source object.
        '''
        if not formatter:
            return ''
        # Sequence formatter
        if isinstance(formatter, (tuple, list)):
            items = []
            formatter, separator, prefix, suffix = formatter
            holders = _placeHoldersNames(formatter)
            if MAPPING_KEY_SYMBOL in holders or MAPPING_VALUE_SYMBOL in holders:
                # Mapping (dict like sequence)
                for key in source:
                    attrs = {
                        MAPPING_KEY_SYMBOL: key,
                        MAPPING_VALUE_SYMBOL: source[key],
                    }
                    attrs.update(kwargs)
                    items.append(_formatData(formatter, attrs,
                                             self._conversionTypes))
            else:
                for item in source:
                    items.append(self._format(item, formatter,
                                              formatters, kwargs))
            if not items:
                return ''
            return prefix + separator.join(items) + suffix
        holders = _placeHoldersNames(formatter)
        if not holders:
            # There is no any named place holder
            return formatter % utils.decode(source)
        attrs = {}
        for name in holders:
            if hasattr(source, name):
                value = getattr(source, name)
                if name in formatters:
                    value = self._format(value, formatters[name],
                                         formatters, kwargs)
                attrs[name] = value
            else:
                # Unknown place holder
                attrs[name] = ''
        attrs.update(kwargs)
        return _formatData(formatter, attrs, self._conversionTypes)

    def _formatResult(self, result, formatters, attrs):
        '''
        Formats output data using the given formatters and the test result.
        '''
        name = result.__class__.__name__[4:-6].lower()
        return self._format(result, formatters[name], formatters, attrs)

    def startTest(self, result, device):
        '''
        Processes a test start execution for the stream channel.
        '''
        TestResultChannel.startTest(self, result, device)
        formatters = (self._verboseFormats if self.isVerbose()
                                           else self._simpleFormats)
        self.write(self._format(result, formatters["start"], formatters,
                                self._deviceAttrs(device)))
        self.write(self._formatResult(result, formatters,
                                      self._deviceAttrs(device)))

    def stopTest(self, result, device):
        '''
        Processes a test stop execution for the stream channel.
        '''
        TestResultChannel.stopTest(self, result, device)
        formatters = (self._verboseFormats if self.isVerbose()
                                           else self._simpleFormats)
        self.write(self._format(result, formatters["stop"], formatters,
                                self._deviceAttrs(device)))
        self.write(self._formatResult(result, formatters,
                                      self._deviceAttrs(device)))
        self.write(self._format(device.cores, formatters["cores"],
                                formatters, self._basicAttrs(device)))
        self.write(self._format(device.errors, formatters["errors"],
                                formatters, self._basicAttrs(device)))

    def write(self, data):
        '''
        Writes the given data to the stream.
        '''
        if data:
            self._stream.write(utils.encode(data, self._encoding))

register(StreamChannel)

