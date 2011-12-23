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

import time
import random

from tadek.core import devices
from tadek.engine.testdefs import *
from tadek.engine.testexec import *
from tadek.engine import testresult
from tadek.engine.testresult import channels
from tadek.connection import protocol

@testStep()
def step(test, device):
    pass

@testCase()
def case(test, device):
    pass

class Suite(TestSuite):
    pass

class FakeDevice(object):
    name = "FakeDevice"
    description = None
    address = devices.DEFAULT_IP, devices.DEFAULT_PORT
    locale = ''
    extensions = ()

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        self.ids = []
        self.connected = True

    def updateTestCaseIds(self, s):
        self.ids.append(s)

    def testCaseIds(self):
        return self.ids

    def isConnected(self):
        return self.connected

    def extension(self, name, **params):
        ext = protocol.getExtension(name)
        status, params = ext.response(**ext.request(**params))
        result = [status]
        for name in sorted(params):
            result.append(params[name])
        return tuple(result) if len(result) else status

TestDevice = FakeDevice

class FakeTestExec(TestExec):
    def __init__(self, context=None,
            casesCounters={}, stepsCounters={}, tearDownCounters={}):
        super(FakeTestExec, self).__init__(context)
        self.casesCounters = casesCounters
        self.stepsCounters = stepsCounters
        self.tearDownCounters = tearDownCounters

    def child(self):
        return self

class FakeTestResult(object):
    def startTest(self, result, device):
        pass

    def stopTest(self, result, device):
        pass

    def start(self, result):
        self.result = result

    def stop(self):
        self.result = None

class DummyTestResult(testresult.TestResultBase):
    message = ''

class DummyChannel(object):
    def __init__(self, name, enabled=True, verbose=False, **params):
        object.__init__(self)
        self.testBuffer = []
        self.name = name
        self._enabled = enabled
        self._verbose = verbose

    def isEnabled(self):
        return bool(self._enabled)

    def isVerbose(self):
        return bool(self._verbose)

    def start(self, result):
        pass

    def stop(self):
        pass

    def startTest(self, result, device):
        if hasattr(result, "message"):
            self.testBuffer.append(result.message)

    def stopTest(self, result, device):
        self.startTest(result, device)

class DummyConcurentChannel(DummyChannel):
    testBuffer = []

    def __init__(self, name, enabled=True, verbose=False, **params):
        DummyChannel.__init__(self, verbose)

    def startTest(self, dummy, device):
        message = len(self.testBuffer)
        time.sleep(0.005)
        self.testBuffer.append(message)

class DummyChannels(object):
    def __init__(self, coreDumps=False):
        self.scenario = []
        if coreDumps:
            self.CoreDumpsChannel = channels.CoreDumpsChannel
        else:
            self.CoreDumpsChannel = self.getDummyCoreDumps

    def getDummyCoreDumps(self):
        return DummyChannel("coredumps")

    def get(self):
        return self.scenario


_CONTENT_CHAR_SET = ''.join([chr(i) for i in xrange(ord('0'), ord('z')+1)])

def createRandomSizeFile(path, minSize=256, maxSize=4096):
    size = random.randint(256, 4096)
    fd = open(path, "wb")
    try:
        n = 0
        k = random.randint(len(_CONTENT_CHAR_SET)/4, len(_CONTENT_CHAR_SET)/2)
        while n < size:
            fd.write(''.join(random.sample(_CONTENT_CHAR_SET, k)))
            n += k
    finally:
        fd.close()

