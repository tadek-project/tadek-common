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
import unittest

from tadek.core import location
from tadek.engine.loader import TestLoader

__all__ = ["LoaderTest"]

class LoaderTest(unittest.TestCase):
    def setUp(self):
        location.add("tests")

    def testLoadFromNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames()
        self.failUnless(tests)
        self.failIf(errors)

    def testLoadFromNamesPkgName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg1")
        self.failUnlessEqual(len(tests), 4)
        self.failIf(errors)

    def testLoadFromNamesInvalidPkgName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg99")
        self.failIf(tests)
        self.failUnless(errors)

    def testLoadFromNamesMdlName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg2.suitesmdl21")
        self.failUnlessEqual(len(tests), 2)
        self.failIf(errors)

    def testLoadFromNamesInvalidMdlName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg2.suitesmdl29")
        self.failIf(tests)
        self.failUnless(errors)

    def testLoadFromNamesClassName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg1.suitesmdl11.Suite112")
        self.failUnlessEqual(len(tests), 1)
        self.failIf(errors)

    def testLoadFromNamesInvalidClassName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg1.suitesmdl11.Suite113")
        self.failIf(tests)
        self.failUnless(errors)

    def testLoadFromNamesCaseName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                    "suitespkg2.suitesmdl22.Suite221.case2211")
        self.failUnlessEqual(len(tests), 1)
        self.failIf(errors)

    def testLoadFromNamesInvalidCaseName(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                    "suitespkg2.suitesmdl22.Suite221.case2213")
        self.failIf(tests)
        self.failUnless(errors)

    def testLoadFromNamesCaseNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                     "suitespkg1.suitesmdl11.Suite111.case1111",
                                     "suitespkg1.suitesmdl11.Suite112.case1122",
                                     "suitespkg2.suitesmdl22.Suite221.case2211")
        self.failUnlessEqual(len(tests), 3)
        self.failIf(errors)

    def testLoadFromNamesCaseNamesOfSameSuite(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                     "suitespkg1.suitesmdl11.Suite111.case1111",
                                     "suitespkg1.suitesmdl11.Suite111.case1112")
        self.failUnlessEqual(len(tests), 1)
        self.failUnlessEqual(len([case for case in tests[0]]), 2)
        self.failIf(errors)

    def testLoadFromNamesInvalidCaseNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                     "suitespkg1.suitesmdl11.Suite111.case1111",
                                     "suitespkg2.suitesmdl22.Suite221.case2213")
        self.failUnlessEqual(len(tests), 1)
        self.failUnless(errors)

    def testLoadFromNamesMixedNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames("suitespkg2.suitesmdl21",
                                     "suitespkg1.suitesmdl11.Suite111.case1112",
                                     "suitespkg1.suitesmdl11.Suite111",
                                     "suitespkg2.suitesmdl21.Suite212.case2121")
        self.failUnlessEqual(len(tests), 3)
        self.failIf(errors)

    def testLoadFromNamesSimilarNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                 "suitespkg2.suitesmdl21.Suite211.case2111",
                                 "suitespkg2.suitesmdl21.Suite211.case21112",
                                 "suitespkg2.suitesmdl21.Suite211.case211111")
        self.failUnlessEqual(len(tests), 1)
        self.failUnlessEqual(len([case for case in tests[0]]), 3)
        self.failIf(errors)

    def testLoadFromNamesSameNames(self):
        loader = TestLoader()
        tests, errors = loader.loadFromNames(
                                 "suitespkg1.suitesmdl12.Suite121",
                                 "suitespkg1.suitesmdl12.",
                                 "suitespkg1.suitesmdl12.Suite122",
                                 "suitespkg1.suitesmdl12.Suite121",
                                 "suitespkg1.suitesmdl12.Suite121.case1212")
        self.failUnlessEqual(len(tests), 2)
        self.failIf(errors)

    def testLoadFromNamesSuitesWithBaseClass(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg2.suitesmdl22")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg2" in tree)
        self.failUnlessEqual(len(tree["suitespkg2"]), 1)
        self.failUnless("suitesmdl22" in tree["suitespkg2"])
        self.failUnlessEqual(len(tree["suitespkg2"]["suitesmdl22"][None]), 3)
        self.failIf(errors)

    def testLoadTree(self):
        loader = TestLoader()
        tree, errors = loader.loadTree()
        self.failUnless(len(tree) >= 2)
        for name in ("suitespkg1", "suitespkg2"):
            self.failUnless(name in tree)
            branch = tree[name]
            self.failUnless(len(branch) >= 3)
        self.failIf(errors)

    def testLoadTreeName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg2.suitesmdl21.Suite212.case2121")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg2" in tree)
        self.failUnlessEqual(len(tree["suitespkg2"]), 1)
        self.failUnless("suitesmdl21" in tree["suitespkg2"])
        self.failUnlessEqual(len(tree["suitespkg2"]["suitesmdl21"][None]), 1)
        self.failIf(errors)

    def testLoadTreeInvalidName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg1.suitesmdl12.Suite121.case1213")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg1" in tree)
        self.failUnlessEqual(len(tree["suitespkg1"]), 1)
        self.failUnless("suitesmdl12" in tree["suitespkg1"])
        self.failIf(tree["suitespkg1"]["suitesmdl12"][None])
        self.failUnless(errors)

    def testLoadTreeSuiteName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg1.suitesmdl12.Suite121")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg1" in tree)
        self.failUnlessEqual(len(tree["suitespkg1"]), 1)
        self.failUnless("suitesmdl12" in tree["suitespkg1"])
        self.failUnlessEqual(len(tree["suitespkg1"]["suitesmdl12"][None]), 1)
        self.failIf(errors)

    def testLoadTreeMdlName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg1.suitesmdl11")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg1" in tree)
        self.failUnlessEqual(len(tree["suitespkg1"]), 1)
        self.failUnless("suitesmdl11" in tree["suitespkg1"])
        self.failUnlessEqual(len(tree["suitespkg1"]["suitesmdl11"][None]), 2)
        self.failIf(errors)

    def testLoadTreeInvalidMdlName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg1.suitesmdl13")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg1" in tree)
        self.failIf(tree["suitespkg1"][None])
        self.failUnless(errors)

    def testLoadTreePkgName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg1")
        self.failUnlessEqual(len(tree), 1)
        self.failUnless("suitespkg1" in tree)
        self.failUnlessEqual(len(tree["suitespkg1"]), 3)
        self.failUnless("suitesmdl11" in tree["suitespkg1"])
        self.failUnlessEqual(len(tree["suitespkg1"]["suitesmdl11"][None]), 2)
        self.failUnless("suitesmdl12" in tree["suitespkg1"])
        self.failUnlessEqual(len(tree["suitespkg1"]["suitesmdl12"][None]), 2)
        self.failIf(errors)

    def testLoadTreeInvalidPkgName(self):
        loader = TestLoader()
        tree, errors = loader.loadTree("suitespkg99")
        self.failIf(tree)
        self.failUnless(errors)

