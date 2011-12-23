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

from sys import stderr

from tadek.core import utils
from tadek.engine.testresult import TestStepResult, TestCaseResult
from tadek.engine.channels import register, TestResultChannel

__all__ = ["StreamChannel"]

DEVICE_VERBOSE_PARAMS = (
    "status",
    "name",
    "time",
    "date",
    "address",
    "port",
    "description"
)

#Device params post processing functions:
DEVICE_PARAMS_SAVE_PPF = {
    "date": utils.timeToString
}
DEVICE_PARAMS_LOAD_PPF = {
    "date": utils.timeFromString,
    "time": float
}

# Line separators:
MINOR_SEPARATOR = 10 * "- "
MAJOR_SEPARATOR = 80 * '-'

class StreamChannel(TestResultChannel):
    '''
    A class for writing test results to a stream.
    '''
    def __init__(self, name, stream=stderr, encoding=None, **params):
        TestResultChannel.__init__(self, name, **params)
        self._stream = stream
        self._encoding = encoding or getattr(self._stream, "encoding", None)
        self._lastParent = None

    def _collectCores(self, result, device):
        '''
        Collects core dumps from the given test result and all its descendants.
        '''
        cores = []
        if device.cores:
            cores.extend(device.cores[:])
        if result.children:
            for child in result.children:
                if child.devices:
                    for dev in child.devices:
                        if dev == device and dev.cores:
                            cores.extend(dev.cores[:])
        cores.sort(cmp=lambda x, y: cmp(x.mtime, y.mtime))
        return cores

    def _createSimpleElement(self, result, device, prefix):
        '''
        Creates element used to print information for not verbose mode.
        '''
        elem = []
        line = u"[%s]" % device.name
        line += u" "+result.id
        if prefix.startswith("STOP"):
            line += u": %s" % device.status
            if isinstance(result, TestCaseResult):
                cores = self._collectCores(result, device)
            else:
                cores = device.cores
            if cores:
                line += u'\n'
                for core in cores:
                    line += u"\tCore file: " + core.path + u'\n'
            if device.errors:
                line += u'\n'
        line += u'\n'.join([utils.decode(err) for err in device.errors])
        elem.append((line,))
        return elem

    def _createElement(self, result, device, prefix):
        '''
        Creates element used to print information for verbose mode.
        '''
        elem = []
        elem.append(("common", "class", result.__class__.__name__[:-6]))
        elem.append(("common", "id", result.id))
        elem.append(("common", "path", result.path))
        if isinstance(result, TestStepResult):
            elem.append(("common", "func", result.func))
            for arg, value in result.args.iteritems():
                elem.append(("arguments", str(arg), str(value)))
        for attr, value in result.attrs.iteritems():
            elem.append(("attributes", utils.decode(attr), utils.decode(value)))
        elem.append((MINOR_SEPARATOR, ))
        for param in DEVICE_VERBOSE_PARAMS:
            elem.append(("device", param,
                         DEVICE_PARAMS_SAVE_PPF.get(param, str)(
                                                    getattr(device, param))))
        if prefix.startswith("STOP") and device.cores:
            for core in device.cores:
                elem.append(''.join(["Core file: ", core.path, "\n\tsize: ",
                                    utils.sizeToString(core.size), "\n\tdate: ",
                                    ' '.join(utils.localTime(core.mtime))]))
        for error in device.errors:
            elem.append(("error" + utils.decode(error),))
        elem.append((MINOR_SEPARATOR, ))
        return elem

    def _format(self, *items):
        '''
        Formats the given line items.
        '''
        return u"->\t".join(items)

    def _writeResult(self, prefix, result, device):
        '''
        Writes into the stream the given test result.
        '''
        if (not isinstance(result, TestStepResult) or
            result.parent != self._lastParent) and self.isVerbose():
            self.write(MAJOR_SEPARATOR + '\n')
        if self.isVerbose():
            elem = self._createElement(result, device, prefix)
        elif not isinstance(result, TestStepResult):
            elem = self._createSimpleElement(result, device, prefix)
        for line in elem:
            string = self._format(prefix, *[f if f else '' for f in line])
            self.write(u"%s\n" % string)
        self._lastParent = result.parent

    def startTest(self, result, device):
        '''
        Processes a test start execution for the stream channel.
        '''
        TestResultChannel.startTest(self, result, device)
        if self.isVerbose():
            self.write('\n')
        elif isinstance(result, TestStepResult):
            # Don't write the test step result
            return
        self._writeResult("START", result, device)

    def stopTest(self, result, device):
        '''
        Processes a test stop execution for the stream channel.
        '''
        TestResultChannel.stopTest(self, result, device)
        if self.isVerbose() or not isinstance(result, TestStepResult):
            self._writeResult("STOP ", result, device)

    def write(self, data):
        '''
        Writes the given data to the stream.
        '''
        self._stream.write(utils.encode(data, self._encoding))

register(StreamChannel)

