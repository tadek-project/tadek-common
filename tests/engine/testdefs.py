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

from commons import *
from tadek.engine.testexec import *
from tadek.engine.testresult import *
from tadek.engine.testresult import DeviceExecResult
from tadek.engine.testdefs import *
from tadek.engine.testdefs import TestStepPrototype, TestStep

__all__ = ["StepTest", "CaseTest", "SuiteTest"]

class StepTest(unittest.TestCase):
    _DESC = "Step description"

    def testCreateStep(self):
        self.failUnless(isinstance(step, TestStepPrototype))
        self.failUnless(isinstance(step(), TestStep))

    def testStepAttrs(self):
        @testStep(description=self._DESC)
        def step(test, device):
            pass
        st = step()
        self.failUnless(isinstance(st, TestStep))
        self.failUnless("description" in st.attrs)
        self.failUnlessEqual(st.attrs["description"], self._DESC)

    def testStepPrototypeRun(self):
        @testStep()
        def step(test, device, arg=False):
            test["arg"] = arg
        self.failUnless(isinstance(step, TestStepPrototype))
        test = TestExec()
        step.run(test, TestDevice(), arg=True)
        self.failUnlessEqual(test["arg"], True)

    def testStepRun(self):
        @testStep()
        def step(test, device):
            test["run"] = True
        st = step()
        self.failUnless(isinstance(st, TestStep))
        test = TestExec()
        st.run(test, TestDevice())
        self.failUnlessEqual(test["run"], True)

    def testStepRunArgs(self):
        @testStep()
        def step(test, device, arg1=0, arg2=''):
            test["arg1"] = arg1
            test["arg2"] = arg2
        a1 = 1
        a2 = "Step argument"
        st = step(arg1=a1, arg2=a2)
        self.failUnless(isinstance(st, TestStep))
        test = TestExec()
        st.run(test, TestDevice())
        self.failUnlessEqual(test["arg1"], a1)
        self.failUnlessEqual(test["arg2"], a2)

    def testStepRunDefaultArgs(self):
        @testStep()
        def step(test, device, arg1=0, arg2=''):
            test["arg1"] = arg1
            test["arg2"] = arg2
        st = step()
        self.failUnless(isinstance(st, TestStep))
        test = TestExec()
        st.run(test, TestDevice())
        self.failUnlessEqual(test["arg1"], 0)
        self.failUnlessEqual(test["arg2"], '')

    def testStepTestResult(self):
        st = step()
        self.failUnless(isinstance(st, TestStep))
        result = st.result(id=1)
        self.failUnless(isinstance(result, TestStepResult))
        self.failUnlessEqual(result.status, STATUS_NO_RUN)
        devres = result.device(TestDevice())
        self.failUnless(isinstance(devres, DeviceExecResult))
        self.failUnlessEqual(devres.status, STATUS_NO_RUN)
        self.failIf(devres.date)
        self.failIf(devres.time)


class CaseTest(unittest.TestCase):
    _DESC = "Case description"

    def testCreateCase(self):
        self.failUnless(isinstance(case, TestCase))
        self.failUnless(isinstance(case(), TestCase))

    def testCaseAttrs(self):
        @testCase(description=self._DESC)
        def case(test, device):
            pass
        self.failUnless(isinstance(case, TestCase))
        self.failUnless("description" in case.attrs)
        self.failUnlessEqual(case.attrs["description"], self._DESC)

    def testCaseTestResult(self):
        device = TestDevice()
        result = case.result(id="case")
        self.failUnless(isinstance(result, TestCaseResult))
        self.failUnlessEqual(result.status, STATUS_NO_RUN)
        devres = result.device(device)
        self.failUnless(isinstance(devres, DeviceExecResult))
        self.failUnlessEqual(devres.status, STATUS_NO_RUN)
        self.failIf(devres.date)
        self.failIf(devres.time)

    def testCaseRun(self):
        @testCase()
        def case(test, device):
            test["run"] = True
        test = TestExec()
        case.run(test, TestDevice())
        self.failUnlessEqual(test["run"], True)

    def testCaseRunSteps(self):
        @testStep()
        def step1(test, device):
            test["run1"] = True
        @testStep()
        def step2(test, device):
            test["run2"] = True
        steps = (step1(), step2())
        case = TestCase(*steps)
        self.failUnless(isinstance(case, TestCase))
        test = TestExec()
        case.run(test, TestDevice())
        for i in xrange(1, len(steps)+1):
            self.failUnlessEqual(test["run%d" % i], True)

    def testCaseRunSuper(self):
        @testCase()
        def case(test, device):
            test["case"] = True
        @testStep()
        def step(test, device):
            test["step"] = True
        superCase = TestCase(step(), case())
        self.failUnless(isinstance(superCase, TestCase))
        test = TestExec()
        superCase.run(test, TestDevice())
        self.failUnlessEqual(test["case"], True)
        self.failUnlessEqual(test["step"], True)


class SimpleSuite(TestSuite):
    description = "Suite description"
    case = case

class ComplexSuite(TestSuite):
    description = "Complex suite description"
    @testStep()
    def step(test, device):
        test["step"] = True
    @testCase()
    def case(test, device):
        test["case"] = True
    case2 = TestCase(step())
    case3 = TestCase(step(), case())

class SuperSuite(TestSuite):
    description = "Super suite description"
    case1 = case()
    case2 = ComplexSuite()

class SuiteTest(unittest.TestCase):
    def testCreateSuite(self):
        suite = Suite()
        self.failUnless(isinstance(suite, TestSuite))
        self.failUnless(isinstance(suite(), TestSuite))

    def testCreateSuperSuite(self):
        suite = SuperSuite()
        self.failUnless(isinstance(suite, TestSuite))
        suiteDict = {}
        for id, cs in suite:
            suiteDict[id] = cs
        self.failUnlessEqual(len(suiteDict), 2)
        self.failUnless("case1" in suiteDict)
        self.failUnlessEqual(suiteDict["case1"], case)
        self.failUnless("case2" in suiteDict)
        suite = suiteDict["case2"]
        self.failUnless(isinstance(suite, ComplexSuite))
        self.failUnlessEqual(len([cs for id, cs in suite]), 3)

    def testCreateSuiteArg(self):
        suite = SimpleSuite("case")
        self.failUnless(isinstance(suite, TestSuite))

    def testCreateSuperSuiteArgs1(self):
        suite = SuperSuite("case2")
        self.failUnless(isinstance(suite, TestSuite))
        suiteDict = {}
        for id, cs in suite:
            suiteDict[id] = cs
        self.failUnlessEqual(len(suiteDict), 1)
        self.failUnless("case2" in suiteDict)
        suite = suiteDict["case2"]
        self.failUnless(isinstance(suite, ComplexSuite))
        self.failUnlessEqual(len([cs for id, cs in suite]), 3)

    def testCreateSuperSuiteArgs2(self):
        suite = SuperSuite("case2.case2", "case2.case3")
        self.failUnless(isinstance(suite, TestSuite))
        suiteDict = {}
        for id, cs in suite:
            suiteDict[id] = cs
        self.failUnlessEqual(len(suiteDict), 1)
        self.failUnless("case2" in suiteDict)
        suite = suiteDict["case2"]
        self.failUnless(isinstance(suite, ComplexSuite))
        self.failUnlessEqual(len([cs for id, cs in suite]), 2)

    def testCreateSuiteWrongArg(self):
        try:
            suite = SimpleSuite("case2")
        except AttributeError:
            pass
        else:
            self.failIf(True)

    def testCreateSuperSuiteWrongArg(self):
        try:
            suite = SuperSuite("case2.case1")
        except AttributeError:
            pass
        else:
            self.failIf(True)

    def testCreateSuiteTooLongArg(self):
        try:
            suite = SimpleSuite("suite.case")
        except AttributeError:
            pass
        else:
            self.failIf(True)

    def testSuiteAttrs(self):
        suite = SimpleSuite()
        self.failUnless(isinstance(suite, TestSuite))
        self.failUnless("description" in suite.attrs)
        self.failUnlessEqual(suite.attrs["description"],
                             SimpleSuite.description)

    def testSuiteRun(self):
        suite = ComplexSuite("case")
        self.failUnless(isinstance(suite, TestSuite))
        test = TestExec()
        for id, case in suite:
            case.run(test, TestDevice())
        self.failUnlessEqual(test["case"], True)

    def testSuiteTestResult(self):
        suite = SimpleSuite()
        self.failUnless(isinstance(suite, TestSuite))
        result = suite.result()
        self.failUnless(isinstance(result, TestSuiteResult))
        self.failUnlessEqual(result.status, STATUS_NO_RUN)
        devres = result.device(TestDevice())
        self.failUnless(isinstance(devres, DeviceExecResult))
        self.failUnlessEqual(devres.status, STATUS_NO_RUN)
        self.failIf(devres.date)
        self.failIf(devres.time)

if __name__ == "__main__":
    unittest.main()

