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

from tadek.core import utils
from tadek.engine.testresult import TestCaseResult
from tadek.engine.channels import register, TestResultChannel
from tadek.engine.testexec import *

__all__ = ["SummaryChannel", "COUNTER_N_TESTS", "COUNTER_TESTS_RUN",
           "COUNTER_CORE_DUMPS", "COUNTER_RUN_TIME"]

# Counters names
COUNTER_N_TESTS = "ntests"
COUNTER_TESTS_RUN = "testsRun"
COUNTER_CORE_DUMPS = "coreDumps"
COUNTER_RUN_TIME = "runTime"

# A list of status counters
STATUS_COUNTERS = (
    STATUS_NO_RUN,
    STATUS_NOT_COMPLETED,
    STATUS_PASSED,
    STATUS_FAILED,
    STATUS_ERROR
)

# Time stamp counters:
_START_STAMP = "startStamp"
_STOP_STAMP = "stopStamp"

def _countCaseResults(result):
    '''
    Counts all test case results in the given test result tree.
    '''
    if isinstance(result, TestCaseResult):
        return 1
    count = 0
    for child in result.children:
        count += _countCaseResults(child)
    return count

class SummaryChannel(TestResultChannel):
    '''
    Channel used to gain summary of tests.
    '''
    def __init__(self, name, enabled=True, verbose=False, **params):
        TestResultChannel.__init__(self, name, enabled, verbose, **params)
        self._counters = {}

    def start(self, result):
        '''
        Initializes all the channel counters.
        '''
        TestResultChannel.start(self, result)
        stamp = time.time()
        self._counters = {
            _START_STAMP: stamp,
            _STOP_STAMP: stamp,
            COUNTER_N_TESTS: _countCaseResults(result),
            COUNTER_TESTS_RUN: 0,
            COUNTER_CORE_DUMPS: 0
        }
        for status in STATUS_COUNTERS:
            self._counters[status] = 0

    def startTest(self, result, device):
        '''
        Processes a test start execution for the summary channel.
        '''
        TestResultChannel.startTest(self, result, device)
        if isinstance(result, TestCaseResult):
            self._counters[STATUS_NOT_COMPLETED] += 1
            self._counters[COUNTER_TESTS_RUN] += 1

    def stopTest(self, result, device):
        '''
        Processes a test stop execution for the summary channel.
        '''
        TestResultChannel.stopTest(self, result, device)
        if isinstance(result, TestCaseResult):
            self._counters[STATUS_NOT_COMPLETED] -= 1
            self._counters[device.status] += 1
            self._counters[_STOP_STAMP] = time.time()
        if device.cores:
            self._counters[COUNTER_CORE_DUMPS] += len(device.cores)

    def getSummary(self):
        '''
        Gets a summary of test results.
        '''
        runTime = self._counters[_STOP_STAMP] - self._counters[_START_STAMP]
        summary = {
            COUNTER_RUN_TIME: utils.runTimeToString(runTime),
            COUNTER_N_TESTS: self._counters[COUNTER_N_TESTS],
            COUNTER_TESTS_RUN: self._counters[COUNTER_TESTS_RUN],
            COUNTER_CORE_DUMPS: self._counters[COUNTER_CORE_DUMPS]
        }
        # Copy all status counters except STATUS_NO_RUN
        for status in STATUS_COUNTERS[1:]:
            summary[status] = self._counters[status]
        return summary

register(SummaryChannel)

