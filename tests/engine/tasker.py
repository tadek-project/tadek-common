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
import unittest

from commons import *
from tadek.core import location
from tadek.engine.testresult import *
from tadek.engine.testexec import *
from tadek.engine.contexts import *
from tadek.engine.tasker import *

__all__ = ["TaskerTest", "TaskTest"]

import datetime
import threading

class TestTasker(TestTasker):
    def __init__(self, *tests):
        super(TestTasker, self).__init__(*tests)

# Make the below testcases module accessible
location.add("tests")

from tadek.engine.testresult import TestSuiteResult
import tadek.testcases.testpkg3.testmdl31
from tadek.testcases.testpkg3.testmdl31 import printT
lock = threading.Lock()

def cleanSuite(suite):
    suite.__name__ = "suite"
    for elem in suite.__dict__.copy():
        if elem[:5]=="suite" or elem[:4]=="case":
            delattr(suite, elem)

class TaskerTest(unittest.TestCase):
    def groupingTasks(self, testSuites):
        Suite = tadek.testcases.testpkg3.testmdl31.Suite
        cleanSuite(Suite)
        suites = []
        if not isinstance(testSuites, tuple):
            testSuites = (testSuites,)
        name = 1
        for tests in testSuites:
            class Suite(Suite):
                pass
            suites.append(Suite(name, tests))
            name += 1
        tasker = TestTasker(*suites)
        task1, task2 = tasker.get(), tasker.get()
        while task2:
            self.failIfEqual(task1, task2)
            self.failIfEqual(task1.parent, task2.parent)
            task1 = task2
            task2 = tasker.get()

    def testCreateTasker(self):
        Suite = tadek.testcases.testpkg3.testmdl31.Suite
        cleanSuite(Suite)
        suite1 = Suite(1, [0, 0])
        suite2 = Suite(2, [0, 0, 0])
        tasker = TestTasker(suite1, suite2)
        task = tasker.get()
        self.failUnless(task and isinstance(task, CaseTask))
        self.failUnless(hasattr(task, "parent") and isinstance(task.parent, SuiteTask))

    def testGroupingTasks1(self):
        self.groupingTasks(
            [[[0, 0, 0], [0, 0], [0, 0]], [0, [0, 0]], 0, [[0, 0], 0, 0]])

    def testGroupingTasks2(self):
        self.groupingTasks(
            [[[0, 0, 0], [0, 0], [0, 0]], [0, [0, 0]], 0, [[0, 0, 0, 0, 0], 0, 0]])
            #[[[0, 0, 0], [0, 0], [0, 0]], [0, [0, 0]], 0, [[0, 0, 0, 0, 0, 0, 0], 0, 0]])

    def testGroupingTasks3(self):
        self.groupingTasks(
            ([[0, 0], [0, 0]],
            [[[0, 0], [0, 0]], [[0, 0]]]))

    def testGroupingTasks4(self):
        self.groupingTasks(
            [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]]])

    def testEqualness(self):
        Suite = tadek.testcases.testpkg3.testmdl31.Suite
        cleanSuite(Suite)
        suite1 = Suite(1, [0, 0])
        suite2 = Suite(2, [0, 0, 0])
        tasker = TestTasker(suite1, suite2)
        task = tasker.get()
        self.failUnlessEqual(task, task.parent)


class TaskTest(unittest.TestCase):
    def testCreateCaseTask(self):
        task = CaseTask(1, case, case.result())
        self.failUnless(isinstance(task, CaseTask))
        self.failUnless(isinstance(task.context(), CaseContext))

    def testCreateSuiteTask(self):
        suite = Suite()
        task = SuiteTask(1, suite, suite.result())
        self.failUnless(isinstance(task, SuiteTask))
        self.failUnless(isinstance(task.context(None), SuiteContext))

    def testCompareTasks(self):
        suite = Suite()
        task1 = SuiteTask(1, suite, suite.result())
        task2 = CaseTask(2, case, case.result(), task1)
        self.failUnlessEqual(task2, task1)
        self.failIfEqual(task1, task2)

if __name__ == "__main__":
    unittest.main()

