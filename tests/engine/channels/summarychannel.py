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

from engine.commons import *
from tadek.engine import channels
from tadek.engine.testexec import *
from tadek.engine.testresult import *
from tadek.engine.testresult import DeviceExecResult
from tadek.engine.runner import TestRunner
from tadek.engine.channels.summarychannel import SummaryChannel, \
                        COUNTER_N_TESTS, COUNTER_TESTS_RUN, COUNTER_CORE_DUMPS

__all__ = ["SummaryChannelTest"]

class SummaryChannelTest(unittest.TestCase):
    '''
    Main SummaryChannel test class.
    '''
    def setUp(self):
        self.device = FakeDevice("ExampleDevice")
        self.device.address = ("127.0.0.1", 1234)
        self.deviceResult = DeviceExecResult(self.device)
        self.deviceResult.status = "Passed"

        self.device1 = FakeDevice("ExampleDevice1")
        self.device1.address = ("127.0.0.1", 1235)
        self.deviceResult1 = DeviceExecResult(self.device1)
        self.deviceResult1.status = "Failed"

        self.caseResult = TestCaseResult()
        self.caseResult.devices = [self.deviceResult]

        self.caseResult1 = TestCaseResult()
        self.caseResult1.devices = [self.deviceResult1]

        self.caseResult2 = TestCaseResult()
        self.caseResult3 = TestCaseResult()

        self.suiteResult = TestSuiteResult()
        self.suiteResult.devices = [self.deviceResult, self.deviceResult1]
        self.suiteResult.children = [self.caseResult, self.caseResult1,
            self.caseResult2]
        self.suiteResult.parent = None

        self.caseResult.parent = self.suiteResult
        self.caseResult1.parent = self.suiteResult
        self.caseResult2.parent = self.suiteResult

    def testStartStopTest_Start2Tests(self):
        channel = SummaryChannel("summary")
        channel.start(self.suiteResult)
        channel.startTest(self.caseResult, self.deviceResult)
        channel.stopTest(self.caseResult, self.deviceResult)
        channel.startTest(self.caseResult1, self.deviceResult1)
        channel.startTest(self.caseResult2, self.deviceResult)
        channel.stop()
        summary = channel.getSummary()
        self.assertEqual(3, summary[COUNTER_N_TESTS])
        self.assertEqual(3, summary[COUNTER_TESTS_RUN])
        self.assertEqual(1, summary[STATUS_PASSED])
        self.assertEqual(0, summary[STATUS_FAILED])
        self.assertEqual(0, summary[STATUS_ERROR])
        self.assertEqual(2, summary[STATUS_NOT_COMPLETED])
        self.assertEqual(0, summary[COUNTER_CORE_DUMPS])

    def testStartStop3Tests(self):
        channel = SummaryChannel("summary")
        channel.start(self.suiteResult)
        channel.startTest(self.caseResult, self.deviceResult)
        channel.stopTest(self.caseResult, self.deviceResult)
        channel.startTest(self.caseResult1, self.deviceResult1)
        channel.stopTest(self.caseResult1, self.deviceResult1)
        channel.startTest(self.caseResult2, self.deviceResult)
        channel.stopTest(self.caseResult2, self.deviceResult)
        channel.stop()
        summary = channel.getSummary()
        self.assertEqual(3, summary[COUNTER_N_TESTS])
        self.assertEqual(3, summary[COUNTER_TESTS_RUN])
        self.assertEqual(2, summary[STATUS_PASSED])
        self.assertEqual(1, summary[STATUS_FAILED])
        self.assertEqual(0, summary[STATUS_ERROR])
        self.assertEqual(0, summary[STATUS_NOT_COMPLETED])
        self.assertEqual(0, summary[COUNTER_CORE_DUMPS])

    def testStartStopTest_CoreDumps(self):
        channel = SummaryChannel("summary")
        channel.start(self.caseResult)
        channel.startTest(self.caseResult, self.deviceResult)
        self.deviceResult.cores = ["core1", "core2", "core3"]
        channel.stopTest(self.caseResult, self.deviceResult)
        channel.stop()
        summary = channel.getSummary()
        self.assertEqual(1, summary[COUNTER_N_TESTS])
        self.assertEqual(1, summary[COUNTER_TESTS_RUN])
        self.assertEqual(1, summary[STATUS_PASSED])
        self.assertEqual(0, summary[STATUS_FAILED])
        self.assertEqual(0, summary[STATUS_ERROR])
        self.assertEqual(0, summary[STATUS_NOT_COMPLETED])
        self.assertEqual(len(self.deviceResult.cores),
                         summary[COUNTER_CORE_DUMPS])

if __name__ == "__main__":
    unittest.main()

