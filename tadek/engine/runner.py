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

from contexts import DeviceContext
from testexec import *
from testresult import *
from tasker import *

JOIN_TIMEOUT = 1.0
STOP_TIMEOUT = 3.0

class DeviceRunner(threading.Thread):
    '''
    A class for controlling test executions on a particular device.
    '''
    def __init__(self, device, tasker, test, result):
        threading.Thread.__init__(self)
        self.device = device
        self._tasker = tasker
        self._test = test
        self._result = result

    def run(self):
        '''
        Runs tests in an execution context.
        '''
        context = DeviceContext(self.device, self._tasker)
        context.run(self._test, self._result)


class TestRunner(object):
    '''
    A class responsible for running test cases.
    '''
    def __init__(self, devices, tests, result=None):
        self._running = None
        self._test = TestExec()
        self._tasker = TestTasker(*tests)
        self.result = result or TestResult()
        self._execs = []
        for device in devices:
            self.addDevice(device)

    def addDevice(self, device):
        '''
        Adds the given device to the test runner.
        '''
        for te in self._execs:
            if te.device == device:
                return
        te = DeviceRunner(DeviceLock(device, self._test),
                          self._tasker, self._test, self.result)
        self._execs.append(te)
        if self._running is not None:
            if not self._running:
                te.device.lock()
            te.start()

    def removeDevice(self, device):
        '''
        Removes the given device from the test runner.
        '''
        found = False
        for te in self._execs:
            if te.device == device:
                found = True
                break
        if not found:
            return
        te.device.stop()
        self._execs.remove(te)

    def start(self):
        '''
        Runs a test cases on the given devices.
        '''
        if self._running is not None:
            return
        result = TestResultContainer()
        for r in self._tasker.results():
            result.children.append(r)
        self.result.start(result)
        for te in self._execs:
            te.start()
        self._running = True

    def stop(self):
        '''
        Stops a current test case execution.
        '''
        for te in self._execs:
            te.device.stop()
        self.join(STOP_TIMEOUT)
        # Stop the test result anyway
        self.result.stop()
        self._running = False

    def pause(self):
        '''
        Pauses a current test case execution.
        '''
        for te in self._execs:
            te.device.lock()
        self._running = False

    def resume(self):
        '''
        Resumes a current test case execution.
        '''
        for te in self._execs:
            te.device.unlock()
        self._running = True

    def join(self, timeout=None):
        '''
        Blocks until all test cases are executed or the given timeout occurs.
        '''
        if not self._running:
            return
        done = True
        if timeout is None:
            # Let interrupt this state
            while True:
                done = True
                for te in self._execs:
                    te.join(JOIN_TIMEOUT)
                    if te.isAlive():
                        done = False
                if done:
                    break
        else:
            for te in self._execs:
                te.join(timeout)
                if te.isAlive():
                    done = False
                    break
        if done:
            self.result.stop()
            self._running = False


class DeviceLock(object):
    '''
    A simple class that allows locking an access to wrapped devices.
    '''
    def __init__(self, device, test):
        self.device = device
        self._test = test
        self._lock = threading.Condition()
        self._locked = False
        self._shouldAbort = False

    def __getattr__(self, name):
        # TODO: Access to some of device attributes like name, address, etc.
        # shouldn't be locked here
        self._lock.acquire()
        try:
            while self._locked:
                self._lock.wait()
            self._test.abort(self.device.isConnected(), "Device disconnected")
            if self._shouldAbort:
                self._shouldAbort = False
                self._test.abortIf(True, "Execution stopped")
            return getattr(self.device, name)
        finally:
            self._lock.release()

    def __eq__(self, device):
        return self.id() == (device.id() if hasattr(device, "id")
                                         else id(device))

    def __ne__(self, device):
        return not (self == device)

    def id(self):
        '''
        Returns the id of a corresponding device.
        '''
        return id(self.device)

    def lock(self):
        '''
        Locks a corresponding device.
        '''
        self._lock.acquire()
        try:
            self._locked = True
        finally:
            self._lock.release()

    def unlock(self):
        '''
        Unlocks a corresponding device.
        '''
        self._lock.acquire()
        try:
            self._locked = False
            self._lock.notify()
        finally:
            self._lock.release()

    def stop(self):
        '''
        Stops a test execution on a corresponding device.
        '''
        self._lock.acquire()
        try:
            self._locked = False
            self._shouldAbort = True
            self._lock.notify()
        finally:
            self._lock.release()

