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
from datetime import datetime

from tadek.core import log
from tadek.engine import channels

import testexec

__all__ = ["TestResult", "TestStepResult", "TestCaseResult",
           "TestSuiteResult", "TestResultContainer"]

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TestResult:
    '''
    A class to forward test results to result channels.
    '''
    def __init__(self):
        self._channels = channels.get()
        self._coreDumps = channels.CoreDumpsChannel()
        self._mutex = threading.RLock()

    def get(self, cls=None, name=None):
        '''
        Gets a list of channels used by the test result. If cls is provided then
        returns only channels of the given class.

        :param cls: A class of returned channels or None
        :type cls: TestResultChannel
        :param name: A name of a channel or None
        :type name: str
        :return: A list of channels
        :rtype: list
        '''
        channels = []
        for channel in self._channels:
            if ((not cls or isinstance(channel, cls)) and
                    (not name or channel.name == name)):
                channels.append(channel)
        return channels

    def start(self, result):
        '''
        Sends the start result through all enabled channels.

        :param result: A test result container to pass through channels
        :type result: TestResultContainer
        '''
        self._mutex.acquire()
        try:
            # Result channels
            for channel in self.get():
                try:
                    channel.start(result)
                except Exception, err:
                    log.exception(err)
                    self._channels.remove(channel)
            # Core dumps channel
            self._coreDumps.start(result)
        finally:
            self._mutex.release()

    def stop(self):
        '''
        Sends the stop result through all enabled channels.
        '''
        self._mutex.acquire()
        try:
            # Core dumps channel
            self._coreDumps.stop()
            self._coreDumps.setEnabled(False)
            # Result channels
            for channel in self.get():
                try:
                    channel.stop()
                except Exception, err:
                    log.exception(err)
                finally:
                    channel.setEnabled(False)
        finally:
            self._mutex.release()

    def startTest(self, result, device):
        '''
        Sends the start test result through all enabled channels.

        :param result: A test result to pass through channels
        :type result: TestResultBase
        :param device: A related device execution result
        :type device: DeviceExecResult
        '''
        self._mutex.acquire()
        try:
            execResult = result.device(device)
            execResult.status = testexec.STATUS_NOT_COMPLETED
            execResult.date = datetime.now()
            # Result channels
            for channel in self.get():
                if channel.isEnabled():
                    try:
                        channel.startTest(result, execResult)
                    except Exception, err:
                        log.exception(err)
                        channel.setEnabled(False)
            # Core dumps channel
            if self._coreDumps.isEnabled():
                try:
                    self._coreDumps.startTest(execResult, device)
                except Exception, err:
                    if isinstance(err, testexec.TestAbortError):
                        execResult.errors.append(testexec.errorInfo(err))
                        raise
                    log.exception(err)
                    self._coreDumps.setEnabled(False)
        finally:
            self._mutex.release()

    def stopTest(self, result, device):
        '''
        Sends the stop test result through all enabled channels.

        :param result: A test result to pass through channels
        :type result: TestResultBase
        :param device: A related device execution result
        :type device: DeviceExecResult
        '''
        self._mutex.acquire()
        try:
            execResult = result.device(device)
            dt = datetime.now() - execResult.date
            execResult.time = (dt.days*24*3600 + dt.seconds
                               + dt.microseconds/10.0**6)
            # Core dumps channel
            if self._coreDumps.isEnabled() and execResult.cores is not None:
                try:
                    self._coreDumps.stopTest(execResult, device)
                except Exception, err:
                    execResult.cores = []
                    if isinstance(err, testexec.TestAbortError):
                        execResult.errors.append(testexec.errorInfo(err))
                        execResult.status = err.status
                        raise
                    log.exception(err)
                    self._coreDumps.setEnabled(False)
            else:
                execResult.cores = []
            # Result channels
            for channel in self.get():
                if channel.isEnabled():
                    try:
                        channel.stopTest(result, execResult)
                    except Exception, err:
                        log.exception(err)
                        channel.setEnabled(False)
        finally:
            self._mutex.release()


class DeviceExecResult:
    '''
    A class to represent test results of device executions.
    '''
    #: An execution status of a test
    status = testexec.STATUS_NO_RUN
    #: An execution date of a test
    date = None
    #: An execution time of a test
    time = 0.0
    #: A returned result of a test
    result = None
    #: A list of core dumps
    cores = None

    def __init__(self, device):
        self._id = device.id() if hasattr(device, "id") else id(device)
        self.name = device.name
        self.description = device.description
        self.address, self.port = device.address
        self.errors = []

    def __eq__(self, device):
        return self.id() == (device.id() if hasattr(device, "id")
                                         else id(device))

    def id(self):
        '''
        Returns the id of a represented device.
        '''
        return self._id


class TestResultBase:
    '''
    A base class of test results.
    '''
    #: An id of the test
    id = None
    #: A system path to the test suite
    path = None
    #: A parent result
    parent = None

    def __init__(self, id=None, path=None, parent=None, attrs=None):
        self.attrs = attrs or {}
        self.children = []
        if parent:
            self.parent = parent
            parent.children.append(self)
            if id and '.' not in id:
                id = "%s.%s" % (parent.id, id) if parent.id else id
            if not path:
                path = parent.path
        self.id = id
        self.path = path
        self.devices = []

    def device(self, device):
        '''
        Returns the test execution result related the given device.
        '''
        if device not in self.devices:
            self.devices.append(DeviceExecResult(device))
        return self.devices[self.devices.index(device)]

    @property
    def status(self):
        '''
        Returns a summarized status for the test execution result.
        '''
        statuses = [d.status for d in self.devices]
        if not statuses:
            return testexec.STATUS_NO_RUN
        for s in (testexec.STATUS_ERROR, testexec.STATUS_NOT_COMPLETED,
                  testexec.STATUS_FAILED, testexec.STATUS_PASSED):
            if s in statuses:
                return s


class TestStepResult(TestResultBase):
    '''
    A class of test step results.
    '''
    def __init__(self, func=None, args=None, **kwargs):
        TestResultBase.__init__(self, **kwargs)
        self.func = func
        self.args = args or {}


class TestCaseResult(TestResultBase):
    '''
    A class of test case results.
    '''
    pass


class TestSuiteResult(TestResultBase):
    '''
    A class of test suite results.
    '''
    pass


class TestResultContainer:
    '''
    A class of test result containers.
    '''
    def __init__(self):
        self.children = []

    def __iter__(self):
        '''
        Returns an iterator that yields one test result per iteration.
        '''
        return iter(self.children)

