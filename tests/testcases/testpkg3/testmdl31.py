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

from tadek.engine.testdefs import *
import time

timeStep=0.1

import threading
lock = threading.Lock()
printLock = threading.Lock()
def printT(*params):
    printLock.acquire()
    s = str(threading.currentThread())
    print s[s.find("(")+1:s.find(",")]+":", params
    printLock.release()

class TestSuite(TestSuite):
    def setCounters(self, test, device):
        if not hasattr(self, "inProgress"):
            self.inProgress = {}
        key = (device, self)
        if not test.casesCounters.has_key(key):
            test.casesCounters[key] = 0
        for case in self._cases.itervalues():
            if isinstance(case, TestCase):
                case.suite = self
                test.stepsCounters[(device, case)] = len(case._steps)
            else:
                case.setCounters(test, device)

    def directCount(self):
        n = 0
        for case in self:
            if isinstance(case[1], TestCase):
                n += 1
        return n

    def doneTestCases(self, test, rootSuite):
        doneCasesCounter = sum(count
            for (dev, suite), count in test.casesCounters.iteritems()
                if suite==rootSuite)
        for (id, suite) in rootSuite:
            if isinstance(suite, TestSuite):
                doneCasesCounter += self.doneTestCases(test, suite)
        if doneCasesCounter==rootSuite.count() and \
                not hasattr(rootSuite, "suiteIsDone"):
            rootSuite.suiteIsDone = True
            test.ranTestSuites += 1
        return doneCasesCounter

    def updateTearDownCounts(self, test, device):
        lock.acquire()
        self.doneTestCases(test, self)
        test.tearDownCounters[(device, self)] = self.task.todo()
        lock.release()

    def setUpSuite(self, test, device):
        super(TestSuite, self).setUpSuite(test, device)
        lock.acquire()
        self.setCounters(test, device)
        lock.release()
        if hasattr(self, "setupFailLock"):
            if not self.setupFailLock.acquire(False):
                time.sleep(3*timeStep)
                self.setupFailLock.release()
                time.sleep(5*timeStep)
                del self.setupFailLock
                test.failThisIf(True, "")
        elif hasattr(self, "setupPassLock"):
            if not self.setupPassLock.acquire(False):
                time.sleep(3*timeStep)
                self.setupPassLock.release()
                time.sleep(7*timeStep)
                del self.setupPassLock
        elif hasattr(self, "setupLongFail"):
            if self.setupLongFail:
                del self.setupLongFail
                time.sleep(20*timeStep)
                test.failThisIf(True, "")
            else:
                del self.setupLongFail
                time.sleep(20*timeStep)
        elif hasattr(self, "setupFail"):
            del self.setupFail
            test.failIf(True, "")
        elif hasattr(self, "setupFailThis"):
            del self.setupFailThis
            test.failThisIf(True, "")
        elif hasattr(self, "setupAbort"):
            del self.setupAbort
            test.abortIf(True, "")

    def setUpCase(self, test, device):
        if hasattr(self, "setupCaseFail"):
            if self.setupCaseFail!=0:
                self.setupCaseFail -= 1
                test.failIf(True, "")
        elif hasattr(self, "setupCaseFailThis"):
            if self.setupCaseFailThis!=0:
                self.setupCaseFailThis -= 1
                test.failThisIf(True, "")
        elif hasattr(self, "setupCaseAbort"):
            del self.setupCaseAbort
            test.abortIf(True, "")

    def tearDownCase(self, test, device):
        if hasattr(self, "teardownCaseFail"):
            del self.teardownCaseFail
            test.failIf(True, "")
        elif hasattr(self, "teardownCaseFailThis"):
            del self.teardownCaseFailThis
            test.failThisIf(True, "")
        elif hasattr(self, "teardownCaseAbort"):
            del self.teardownCaseAbort
            test.abortIf(True, "")

    def tearDownSuite(self, test, device):
        super(TestSuite, self).tearDownSuite(test, device)
        self.updateTearDownCounts(test, device)
        if hasattr(self, "teardownFail"):
            del self.teardownFail
            test.failIf(True, "")
        elif hasattr(self, "teardownFailThis"):
            del self.teardownFailThis
            test.failThisIf(True, "")
        elif hasattr(self, "teardownAbort"):
            del self.teardownAbort
            test.abortIf(True, "")

def setInProgress(device, case):
    lock.acquire()
    if not hasattr(case[0].suite, "inProgress"):
        case[0].suite.inProgress = {}
    case[0].suite.inProgress[device] = True
    lock.release()

def updateCountsInStep(test, device, case):
    lock.acquire()
    test.stepsCounters[(device, case[0])] -= 1
    test.ranTestSteps += 1
    if test.stepsCounters[(device, case[0])]==0:
        test.casesCounters[(device, case[0].suite)] += 1
        test.ranTestCases += 1
        case[0].suite.inProgress[device] = False
    lock.release()

@testStep()
def step(test, device, delta=0, case=[]):
    setInProgress(device, case)
    time.sleep(delta*timeStep)
    updateCountsInStep(test, device, case)

@testStep()
def blockingStep(test, device, caseLock=False, case=[]):
    setInProgress(device, case)
    if caseLock:
        caseLock[0].acquire()
    updateCountsInStep(test, device, case)

@testStep()
def failStep(test, device, stepElem=0, case=[]):
    if stepElem==-11:
        test.fail(False, "")
    elif stepElem==-12:
        test.failThis(False, "")
    elif stepElem==-13:
        test.abort(False, "")

class Suite(TestSuite):
    def __init__(self, num=0, tests=([])):
        self.__class__.__name__ = 'suite' + str(num)
        if not tests:
            return
        while isinstance(tests[0], str):
            if tests[0]=="F":
                self.setupFail = 1
            elif tests[0]=="FT":
                self.setupFailThis = 1
            elif tests[0]=="A":
                self.setupAbort = 1
            elif tests[0][0:3]=="FCT":
                num = tests[0][3:]
                self.setupCaseFailThis = int(num) if num else -1
            elif tests[0][0:2]=="FC":
                num = tests[0][2:]
                self.setupCaseFail = int(num) if num else -1
            elif tests[0]=="AC":
                self.setupCaseAbort = 1
            tests.pop(0)
        while isinstance(tests[-1], str):
            if tests[-1]=="F":
                self.teardownFail = 1
            elif tests[-1]=="FT":
                self.teardownFailThis = 1
            elif tests[-1]=="A":
                self.teardownAbort = 1
            elif tests[-1]=="FC":
                self.teardownCaseFail = 1
            elif tests[-1]=="FCT":
                self.teardownCaseFailThis = 1
            elif tests[-1]=="AC":
                self.teardownCaseAbort = 1
            tests.pop()
        for i, elem in enumerate(tests):
            index = str(num)+str(i+1)
            if isinstance(elem, list):
                class Suite(self.__class__):
                    pass
                setattr(self.__class__, "suite"+index, Suite(index, elem))
            else:
                steps = []
                if not isinstance(elem, tuple):
                    elem = (elem,)
                cases = []
                for el in elem:
                    cases.append([])
                    if el==-1:
                        self.setupFailLock = threading.Lock()
                        steps.append(blockingStep(caseLock=[self.setupFailLock], case=cases[-1]))
                    elif el==-2:
                        self.setupPassLock = threading.Lock()
                        steps.append(blockingStep(caseLock=[self.setupPassLock], case=cases[-1]))
                    elif el==-3:
                        steps.append(step(case=cases[-1]))
                        self.setupLongFail = True
                    elif el==-4:
                        steps.append(step(case=cases[-1]))
                        self.setupLongFail = False
                    elif el<-10:
                        steps.append(failStep(stepElem=el, case=cases[-1]))
                    else:
                        steps.append(step(delta=el, case=cases[-1]))
                case = TestCase(*steps)
                for c in cases:
                    c.append(case)
                setattr(self.__class__, "case"+index, case)
        super(globals()["Suite"], self).__init__()
