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

import unittest
import threading

from commons import *

from tadek.core import location
from tadek.engine import runner
from tadek.engine.runner import TestRunner, DeviceLock, DeviceRunner
from tadek.engine.testresult import TestResultContainer
from tadek.engine.testexec import TestAbortError
from tadek.engine.tasker import *
import tadek.engine.tasker
# Make the below testcases module accessible
location.add("tests")

import tadek.testcases.testpkg3.testmdl31
from tadek.testcases.testpkg3.testmdl31 import printT
lock = threading.Lock()

__all__ = ["DeviceRunnerTest", "RunnerTest", "DeviceLockTest"]

def cleanSuite(suite):
    suite.__name__ = "suite"
    for elem in suite.__dict__.copy():
        if elem[:5]=="suite" or elem[:4]=="case":
            delattr(suite, elem)

def numOfTestSuites(tests):
    num = 0
    for t in tests:
        if isinstance(t, list):
            num += 1+numOfTestSuites(t)
    return num

def numOfTestCases(tests):
    num = 0
    for t in tests:
        if isinstance(t, list):
            num += numOfTestCases(t)
        elif not isinstance(t, str):
            num += 1
    return num

def numOfTestSteps(tests):
    num = 0
    for t in tests:
        if isinstance(t, list):
            num += numOfTestSteps(t)
        elif isinstance(t, tuple):
            num += len(t)
        elif not isinstance(t, str):
            num += 1
    return num

class SuiteTask(SuiteTask):
    def __init__(self, *args, **kwargs):
        super(SuiteTask, self).__init__(*args, **kwargs)
        self.test.task = self

class DeviceRunnerTest(unittest.TestCase):

    def checkSuitesCounts(self, suite, suiteCasesCounters):
        #print suite.__class__.__name__+" (suite):", suite.directCount(), suiteCasesCounters.get(suite, 0)
        self.failUnlessEqual(suite.directCount(), suiteCasesCounters.get(suite, 0))
        for s in suite:
            if isinstance(s[1], TestSuite):
                self.checkSuitesCounts(s[1], suiteCasesCounters)

    def runTest(self, nThreads, testSuites, notRanTestSuites=0,
                notRanTestCases=0, notRanTestSteps=0, detailedTests=True):
        '''
        Prepare and run unit tests for TestExec class.
        Parameter testSuites describes test suites and test cases.
        It is a tuple consisting of lists. Every list
        describes a suite and contains other lists (suites)
        or tuples. There is no need to create tuple for tests
        with only one suite without parent.
        Every tuple inside a list describes a single test case
        and contains numbers which describe test steps.
        Non negative number is a number of seconds for sleep
        function used inside steps.
        The first element of a list can be a string describing
        setUpSuite (F - fail, FT - fail this, A - abort)
        and setUpCase (FC, FCT, AC).
        The same letters used in the last element of a list
        describe tearDownSuite and tearDownCase.
        For simplicity for single step cases can there is
        no need to create tuple. Special steps are denoted
        as negative numbers (see class Suite in
        tests/testcases/testpkg3/testmdl31.py).
        Parameter nThreads is a number of devices (and threads).
        '''
        Suite = tadek.testcases.testpkg3.testmdl31.Suite
        cleanSuite(Suite)
        suites = []
        name = 1
        if not isinstance(testSuites, tuple):
            testSuites = (testSuites,)
        for tests in testSuites:
            class Suite(Suite):
                pass
            suites.append(Suite(name, tests))
            name += 1
        suiteTask = tadek.engine.tasker.SuiteTask
        tadek.engine.tasker.SuiteTask = SuiteTask
        tasker = TestTasker(*suites)
        tadek.engine.tasker.SuiteTask = suiteTask
        device = []
        deviceRunner = []
        casesCounters = {}
        stepsCounters = {}
        tearDownCounters= {}
        test = FakeTestExec(casesCounters=casesCounters,
            stepsCounters=stepsCounters, tearDownCounters=tearDownCounters)
        test.tasker = tasker
        test.ranTestSuites = 0
        test.ranTestCases = 0
        test.ranTestSteps = 0
        testResult = FakeTestResult()
        #print "Test:", self
        for i in xrange(nThreads):
            device.append(TestDevice())
            deviceRunner.append(DeviceRunner(
                device[i], tasker, test, testResult))
            deviceRunner[i].start()
        for i in xrange(nThreads):
            deviceRunner[i].join()

        #print "Ran test suites, not ran, total:", test.ranTestSuites, notRanTestSuites, numOfTestSuites(testSuites)
        #print "Ran test cases, not ran, total:", test.ranTestCases, notRanTestCases, numOfTestCases(testSuites)
        #print "Ran test steps, not ran, total:", test.ranTestSteps, notRanTestSteps, numOfTestSteps(testSuites)
        self.failUnlessEqual(test.ranTestSuites+notRanTestSuites, numOfTestSuites(testSuites))
        self.failUnlessEqual(test.ranTestCases+notRanTestCases, numOfTestCases(testSuites))
        self.failUnlessEqual(test.ranTestSteps+notRanTestSteps, numOfTestSteps(testSuites))
        if detailedTests:
            for (device, suite), count in tearDownCounters.iteritems():
                #print suite.__class__.__name__+" (tearDown):", count
                self.failUnlessEqual(count, 0)
            suiteCasesCounters = {}
            for (device, suite), count in casesCounters.iteritems():
                counter = suiteCasesCounters.get(suite, 0)
                suiteCasesCounters[suite] = counter+count
            for suite in suites:
                if isinstance(suite, TestSuite):
                    self.checkSuitesCounts(suite, suiteCasesCounters)

    def testRun1Threads1(self):
        self.runTest(1, [[[1, 0, 1], [1, 0], [0, 0]], 0])

    def testRun1Threads2(self):
        self.runTest(1, [[[1, 0, 1], [1, 0], [0, 0]], 0])

    def testRun1Threads3(self):
        self.runTest(1, [[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]])

    def testRun1Threads4(self):
        self.runTest(1, ([[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]], [[[1, 0, 1], [1, 0], [0, 0]], 0]))

    def testRun1Threads5(self):
        self.runTest(1, [[[-3, 1, 1], [1, 0], [0, 0]], 0], 3, 3, 3, detailedTests=False)

    def testRun1Threads6(self):
        self.runTest(1, [[[[[["F", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun1Threads7(self):
        self.runTest(1, [["F", [[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 9, 11, 11, detailedTests=False)

    def testRun1Threads8(self):
        self.runTest(1, [[[[["F", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 8, 10, 10, detailedTests=False)

    def testRun1Threads9(self):
        self.runTest(1, [[[[["FT", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 8, 10, 10, detailedTests=False)

    def testRun1Threads10(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "F"], [0]]]], 0])

    def testRun1Threads11(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "FT"], [0]]]], 0])

    def testRun1Threads12(self):
        self.runTest(1, [[[[["A", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 9, 11, 11, detailedTests=False)

    def testRun1Threads13(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "A"], [0]]]], 0], 5, 1, 1, detailedTests=False)

    def testRun1Threads14(self):
        self.runTest(1, [[[[["FC", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 8, 10, 10, detailedTests=False)

    def testRun1Threads14a(self):
        self.runTest(1, [[[[["FC7", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 7, 7, 7, detailedTests=False)

    def testRun1Threads15(self):
        self.runTest(1, [[[[["FCT", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 8, 10, 10, detailedTests=False)

    def testRun1Threads15a(self):
        self.runTest(1, [[[[["FCT7", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 7, 7, 7, detailedTests=False)

    def testRun1Threads16(self):
        self.runTest(1, [[[[["AC", [1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 9, 11, 11, detailedTests=False)

    def testRun1Threads17(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "FC"], [0]]]], 0])

    def testRun1Threads18(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "FCT"], [0]]]], 0])

    def testRun1Threads19(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0], [1, 0], [0, 0], "AC"], [0]]]], 0], 9, 10, 10, detailedTests=False)

    def testRun1Threads20(self):
        self.runTest(1, [[[[[["F", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun1Threads21(self):
        self.runTest(1, [[[[[["FT", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun1Threads22(self):
        self.runTest(1, [[[[[["FC", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun1Threads23(self):
        self.runTest(1, [[[[[["FCT", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun1Threads24(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0, "F"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun1Threads25(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0, "FT"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun1Threads26(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0, "FC"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun1Threads27(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0, "FCT"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun1Threads28(self):
        self.runTest(1, [[[[[[1, 0, 1, 0, 0, 0, "AC"], [1, 0], [0, 0]], [0]]]], 0], 9, 10, 10, detailedTests=False)


    def testRun2ThreadsFails1(self):
        self.runTest(2, [[[[[["F", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], detailedTests=False)

    def testRun2ThreadsFails2(self):
        self.runTest(2, [[[[[["FT", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], detailedTests=False)

    def testRun2ThreadsFails3(self):
        self.runTest(2, [[[[[["FC", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun2ThreadsFails4(self):
        self.runTest(2, [[[[[["FCT", 1, 0, 1, 0, 0, 0], [1, 0], [0, 0]], [0]]]], 0], 6, 6, 6, detailedTests=False)

    def testRun2ThreadsFails5(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "F"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun2ThreadsFails6(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "FT"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun2ThreadsFails7(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "FC"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun2ThreadsFails8(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "FCT"], [1, 0], [0, 0]], [0]]]], 0])

    def testRun2ThreadsFails9(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "AC"], [1, 0], [0, 0]], [0]]]], 0], detailedTests=False)

    def testRun2ThreadsFails10(self):
        self.runTest(2, [[[[[[1, 0, 1, 0, 0, 0, "A"], [1, 0], [0, 0]], [0]]]], 0], detailedTests=False)


    def testRun2Threads1(self):
        self.runTest(2, [[[1, 0, 1], [1, 0], [0, 0]], 0])

    def testRun2Threads2(self):
        self.runTest(2, [[[1, 1, 1], [1, 0], [1, 1]], 1])

    def testRun2Threads3(self):
        self.runTest(2, [[[1, 0, 1], [-1, 2], [0, 0]], [1, [1, 0]], 2, [[1, 1], 0, 0]], detailedTests=False)

    def testRun2Threads4(self):
        self.runTest(2, [[[1, -1, 1], [1, 0], [0, 0]], 0], detailedTests=False)

    def testRun2Threads5(self):
        self.runTest(2, [[[1, -2, 1], [1, 0], [0, 0]], 0])

    def testRun2Threads6(self):
        self.runTest(2, ([[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]], [[[1, 0, 1], [1, 0], [0, 0]], 0]))

    def testRun2Threads7(self):
        self.runTest(2, ([0, [[-3]]], [[0, 0], [0, 0, 0]]), detailedTests=False)

    def testRun2Threads8(self):
        self.runTest(2, ([0, [[-4]]], [[0, 0], [0, 0, 0]]))


    def testRun3Threads1(self):
        self.runTest(3, [[[1, 0, 1], [1, 0], [0, 0]], 0])

    def testRun3Threads2(self):
        self.runTest(3, [[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]])

    def testRun3Threads3(self):
        self.runTest(3, ([[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]], [[[1, 0, 1], [1, 0], [0, 0]], 0]))

    def testRun3Threads4(self):
        self.runTest(3, ([[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]], [[[1, 0, 1], [1, 0], [0, 0]], 0],
            [[[1, 0, 1], [1, 2], [0, 0]], [1, [-3, 0]], 0, [[1, 1], 0, 0]], [[[1, 0, 1], [1, 0], [0, 0]], [-3, [1, 0]], 0, [[1, -3], -4, 10]]), detailedTests=False)


    def testRun4Threads1(self):
        self.runTest(4, [[[1, 1, 1], [1, 0], [0, 0]], 0])

    def testRun4Threads2(self):
        self.runTest(4, [[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 0]], 0, [[1, 1], 0, 0]])


    def testRun5Threads1(self):
        self.runTest(5, [[[1, 2, 1], [1, 0], [0, 0]], 0])

    def testRun5Threads2(self):
        self.runTest(5, [[[1, 0, 1], [1, 0], [0, 0]], [1, [1, -1]], 0, [[-1, 1], 0, 0]], detailedTests=False)

    def testRun5Threads3(self):
        self.runTest(5, [[[1, 0, 1], [1, 0], [0, 0]], [1, [1, 2]], 0, [[1, 2, 3, 0, 1, 3, 1], 0, 0]])

    def testRun5Threads4(self):
        self.runTest(5, ([0, [[-4]]], [[0, 0], [0, 0, 0]]))

    def testRun5Threads5(self):
        self.runTest(5, [[-3]], detailedTests=False)

    def testRun5Threads6(self):
        self.runTest(5, ([[[[-3]]], 1], [[-3, 1, [1, -3, -3]]]), detailedTests=False)

    def testRun5Threads7(self):
        self.runTest(5, [-3], detailedTests=False)

    def testRun5Threads8(self):
        self.runTest(5, [-4])


    def testRunFail(self):
        self.runTest(1, ([0], [0, [(0, -11, 1), 0], [0, (1, 0, -11, 1)]]), 3, 2, 4, detailedTests=False)

    def testRunFailThis(self):
        self.runTest(1, ([0], [0, [(0, -12, 1), 0], [0, (0, 0, -12, 1)]]), 3, 2, 2, detailedTests=False)

    def testRunAbort(self):
        self.runTest(1, [0, [(0, 0, -13, 1)], [[0]]], 4, 2, 3, detailedTests=False)


class RunnerTest(unittest.TestCase):
    '''
    Main Runner test class.
    '''
    def testCreate(self):
        devices = (FakeDevice("d1"),
            FakeDevice("d2"),
            FakeDevice("d3"))
        result = FakeTestResult()
        runner = TestRunner(
            devices,
            (case, case),
            result)
        self.assertEqual(runner.result, result)
        self.assertEqual(len(runner._execs), len(devices))

    def testAddDevice(self):
        devices = []
        runner = TestRunner((), ())
        devices = (FakeDevice(),
            FakeDevice())
        for i, device in enumerate(devices):
            runner.addDevice(device)
            self.assertEqual(len(runner._execs), i+1)

    def testRemoveDevice(self):
        devices = (FakeDevice("d1"),
            FakeDevice("d2"),
            FakeDevice("d3"))
        runner = TestRunner(
            devices,
            (case, case),
            FakeTestResult)
        self.assertEqual(len(runner._execs), len(devices))
        for i, device in enumerate(devices):
            runner.removeDevice(device)
            self.assertEqual(len(devices)-i-1, len(runner._execs))

    def testStart(self):
        result = FakeTestResult()
        runner = TestRunner(
            (FakeDevice(),),
            (case,),
            result)
        runner.start()
        self.assertTrue(runner._running)
        runner.join()
        self.assertFalse(runner._running)

    def testStop(self):
        result = FakeTestResult()
        runner = TestRunner(
            (FakeDevice(),),
            (case,),
            result)
        runner.start()
        self.assertTrue(runner._running)
        runner.stop()
        self.assertFalse(runner._running)

    def testPauseResume(self):
        result = FakeTestResult()
        runner = TestRunner(
            (FakeDevice(),),
            (case,),
            result)
        runner.start()
        self.assertTrue(runner._running)
        result = runner.pause()
        self.assertFalse(runner._running)
        runner.resume()
        self.assertTrue(runner._running)
        runner.stop()
        self.assertFalse(runner._running)

    def testStartStopResult(self):
        result = FakeTestResult()
        runner = TestRunner(
            (FakeDevice(),),
            (case,),
            result)
        runner.start()
        self.assertTrue(runner._running)
        result = runner.result.result
        self.failUnless(result and isinstance(result, TestResultContainer))
        runner.stop()
        result = runner.result.result
        self.failIf(result)


class DeviceLockTest(unittest.TestCase):
    '''
    Main DeviceLock test class.
    '''
    def testCreate(self):
        device = FakeDevice("d1")
        devLock = DeviceLock(device, FakeTestExec())
        self.assertFalse(devLock._locked)
        self.assertFalse(devLock._shouldAbort)

    def testEqual(self):
        device = FakeDevice("d1")
        devLock = DeviceLock(device, FakeTestExec())
        self.assertTrue(devLock==device)

    def testGetattr(self):
        device = FakeDevice("d1")
        devLock = DeviceLock(device, FakeTestExec())
        box = {"TestName": "TestValue"}
        device.box = box
        self.assertEqual(box, devLock.box)
        device.connected = False
        try:
            devLock.box
        except TestAbortError, err:
            self.failUnlessEqual(str(err), "Device disconnected")
        except:
            self.failIf(True)
        else:
            self.failIf(True)
        device.connected = True
        devLock.stop()
        try:
            devLock.box
        except TestAbortError, err:
            self.failUnlessEqual(str(err), "Execution stopped")
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testLockUnlock(self):
        device = FakeDevice("d1")
        devLock = DeviceLock(device, FakeTestExec())
        devLock.lock()
        self.assertTrue(devLock._locked)
        devLock.unlock()
        self.assertFalse(devLock._locked)

    def testStop(self):
        device = FakeDevice("d1")
        devLock = DeviceLock(device, FakeTestExec())
        devLock.stop()
        self.assertFalse(devLock._locked)
        self.assertTrue(devLock._shouldAbort)

if __name__ == "__main__":
    unittest.main()

