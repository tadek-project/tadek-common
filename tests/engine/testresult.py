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
import time
import shutil
import unittest
import threading

from tadek.core import settings
from tadek.engine import channels
from tadek.engine import testresult 
from tadek.engine.testresult import *

from engine import commons

__all__ = ["TestResultTest", "TestResultCoreDumpsTest"]


class OutputThread(threading.Thread):
    def __init__(self, testResult, value):
        threading.Thread.__init__(self)
        self._testResult = testResult
        self._value = value
        self._device = commons.FakeDevice()

    def run(self):
        self._testResult.start(None)
        for x in xrange(20):
            self._testResult.startTest(self._value, self._device)
            time.sleep(0.001)
            self._testResult.stopTest(self._value, self._device)
            time.sleep(0.001)


class TestResultTest(unittest.TestCase):
    def setUp(self):
        self.originalChannels = testresult.channels
        testresult.channels = commons.DummyChannels()

    def tearDown(self):
        testresult.channels = self.originalChannels

    def testIterChannels(self):
        channel1 = commons.DummyChannel("Test_0")
        channel2 = commons.DummyChannel("Test_1", False)
        testresult.channels.scenario = [channel1, channel2]
        result = TestResult()
        result.start(None)
        self.assertEqual([channel1, channel2], result.get())

    def testMultipleChannelsLog(self):
        device = commons.FakeDevice()
        channels = []
        for x in xrange(2):
            channel = commons.DummyChannel("Test_%d" % x, True)
            testresult.channels.scenario.append(channel)
            channels.append(channel)
        result = TestResult()
        result.start(None)
        caseResult = commons.DummyTestResult()
        caseResult.message = messageStart = "testStart"
        result.startTest(caseResult, device)
        caseResult.message = messageStop = "testStop"
        result.stopTest(caseResult, device)
        for channel in channels:
            self.assertEqual([messageStart, messageStop], channel.testBuffer)

    def testThreadSafety(self):
        channels = []
        threads = []
        for x in xrange(2):
            channel = commons.DummyConcurentChannel("Test_%d" % x, True)
            testresult.channels.scenario.append(channel)
            channels.append(channel)
        testRes = TestResult()
        for x in xrange(4):
            thread = OutputThread(testRes, TestCaseResult())
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        for channel in channels:
            self.assertTrue(channel.testBuffer)
            self.assertTrue(channel.testBuffer == sorted(channel.testBuffer))
            self.assertEqual(len(channel.testBuffer),
                                                len(set(channel.testBuffer)))


class TestResultCoreDumpsTest(unittest.TestCase):
    _TEST_CORE_DIR = os.path.abspath(os.path.join("tests", "_coredumps"))
    _TEST_CORE_FILE = "file.core"
    _TEST_CORE_PATTERN = ".+\.core"

    def setUp(self):
        self._origChannels = testresult.channels
        testresult.channels = commons.DummyChannels(coreDumps=True)
        self.testResult = TestResult()
        section = settings.get(channels.CONFIG_NAME,
                               self.testResult._coreDumps.name, force=True)
        self._origDirs = str(section["dirs"])
        section["dirs"] = self._TEST_CORE_DIR
        self._origPattern = str(section["pattern"])
        section["pattern"] = self._TEST_CORE_PATTERN
        if not os.path.exists(self._TEST_CORE_DIR):
            os.mkdir(self._TEST_CORE_DIR)
        self.testResult.start(None)

    def tearDown(self):
        self.testResult.stop()
        testresult.channels = self._origChannels
        section = settings.get(channels.CONFIG_NAME,
                               self.testResult._coreDumps.name, force=True)
        section["dirs"] = self._origDirs
        section["pattern"] = self._origPattern
        if os.path.exists(self._TEST_CORE_DIR):
            shutil.rmtree(self._TEST_CORE_DIR)

    def testEnableCoreDumpsChannel(self):
        result = TestCaseResult()
        device = commons.FakeDevice()
        self.testResult._coreDumps.setEnabled(False)
        self.testResult.startTest(result, device)
        core = os.path.join(self._TEST_CORE_DIR, self._TEST_CORE_FILE)
        commons.createRandomSizeFile(core)
        self.testResult._coreDumps.setEnabled(True)
        self.testResult.stopTest(result, device)
        execResult = result.device(device)
        self.failIf(execResult.cores)

    def testEnebledCoreDumpsChannel(self):
        result = TestCaseResult()
        device = commons.FakeDevice()
        self.testResult._coreDumps.setEnabled(True)
        self.testResult.startTest(result, device)
        core = os.path.join(self._TEST_CORE_DIR, self._TEST_CORE_FILE)
        commons.createRandomSizeFile(core)
        self.testResult.stopTest(result, device)
        execResult = result.device(device)
        self.failUnlessEqual(len(execResult.cores), 1)
        self.failUnless(core in execResult.cores)

    def testDisableCoreDumpsChannel(self):
        result = TestCaseResult()
        device = commons.FakeDevice()
        self.testResult._coreDumps.setEnabled(True)
        self.testResult.startTest(result, device)
        core = os.path.join(self._TEST_CORE_DIR, self._TEST_CORE_FILE)
        commons.createRandomSizeFile(core)
        self.testResult._coreDumps.setEnabled(False)
        self.testResult.stopTest(result, device)
        execResult = result.device(device)
        self.failIf(execResult.cores)

    def testDisabledCoreDumpsChannel(self):
        result = TestCaseResult()
        device = commons.FakeDevice()
        self.testResult._coreDumps.setEnabled(False)
        self.testResult.startTest(result, device)
        core = os.path.join(self._TEST_CORE_DIR, self._TEST_CORE_FILE)
        commons.createRandomSizeFile(core)
        self.testResult.stopTest(result, device)
        execResult = result.device(device)
        self.failIf(execResult.cores)


if __name__ == "__main__":
    unittest.main()

