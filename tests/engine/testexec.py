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
from tadek.engine.tasker import *
from tadek.engine.testdefs import *
from tadek.engine.contexts import *
from tadek.engine.testexec import (TestExec, TestAbortError,
                                   TestFailError, TestFailThisError)

__all__ = ["AssertErrorTest", "ExecTest"]

class AssertErrorTest(unittest.TestCase):
    def testAbortExec(self):
        test = TestExec()
        try:
            test.abort(False, "Abort test")
        except TestAbortError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testAbortIfExec(self):
        test = TestExec()
        try:
            test.abortIf(True, "Abort test")
        except TestAbortError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testPassAbortExec(self):
        test = TestExec()
        try:
            test.abort(True, "Abort test")
        except:
            self.failIf(True)

    def testPassAbortIfExec(self):
        test = TestExec()
        try:
            test.abortIf(False, "Abort test")
        except:
            self.failIf(True)

    def testFailExec(self):
        test = TestExec()
        try:
            test.fail(False, "Fail test")
        except TestFailError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testFailIfExec(self):
        test = TestExec()
        try:
            test.failIf(True, "Fail test")
        except TestFailError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testPassFailExec(self):
        test = TestExec()
        try:
            test.fail(True, "Fail test")
        except:
            self.failIf(True)

    def testPassFailIfExec(self):
        test = TestExec()
        try:
            test.failIf(False, "Fail test")
        except:
            self.failIf(True)

    def testFailThisExec(self):
        test = TestExec()
        try:
            test.failThis(False, "Fail this test")
        except TestFailThisError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testFailThisIfExec(self):
        test = TestExec()
        try:
            test.failThisIf(True, "Fail this test")
        except TestFailThisError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testPassFailThisExec(self):
        test = TestExec()
        try:
            test.failThis(True, "Fail this test")
        except:
            self.failIf(True)

    def testPassFailThisIfExec(self):
        test = TestExec()
        try:
            test.failThisIf(False, "Fail this test")
        except:
            self.failIf(True)

@testStep()
def step1(test, device):
    if not test["setUpSuite"] or not test["setUpCase"]:
        device.failure = True
    test["step1"] = True
    return True

@testStep()
def step2(test, device):
    if not test["step1"] or not test["result"]:
        device.failure = True


class Suite1(TestSuite):
    def setUpSuite(self, test, device):
        test["setUpSuite"] = True

    def setUpCase(self, test, device):
        if not test["setUpSuite"]:
            device.failure = True
        test["setUpCase"] = True

    case1 = TestCase(step1(), step2())
    case2 = TestCase(step2())


class ExecTest(unittest.TestCase):
    def testExchangeInfoOneCase(self):
        device = FakeDevice()
        context = DeviceContext(device, TestTasker(Suite1("case1")))
        context.run(TestExec(), FakeTestResult())
        self.failIf(getattr(device, "failure", False))

    def testExchangeInfoTwoCases(self):
        device = FakeDevice()
        context = DeviceContext(device, TestTasker(Suite1()))
        context.run(TestExec(), FakeTestResult())
        self.failUnless(getattr(device, "failure", False))

if __name__ == "__main__":
    unittest.main()

