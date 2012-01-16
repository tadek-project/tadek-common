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

from tadek.core import utils
from tadek.core.structs import FileDetails
from tadek.engine import channels
from tadek.engine import testresult

__all__ = ["XmlChannel"]

ROOT_ELEMENT = "results"

_STEP_FUNC_POS = 2
_STEP_ARGS_POS = 4
_DEVICE_STATUS_POS = 1
_DEVICE_TIME_POS = 3

def _subElement(parent, tag, text=None, pos=None):
    '''
    Creates a tree subelement of the given tag name and text.
    '''
    element = parent.makeelement(tag, {})
    if text is not None:
        element.text = utils.decode(text)
    if pos is None:
        parent.append(element)
    else:
        parent.insert(pos, element)
    return element


class XmlChannelReadError(channels.TestResultChannelError):
    '''
    A base exception class for XML channel read errors.
    '''
    _MSG_FORMAT = "%s"

    def __init__(self, *tags):
        msg = self._MSG_FORMAT % '/'.join(tags)
        channels.TestResultChannelError.__init__(self, msg)

class XmlInvalidTagError(XmlChannelReadError):
    '''
    An exception class for notifying XML file format errors.
    '''
    _MSG_FORMAT = "Invalid tag: %s"

class XmlMissingTagError(XmlChannelReadError):
    '''
    An exception class for notifying XML file format errors.
    '''
    _MSG_FORMAT = "Missing tag: %s"


class _Device:
    '''
    A simple class for storing attributes of real devices.
    '''
    #: A device name
    name = None
    #: A device address-port pair
    address = (None, None)
    #: A device description
    description = None


class XmlChannel(channels.TestResultFileChannel):
    '''
    A channel class for writing/reading test results to/from XML files.
    '''
    #: Extension of an XML result file
    _fileExt = ".xml"

    #: Result classes tags names mapping
    _resultTagMaps = {
        testresult.TestStepResult: "step",
        testresult.TestCaseResult: "case",
        testresult.TestSuiteResult: "suite"
    }

    #: Result classes adding tree element methods mapping
    _resultMethodMaps = {
        testresult.TestStepResult: "_addStepElement",
        testresult.TestCaseResult: "_addCaseElement",
        testresult.TestSuiteResult: "_addSuiteElement"
    }

    def __init__(self, name, xslt=None, **params):
        channels.TestResultFileChannel.__init__(self, name, **params)
        self._xslt = xslt
        self._root = None

    def _addResultElement(self, result, parent):
        '''
        Adds a tree element for the given test result.
        '''
        element = _subElement(parent, self._resultTagMaps[result.__class__])
        _subElement(element, "id", result.id)
        _subElement(element, "path", result.path)
        if self.isVerbose():
            attrs = _subElement(element, "attributes")
            for name, value in result.attrs.iteritems():
                _subElement(attrs, str(name), value)
        _subElement(element, "devices")
        # FIXME: Do we need 'children' in step elements too?
        _subElement(element, "children")
        return element

    def _addStepElement(self, result, parent):
        '''
        Adds a tree element for the given test step result.
        '''
        element = self._addResultElement(result, parent)
        _subElement(element, "function", result.func, pos=_STEP_FUNC_POS)
        if self.isVerbose():
            args = _subElement(element, "arguments", pos=_STEP_ARGS_POS)
            for name, value in result.args.iteritems():
                _subElement(args, str(name), value)
        return element

    def _addCaseElement(self, result, parent):
        '''
        Adds a tree element for the given test case result.
        '''
        element = self._addResultElement(result, parent)
        # Add all its test steps
        children = element.find("children")
        for step in result.children:
            self._addStepElement(step, children)
        return element

    def _addSuiteElement(self, result, parent):
        '''
        Adds a tree element for the given test suite result.
        '''
        return self._addResultElement(result, parent)

    def _resultElement(self, result):
        '''
        Gets a tree element corresponding to the given test result.
        '''
        path = result.id.split('.')
        branch = [result]
        while result.parent:
            result = result.parent
            branch.insert(0, result)
        parent = self._root
        for result in branch:
            element = None
            for child in parent.findall(self._resultTagMaps[result.__class__]):
                if child.findtext("id") == result.id:
                    element = child
                    break
            if element is None:
                method = self._resultMethodMaps[result.__class__]
                element = getattr(self, method)(result, parent)
            parent = element.find("children")
        return element

    def _deviceElement(self, device, result):
        '''
        Gets a tree element corresponding the given device execution result.
        '''
        devices = self._resultElement(result).find("devices")
        for element in list(devices):
            if element.findtext("name") == device.name:
                return element
        element = _subElement(devices, "device")
        _subElement(element, "name", device.name)
        if self.isVerbose():
            _subElement(element, "date", utils.timeToString(device.date))
            _subElement(element, "address", device.address)
            _subElement(element, "port", device.port)
            _subElement(element, "description", device.description)
        return element

    def start(self, result):
        '''
        Sets up the XML channel.
        '''
        channels.TestResultFileChannel.start(self, result)
        self._root = etree.Element(ROOT_ELEMENT)

    def stop(self):
        '''
        Cleans up the XML channel.
        '''
        channels.TestResultFileChannel.stop(self)
        self._root = None

    def startTest(self, result, device):
        '''
        Processes a test start execution for the XML channel.
        '''
        channels.TestResultFileChannel.startTest(self, result, device)
        element = self._deviceElement(device, result)
        _subElement(element, "status", device.status, pos=_DEVICE_STATUS_POS)
        self.write()

    def stopTest(self, result, device):
        '''
        Processes a test stop execution for the XML channel.
        '''
        channels.TestResultFileChannel.stopTest(self, result, device)
        element = self._deviceElement(device, result)
        status = element.find("status")
        if status is None:
            status = _subElement(element, "status", pos=_DEVICE_STATUS_POS)
        status.text = device.status
        _subElement(element, "time", device.time, pos=_DEVICE_TIME_POS)
        if device.errors:
            errors = _subElement(element, "errors")
            for error in device.errors:
                _subElement(errors, "error", error)
        if device.cores:
            cores = _subElement(element, "cores")
            for core in device.cores:
                elem = _subElement(cores, "core")
                _subElement(elem, "path", core.path)
                if self.isVerbose():
                    _subElement(elem, "date",
                                ' '.join(utils.localTime(core.mtime)))
                    _subElement(elem, "size", core.size)
        self.write()

    def write(self):
        '''
        Writes the XML element tree to a related file.
        '''
        utils.saveXml(self._root, self.filePath(), xslt=self._xslt)

    def _readDeviceElement(self, element, result):
        '''
        Reads the given element representing a device test execution result.
        '''
        name = element.findtext("name")
        if name is None:
            raise XmlMissingTagError(element.tag, "name")
        status = element.findtext("status")
        if status is None:
            raise XmlMissingTagError(element.tag, "status")
        device = _Device()
        device.name = name
        port = element.findtext("port")
        if port:
            port = int(port)
        device.address = (element.findtext("address"), port)
        device.description = element.findtext("description")
        device = result.device(device)
        device.status = status
        date = element.findtext("date")
        if date:
            device.date = utils.timeFromString(date)
        time = element.findtext("time")
        if time:
            device.time = float(time)
        errors = element.find("errors")
        if errors is not None:
            for error in errors.findall("error"):
                device.errors.append(error.text)
        cores = element.find("cores")
        if cores is not None:
            device.cores = []
            for core in cores.findall("core"):
                path = core.findtext("path")
                if path is None:
                    raise XmlMissingTagError("core", "path")
                mtime = core.findtext("date") or 0.0
                mtime = mtime and utils.timeStampFromString(mtime)
                size = long(core.findtext("size") or 0)
                device.cores.append(FileDetails(path, mtime=mtime, size=size))

    def _readResultElement(self, element, parent):
        '''
        Reads the given element with a test result.
        '''
        for cls, tag in self._resultTagMaps.iteritems():
            if element.tag == tag:
                break
        if element.tag != tag:
            raise XmlInvalidTagError(element.tag)
        id = element.findtext("id")
        if id is None:
            raise XmlMissingTagError(tag, "id")
        path = element.findtext("path")
        if path is None:
            raise XmlMissingTagError(tag, "path")
        devices = element.find("devices")
        if devices is None:
            raise XmlMissingTagError(tag, "devices")
        if element.find("children") is None:
            raise XmlMissingTagError(tag, "children")
        result = cls(id=id, path=path, parent=parent)
        attrs = element.find("attributes")
        if attrs is not None:
            for attr in list(attrs):
                result.attrs[attr.tag] = attr.text
        for device in devices.findall("device"):
            self._readDeviceElement(device, result)
        return result

    def _readStepElement(self, element, parent):
        '''
        Reads a test step result from the given 
        '''
        func = element.findtext("function")
        if func is None:
            raise XmlMissingTagError(element.tag, "function")
        result = self._readResultElement(element, parent)
        result.func = func
        args = element.find("arguments")
        if args is not None:
            for arg in list(args):
                result.args[arg.tag] = arg.text
        return result

    def _readCaseElement(self, element, parent):
        '''
        Reads a test case result from the given 
        '''
        result = self._readResultElement(element, parent)
        for step in element.find("children").findall("step"):
            self._readStepElement(step, result)
        return result

    def _readSuiteElement(self, element, parent):
        '''
        Reads a test suite result from the given 
        '''
        result = self._readResultElement(element, parent)
        children = element.find("children")
        for child in list(children):
            if child.tag == "case":
                self._readCaseElement(child, result)
            elif child.tag == "suite":
                self._readSuiteElement(child, result)
            else:
                raise XmlInvalidTagError(element.tag, child.tag)
        return result

    def read(self, file):
        '''
        Reads the XML file with test results.
        '''
        channels.TestResultFileChannel.read(self, file)
        fd = open(self.filePath())
        try:
            self._root = etree.ElementTree(file=fd).getroot()
            if self._root.tag != ROOT_ELEMENT:
                raise XmlInvalidTagError(self._root.tag)
            container = testresult.TestResultContainer()
            for suite in self._root.findall("suite"):
                container.children.append(self._readSuiteElement(suite, None))
            return container
        finally:
            self._root = None
            fd.close()

channels.register(XmlChannel)

