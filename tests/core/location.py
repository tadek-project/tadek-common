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
import sys
import unittest

from tadek import models
from tadek import teststeps
from tadek import testcases
from tadek import testsuites
from tadek.core import location

__all__ = ["LocationTest"]


_LOCATION_DIR = os.path.abspath("tests")
_MODELS_DIR = os.path.join(_LOCATION_DIR, "models")
_TESTSTEPS_DIR = os.path.join(_LOCATION_DIR, "teststeps")
_TESTCASES_DIR = os.path.join(_LOCATION_DIR, "testcases")
_TESTSUITES_DIR = os.path.join(_LOCATION_DIR, "testsuites")


class LocationTest(unittest.TestCase):
    def tearDown(self):
        location.remove(_LOCATION_DIR)

    def testAdd(self):
        location.add(_LOCATION_DIR)
        self.failUnless(_MODELS_DIR in models.__path__)
        self.failUnless(_TESTSTEPS_DIR in teststeps.__path__)
        self.failUnless(_TESTCASES_DIR in testcases.__path__)
        self.failUnless(_TESTSUITES_DIR in testsuites.__path__)
        try:
            __import__("tadek.models.model1")
            __import__("tadek.teststeps.stepspkg2.stepsmdl21")
            __import__("tadek.testcases.casespkg1.casesmdl11")
            __import__("tadek.testsuites.suitespkg2.suitesmdl22")
        except ImportError:
            self.failIf(True)

    def testAddDisabled(self):
        location.add(_LOCATION_DIR, False)
        self.failIf(_MODELS_DIR in models.__path__)
        self.failIf(_TESTSTEPS_DIR in teststeps.__path__)
        self.failIf(_TESTCASES_DIR in testcases.__path__)
        self.failIf(_TESTSUITES_DIR in testsuites.__path__)
        try:
            __import__("tadek.models.model1")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.teststeps.stepspkg2.stepsmdl21")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testcases.casespkg1.casesmdl11")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testsuites.suitespkg2.suitesmdl22")
        except ImportError:
            pass
        else:
            self.failIf(True)

    def testRemove(self):
        self.testAdd()
        location.remove(_LOCATION_DIR)
        self.failIf(_MODELS_DIR in models.__path__)
        self.failIf(_TESTSTEPS_DIR in teststeps.__path__)
        self.failIf(_TESTCASES_DIR in testcases.__path__)
        self.failIf(_TESTSUITES_DIR in testsuites.__path__)
        try:
            __import__("tadek.models.model1")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.teststeps.stepspkg2.stepsmdl21")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testcases.casespkg1.casesmdl11")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testsuites.suitespkg2.suitesmdl22")
        except ImportError:
            pass
        else:
            self.failIf(True)

    def testEnable(self):
        location.add(_LOCATION_DIR, False)
        location.enable(_LOCATION_DIR)
        self.failUnless(_MODELS_DIR in models.__path__)
        self.failUnless(_TESTSTEPS_DIR in teststeps.__path__)
        self.failUnless(_TESTCASES_DIR in testcases.__path__)
        self.failUnless(_TESTSUITES_DIR in testsuites.__path__)
        try:
            __import__("tadek.models.model1")
            __import__("tadek.teststeps.stepspkg1.stepsmdl12")
            __import__("tadek.testcases.casespkg2.casesmdl21")
            __import__("tadek.testsuites.suitespkg1.suitesmdl11")
        except ImportError:
            self.failIf(True)

    def testDisable(self):
        location.add(_LOCATION_DIR)
        location.disable(_LOCATION_DIR)
        self.failIf(_MODELS_DIR in models.__path__)
        self.failIf(_TESTSTEPS_DIR in teststeps.__path__)
        self.failIf(_TESTCASES_DIR in testcases.__path__)
        self.failIf(_TESTSUITES_DIR in testsuites.__path__)
        try:
            __import__("tadek.models.model1")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.teststeps.stepspkg2.stepsmdl21")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testcases.casespkg1.casesmdl11")
        except ImportError:
            pass
        else:
            self.failIf(True)
        try:
            __import__("tadek.testsuites.suitespkg2.suitesmdl22")
        except ImportError:
            pass
        else:
            self.failIf(True)

    def testGet(self):
        location.add(_LOCATION_DIR)
        self.failUnless(_LOCATION_DIR in location.get())

    def testGetEnabled(self):
        location.add(_LOCATION_DIR)
        self.failUnless(_LOCATION_DIR in location.get(True))

    def testGetDisabled(self):
        location.add(_LOCATION_DIR, False)
        self.failUnless(_LOCATION_DIR in location.get())
        self.failIf(_LOCATION_DIR in location.get(True))

    def testGetModels(self):
        location.add(_LOCATION_DIR)
        mdls = location.getModels()
        self.failUnless("model1" in mdls)
        self.failUnless("model2" in mdls)

    def testGetSteps(self):
        location.add(_LOCATION_DIR)
        steps = location.getSteps()
        self.failUnless("stepspkg1" in steps)
        self.failUnless("stepspkg1.stepsmdl11" in steps)
        self.failUnless("stepspkg1.stepsmdl12" in steps)
        self.failUnless("stepspkg2" in steps)
        self.failUnless("stepspkg2.stepsmdl21" in steps)
        self.failUnless("stepspkg2.stepsmdl22" in steps)

    def testGetCases(self):
        location.add(_LOCATION_DIR)
        cases = location.getCases()
        self.failUnless("casespkg1" in cases)
        self.failUnless("casespkg1.casesmdl11" in cases)
        self.failUnless("casespkg1.casesmdl12" in cases)
        self.failUnless("casespkg2" in cases)
        self.failUnless("casespkg2.casesmdl21" in cases)
        self.failUnless("casespkg2.casesmdl22" in cases)

    def testGetSuites(self):
        location.add(_LOCATION_DIR)
        suites = location.getSuites()
        self.failUnless("suitespkg1" in suites)
        self.failUnless("suitespkg1.suitesmdl11" in suites)
        self.failUnless("suitespkg1.suitesmdl12" in suites)
        self.failUnless("suitespkg2" in suites)
        self.failUnless("suitespkg2.suitesmdl21" in suites)
        self.failUnless("suitespkg2.suitesmdl22" in suites)

