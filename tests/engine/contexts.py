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
from tadek.engine.contexts import *
from tadek.engine.testdefs import *
from tadek.engine.tasker import *
from tadek.engine.testexec import TestAbortError

__all__ = ["CaseContextTest", "ContextsTest"]

@testStep()
def step1(test, device):
    if "step1" not in test:
        test["step1"] = 0
    test["step1"] += 1

@testStep()
def step2(test, device):
    if "step2" not in test:
        test["step2"] = 0
    test["step2"] += 1

@testStep()
def step3(test, device):
    if "step3" not in test:
        test["step3"] = 0
    test["step3"] += 1


class _Suite(TestSuite):
    def setUpSuite(self, test, device):
        if "setUpSuite" not in test:
            test["setUpSuite"] = 0
        test["setUpSuite"] += 1

    def setUpCase(self, test, device):
        if "setUpCase" not in test:
            test["setUpCase"] = 0
        test["setUpCase"] += 1

    def tearDownCase(self, test, device):
        if "tearDownCase" not in test:
            test["tearDownCase"] = 0
        test["tearDownCase"] += 1

    def tearDownSuite(self, test, device):
        if "tearDownSuite" not in test:
            test["tearDownSuite"] = 0
        test["tearDownSuite"] += 1


class Suite1(_Suite):
    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())


class Suite2(TestSuite):
    def setUpSuite(self, test, device):
        if "setUpSuite2" not in test:
            test["setUpSuite2"] = 0
        test["setUpSuite2"] += 1

    def setUpCase(self, test, device):
        if "setUpCase2" not in test:
            test["setUpCase2"] = 0
        test["setUpCase2"] += 1

    def tearDownCase(self, test, device):
        if "tearDownCase2" not in test:
            test["tearDownCase2"] = 0
        test["tearDownCase2"] += 1

    def tearDownSuite(self, test, device):
        if "tearDownSuite2" not in test:
            test["tearDownSuite2"] = 0
        test["tearDownSuite2"] += 1

    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = TestCase(step2(), step3(), step1())
    case4 = TestCase(step3(), step1(), step2())
    case5 = TestCase(step1(), step2(), step2(), step3())


######## setUpSuite() / tearDownSuite() ########

class Suite3(_Suite):
    def setUpSuite(self, test, device):
        if "setUpSuite3" not in test:
            test["setUpSuite3"] = 0
        test["setUpSuite3"] += 1
        test.failThis(False, "Fail this set up suite 3")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite31(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite3()


class Suite4(_Suite):
    def setUpSuite(self, test, device):
        if "setUpSuite4" not in test:
            test["setUpSuite4"] = 0
        test["setUpSuite4"] += 1
        test.fail(False, "Fail set up suite 4")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite41(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite4()


class Suite5(_Suite):
    def setUpSuite(self, test, device):
        if "setUpSuite5" not in test:
            test["setUpSuite5"] = 0
        test["setUpSuite5"] += 1
        test.abort(False, "Abort set up suite 5")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite51(_Suite):
    case1 = Suite5()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite6(_Suite):
    def setUpSuite(self, test, device):
        if "setUpSuite6" not in test:
            test["setUpSuite6"] = 0
        test["setUpSuite6"] += 1
        # NameError
        error

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite61(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite6()


class Suite7(_Suite):
    def tearDownSuite(self, test, device):
        if "tearDownSuite7" not in test:
            test["tearDownSuite7"] = 0
        test["tearDownSuite7"] += 1
        test.failThis(False, "Fail this tear down suite 7")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite71(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite7()


class Suite8(_Suite):
    def tearDownSuite(self, test, device):
        if "tearDownSuite8" not in test:
            test["tearDownSuite8"] = 0
        test["tearDownSuite8"] += 1
        test.fail(False, "Fail tear down suite 8")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite81(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite8()


class Suite9(_Suite):
    def tearDownSuite(self, test, device):
        if "tearDownSuite9" not in test:
            test["tearDownSuite9"] = 0
        test["tearDownSuite9"] += 1
        test.abort(False, "Abort tear down suite 9")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite91(_Suite):
    case1 = Suite9()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite10(_Suite):
    def tearDownSuite(self, test, device):
        if "tearDownSuite10" not in test:
            test["tearDownSuite10"] = 0
        test["tearDownSuite10"] += 1
        # NameError
        error

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite101(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite10()


######## setUpCase() / tearDownCase() ########

class Suite11(_Suite):
    def setUpCase(self, test, device):
        if "setUpCase11" not in test:
            test["setUpCase11"] = 0
        test["setUpCase11"] += 1
        test.failThis(False, "Fail this set up case 11")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite111(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite11()


class Suite12(_Suite):
    def setUpCase(self, test, device):
        if "setUpCase12" not in test:
            test["setUpCase12"] = 0
        test["setUpCase12"] += 1
        test.fail(False, "Fail set up case 12")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite121(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite12()


class Suite13(_Suite):
    def setUpCase(self, test, device):
        if "setUpCase13" not in test:
            test["setUpCase13"] = 0
        test["setUpCase13"] += 1
        test.abort(False, "Abort set up case 13")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite131(_Suite):
    case1 = Suite13()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite14(_Suite):
    def setUpCase(self, test, device):
        if "setUpCase14" not in test:
            test["setUpCase14"] = 0
        test["setUpCase14"] += 1
        # NameError
        error

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite141(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite14()


class Suite15(_Suite):
    def tearDownCase(self, test, device):
        if "tearDownCase15" not in test:
            test["tearDownCase15"] = 0
        test["tearDownCase15"] += 1
        test.failThis(False, "Fail this tear down case 15")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite151(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite15()


class Suite16(_Suite):
    def tearDownCase(self, test, device):
        if "tearDownCase16" not in test:
            test["tearDownCase16"] = 0
        test["tearDownCase16"] += 1
        test.fail(False, "Fail tear down case 16")

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite161(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite16()


class Suite17(_Suite):
    def tearDownCase(self, test, device):
        if "tearDownCase17" not in test:
            test["tearDownCase17"] = 0
        test["tearDownCase17"] += 1
        test.abort(False, "Abort tear down case 17")

    case1 = TestCase(step1())
    case2 = TestCase(step1())
    case3 = TestCase(step1())

class Suite171(_Suite):
    case1 = Suite17()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite18(_Suite):
    def tearDownCase(self, test, device):
        if "tearDownCase18" not in test:
            test["tearDownCase18"] = 0
        test["tearDownCase18"] += 1
        # NameError
        error

    case1 = TestCase(step1())
    case2 = TestCase(step2())
    case3 = TestCase(step3())

class Suite181(_Suite):
    case1 = Suite1()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite18()


@testStep()
def step4(test, device):
    if "step4" not in test:
        test["step4"] = 0
    test["step4"] += 1
    test.failThis(False, "Fail this step")

@testStep()
def step5(test, device):
    if "step5" not in test:
        test["step5"] = 0
    test["step5"] += 1
    test.fail(False, "Fail a case")

@testStep()
def step6(test, device):
    if "step6" not in test:
        test["step6"] = 0
    test["step6"] += 1
    test.abort(False, "Abort a case")

@testStep()
def step7(test, device):
    if "step7" not in test:
        test["step7"] = 0
    test["step7"] += 1
    # NameError
    error

class Suite19(_Suite):
    case1 = TestCase(step1())
    case2 = TestCase(step1(), step4(), step2())
    case3 = TestCase(step3())

class Suite191(_Suite):
    case1 = Suite19()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite20(_Suite):
    case1 = TestCase(step1())
    case2 = TestCase(step2(), step5(), step3())
    case3 = TestCase(step1())

class Suite201(_Suite):
    case1 = Suite20()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite21(_Suite):
    case1 = TestCase(step1())
    case2 = TestCase(step3(), step6(), step2())
    case3 = TestCase(step3())

class Suite211(_Suite):
    case1 = Suite21()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


class Suite22(_Suite):
    case1 = TestCase(step1())
    case2 = TestCase(step2(), step7(), step3())
    case3 = TestCase(step2())

class Suite221(_Suite):
    case1 = Suite22()
    case2 = TestCase(step1(), step2(), step3())
    case3 = Suite1()


def _validExec(test, testExec, **kwargs):
    for key, value in kwargs.iteritems():
        test.failUnlessEqual(testExec[key], value)


class CaseContextTest(unittest.TestCase):
    def testRunSimpleCase(self):
        test = FakeTestExec()
        case = TestCase(step1(), step2(), step3())
        context = CaseTask(1, case, case.result(id="case")).context()
        context.run(test, FakeDevice(), FakeTestResult())
        _validExec(self, test, step1=1, step2=1, step3=1)

    def testRunCaseFailThis(self):
        test = FakeTestExec()
        case = TestCase(step1(), step4(), step2())
        context = CaseTask(1, case, case.result(id="case")).context()
        context.run(test, FakeDevice(), FakeTestResult())
        _validExec(self, test, step1=1, step2=1, step4=1)

    def testRunCaseFail(self):
        test = FakeTestExec()
        case = TestCase(step1(), step5(), step3())
        context = CaseTask(1, case, case.result(id="case")).context()
        context.run(test, FakeDevice(), FakeTestResult())
        _validExec(self, test, step1=1, step3=None, step5=1)

    def testRunCaseAbort(self):
        test = FakeTestExec()
        case = TestCase(step2(), step6(), step3())
        context = CaseTask(1, case, case.result(id="case")).context()
        try:
            context.run(test, FakeDevice(), FakeTestResult())
        except TestAbortError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)
        _validExec(self, test, step2=1, step3=None, step6=1)


class ContextsTest(unittest.TestCase):
    def testRunSimpeSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite1()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunSimpeSuiteChildCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite1("case2")))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=1, tearDownCase=1,
                               step1=None, step2=1, step3=None)

    def testRunComplexSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite2()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite2=1, tearDownSuite2=1,
                               setUpSuite=1, tearDownSuite=1,
                               setUpCase2=7, tearDownCase2=7,
                               setUpCase=3, tearDownCase=3,
                               step1=5, step2=6, step3=5)

    def testRunComplexSuiteOneChildCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite2("case5")))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite2=1, tearDownSuite2=1,
                               setUpSuite=None, tearDownSuite=None,
                               setUpCase2=1, tearDownCase2=1,
                               setUpCase=None, tearDownCase=None,
                               step1=1, step2=2, step3=1)

    def testRunComplexSuiteSubSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite2("case1")))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite2=1, tearDownSuite2=1,
                               setUpSuite=1, tearDownSuite=1,
                               setUpCase2=3, tearDownCase2=3,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteOneDescendantCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite2("case1.case1")))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite2=1, tearDownSuite2=1,
                               setUpSuite=1, tearDownSuite=1,
                               setUpCase2=1, tearDownCase2=1,
                               setUpCase=1, tearDownCase=1,
                               step1=1, step2=None, step3=None)

    def testRunSuiteFailThisSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite3()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite3=1, tearDownSuite=None,
                               setUpCase=None, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteFailThisSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite31()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, setUpSuite3=1, tearDownSuite=2,
                               setUpCase=7, tearDownCase=7,
                               step1=2, step2=2, step3=2)

    def testRunSuiteFailSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite4()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite4=1, tearDownSuite=None,
                               setUpCase=None, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteFailSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite41()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, setUpSuite4=1, tearDownSuite=2,
                               setUpCase=7, tearDownCase=7,
                               step1=2, step2=2, step3=2)

    def testRunSuiteAbortSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite5()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite5=1, tearDownSuite=None,
                               setUpCase=None, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteAbortSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite51()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, setUpSuite5=1, tearDownSuite=1,
                               setUpCase=1, tearDownCase=1,
                               step1=1, step2=1, step3=1)

    def testRunSuiteErrorSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite6()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite6=1, tearDownSuite=None,
                               setUpCase=None, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteErrorSetUpSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite61()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, setUpSuite6=1, tearDownSuite=2,
                               setUpCase=7, tearDownCase=7,
                               step1=2, step2=2, step3=2)

    def testRunSuiteFailThisTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite7()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite7=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteFailThisTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite71()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite7=1, tearDownSuite=2,
                               setUpCase=13, tearDownCase=13,
                               step1=3, step2=3, step3=3)

    def testRunSuiteFailTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite8()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite8=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteFailTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite81()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite8=1, tearDownSuite=2,
                               setUpCase=13, tearDownCase=13,
                               step1=3, step2=3, step3=3)

    def testRunSuiteAbortTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite9()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite9=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteAbortTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite91()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, tearDownSuite9=1, tearDownSuite=1,
                               setUpCase=7, tearDownCase=7,
                               step1=2, step2=2, step3=2)

    def testRunSuiteErrorTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite10()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite10=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteErrorTearDownSuite(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite101()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite10=1, tearDownSuite=2,
                               setUpCase=13, tearDownCase=13,
                               step1=3, step2=3, step3=3)

    def testRunSuiteFailThisSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite11()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase11=3, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteFailThisSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite111()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=10, setUpCase11=3, tearDownCase=10,
                               step1=2, step2=2, step3=2)

    def testRunSuiteFailSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite12()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase12=3, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteFailSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite121()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=10, setUpCase12=3, tearDownCase=10,
                               step1=2, step2=2, step3=2)

    def testRunSuiteAbortSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite13()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase13=1, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteAbortSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite131()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, tearDownSuite=2,
                               setUpCase=2, setUpCase13=1, tearDownCase=2,
                               step1=1, step2=1, step3=1)

    def testRunSuiteErrorSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite14()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase14=3, tearDownCase=None,
                               step1=None, step2=None, step3=None)

    def testRunComplexSuiteErrorSetUpCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite141()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=10, setUpCase14=3, tearDownCase=10,
                               step1=2, step2=2, step3=2)

    def testRunSuiteFailThisTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite15()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase15=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteFailThisTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite151()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase15=3, tearDownCase=10,
                               step1=3, step2=3, step3=3)

    def testRunSuiteFailTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite16()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase16=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteFailTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite161()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase16=3, tearDownCase=10,
                               step1=3, step2=3, step3=3)

    def testRunSuiteAbortTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite17()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=1, tearDownCase17=1,
                               step1=1)

    def testRunComplexSuiteAbortTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite171()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, tearDownSuite=2,
                               setUpCase=3, tearDownCase17=1, tearDownCase=2,
                               step1=2, step2=1, step3=1)

    def testRunSuiteErrorTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite18()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase18=3,
                               step1=1, step2=1, step3=1)

    def testRunComplexSuiteErrorTearDownCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite181()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase18=3, tearDownCase=10,
                               step1=3, step2=3, step3=3)

    def testRunSuiteFailThisCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite19()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase=3,
                               step1=2, step2=1, step3=1, step4=1)

    def testRunComplexSuiteFailThisCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite191()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase=13,
                               step1=4, step2=3, step3=3, step4=1)

    def testRunSuiteFailCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite20()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase=3,
                               step1=2, step2=1, step3=None, step5=1)

    def testRunComplexSuiteFailCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite201()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase=13,
                               step1=4, step2=3, step3=2, step5=1)

    def testRunSuiteAbortCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite21()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=2, tearDownCase=2,
                               step1=1, step2=None, step3=1, step6=1)

    def testRunComplexSuiteAbortCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite211()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=2, tearDownSuite=2,
                               setUpCase=5, tearDownCase=5,
                               step1=2, step2=1, step3=2, step6=1)

    def testRunSuiteErrorCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite22()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=1, tearDownSuite=1,
                               setUpCase=3, tearDownCase=3,
                               step1=1, step2=2, step3=None, step7=1)

    def testRunComplexSuiteErrorCase(self):
        test = FakeTestExec()
        context = DeviceContext(FakeDevice(), TestTasker(Suite221()))
        context.run(test, FakeTestResult())
        _validExec(self, test, setUpSuite=3, tearDownSuite=3,
                               setUpCase=13, tearDownCase=13,
                               step1=3, step2=4, step3=2, step7=1)

if __name__ == "__main__":
    unittest.main()

