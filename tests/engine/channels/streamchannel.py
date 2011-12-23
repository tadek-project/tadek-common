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
import cStringIO
from sys import stderr
import tempfile
import codecs
import os
import datetime

from engine.commons import *
from tadek.engine import channels
from tadek.engine.runner import TestRunner
from tadek.engine.testresult import *
from tadek.engine.testresult import DeviceExecResult
from tadek.engine.testexec import TestExec
from tadek.engine.channels.streamchannel import StreamChannel

__all__ = ["StreamChannelTest"]

class StreamChannelTest(unittest.TestCase):

    def setUp(self):
        self.device = FakeDevice("ExampleDevice")
        self.device.address = ("127.0.0.1", 1234)
        self.deviceResult = DeviceExecResult(self.device)
        self.deviceResult.date = datetime.datetime(2011, 2, 1, 15, 17, 54, 580480)
        self.deviceResult.time = 4.25
        self.deviceResult.status = "NOT COMPLETED"

        self.stepResult = TestStepResult()
        self.stepResult.attrs = {'description': "Test step"}
        self.stepResult.devices = [self.deviceResult]
        self.stepResult.id = "app.basic.ExampleTestsSuite.caseExampleCase.step1"
        self.stepResult.path = "/example/path/app/testsuites/app"
        self.stepResult.func = "tadek.teststeps.app.basic.stepExampleStep"

        self.caseResult = TestCaseResult()
        self.caseResult.attrs = {'description': "Test case"}
        self.caseResult.devices = [self.deviceResult]
        self.caseResult.id = "app.basic.ExampleTestsSuite.caseExampleCase"
        self.caseResult.path = "/example/path/app/testsuites/app"
        self.caseResult.children = [self.stepResult]

        self.stepResult.parent = self.caseResult

        self.suiteResult = TestSuiteResult()
        self.suiteResult.attrs = {'description': "Test suite"}
        self.suiteResult.devices = [self.deviceResult]
        self.suiteResult.id = "app.basic.ExampleTestsSuite"
        self.suiteResult.path = "/example/path/app/testsuites/app"
        self.suiteResult.children = [self.caseResult]
        self.suiteResult.parent = None

        self.caseResult.parent = self.suiteResult

    _MAJOR_BREAK = 80 * '-'
    _MINOR_BREAK = 10 * "- "
    START_VERBOSE = 'START->\t'
    STOP_VERBOSE = 'STOP ->\t'

    def _compare(self, values, expectedValues):
        actualValues = values.split('\n')
        for actualValue, expectedValue in zip(actualValues, expectedValues):
            self.assertEqual(actualValue, expectedValue)

    def testEncodingUTF(self):
        f=tempfile.NamedTemporaryFile(delete=False)
        name = f.name
        encoding = 'UTF-8'
        try:
            channel =  StreamChannel("Test", stream=f, encoding=encoding)
            self.assertEqual(channel._encoding, encoding)
            s = u'\u2041\u4349\uf091\u0041'
            channel.write(s)
            f.close()
            f = codecs.open(name, 'rb', encoding)
            data = f.read()
            f.close()
            self.assertEqual(s, data)
        finally:
            f.close()
            os.unlink(name)

    def testEncodingISO8859(self):
        f=tempfile.NamedTemporaryFile(delete=False)
        name = f.name
        encoding = 'ISO8859-1'
        try:
            channel =  StreamChannel("Test", stream=f, encoding=encoding)
            self.assertEqual(channel._encoding, encoding)
            s = u'\u0041\u0049\u00A1\u0041'
            channel.write(s)
            f.close()
            f = codecs.open(name, 'rb', encoding)
            data = f.read()
            f.close()
            self.assertEqual(s, data)
        finally:
            f.close()
            os.unlink(name)

    def testStartTestSuite(self):
        expectedValue = ["START->\t["+self.device.name+"] "+self.suiteResult.id]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.startTest(self.suiteResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStartTestCase(self):
        expectedValue = ["START->\t["+self.device.name+"] "+
            self.caseResult.id]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.startTest(self.caseResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStartTestStep(self):
        expectedValue = [""]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.startTest(self.stepResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestSuite(self):
        expectedValue = ["STOP ->\t["+self.device.name+"] "+
            self.suiteResult.id+": "+self.deviceResult.status, ""]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.stopTest(self.suiteResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestCase(self):
        expectedValue = ["STOP ->\t["+self.device.name+"] "+
            self.caseResult.id+": "+self.deviceResult.status, ""]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.stopTest(self.caseResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestStep(self):
        expectedValue = [""]
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=False, stream=string)
        channel.stopTest(self.stepResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStartTestSuiteVerbose(self):
        expectedValue = ['',
            self._MAJOR_BREAK,
            self.START_VERBOSE+"common"+'->\tclass->\tTestSuite',
            self.START_VERBOSE+"common"+'->\tid->\t'+self.suiteResult.id,
            self.START_VERBOSE+"common"+'->\tpath->\t'+self.suiteResult.path,
            self.START_VERBOSE+"attributes"+'->\tdescription->\tTest suite',
            self.START_VERBOSE+self._MINOR_BREAK,
            self.START_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.START_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.START_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.START_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.START_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.START_VERBOSE+"device"+'->\tport->\t1234',
            self.START_VERBOSE+"device"+'->\tdescription->\tNone',
            self.START_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.startTest(self.suiteResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStartTestCaseVerbose(self):
        expectedValue = ['',
            self._MAJOR_BREAK,
            self.START_VERBOSE+"common"+'->\tclass->\tTestCase',
            self.START_VERBOSE+"common"+'->\tid->\t'+self.caseResult.id,
            self.START_VERBOSE+"common"+'->\tpath->\t'+self.caseResult.path,
            self.START_VERBOSE+"attributes"+'->\tdescription->\tTest case',
            self.START_VERBOSE+self._MINOR_BREAK,
            self.START_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.START_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.START_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.START_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.START_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.START_VERBOSE+"device"+'->\tport->\t1234',
            self.START_VERBOSE+"device"+'->\tdescription->\tNone',
            self.START_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.startTest(self.caseResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStartTestStepVerbose(self):
        expectedValue = ['',
            self._MAJOR_BREAK,
            self.START_VERBOSE+"common"+'->\tclass->\tTestStep',
            self.START_VERBOSE+"common"+'->\tid->\t'+self.stepResult.id,
            self.START_VERBOSE+"common"+'->\tpath->\t'+self.stepResult.path,
            self.START_VERBOSE+"common"+'->\tfunc->\t'+self.stepResult.func,
            self.START_VERBOSE+"attributes"+'->\tdescription->\tTest step',
            self.START_VERBOSE+self._MINOR_BREAK,
            self.START_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.START_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.START_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.START_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.START_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.START_VERBOSE+"device"+'->\tport->\t1234',
            self.START_VERBOSE+"device"+'->\tdescription->\tNone',
            self.START_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.startTest(self.stepResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestSuiteVerbose(self):
        expectedValue = [
            self._MAJOR_BREAK,
            self.STOP_VERBOSE+"common"+'->\tclass->\tTestSuite',
            self.STOP_VERBOSE+"common"+'->\tid->\t'+self.suiteResult.id,
            self.STOP_VERBOSE+"common"+'->\tpath->\t'+self.suiteResult.path,
            self.STOP_VERBOSE+"attributes"+'->\tdescription->\tTest suite',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            self.STOP_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.STOP_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.STOP_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.STOP_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.STOP_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.STOP_VERBOSE+"device"+'->\tport->\t1234',
            self.STOP_VERBOSE+"device"+'->\tdescription->\tNone',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.stopTest(self.suiteResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestCaseVerbose(self):
        expectedValue = [
            self._MAJOR_BREAK,
            self.STOP_VERBOSE+"common"+'->\tclass->\tTestCase',
            self.STOP_VERBOSE+"common"+'->\tid->\t'+self.caseResult.id,
            self.STOP_VERBOSE+"common"+'->\tpath->\t'+self.caseResult.path,
            self.STOP_VERBOSE+"attributes"+'->\tdescription->\tTest case',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            self.STOP_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.STOP_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.STOP_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.STOP_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.STOP_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.STOP_VERBOSE+"device"+'->\tport->\t1234',
            self.STOP_VERBOSE+"device"+'->\tdescription->\tNone',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.stopTest(self.caseResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

    def testStopTestStepVerbose(self):
        expectedValue = [
            self._MAJOR_BREAK,
            self.STOP_VERBOSE+"common"+'->\tclass->\tTestStep',
            self.STOP_VERBOSE+"common"+'->\tid->\t'+self.stepResult.id,
            self.STOP_VERBOSE+"common"+'->\tpath->\t'+self.stepResult.path,
            self.STOP_VERBOSE+"common"+'->\tfunc->\t'+self.stepResult.func,
            self.STOP_VERBOSE+"attributes"+'->\tdescription->\tTest step',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            self.STOP_VERBOSE+"device"+'->\tstatus->\t'+
                self.deviceResult.status,
            self.STOP_VERBOSE+"device"+'->\tname->\t'+
                self.deviceResult.name,
            self.STOP_VERBOSE+"device"+'->\ttime->\t'+
                str(self.deviceResult.time),
            self.STOP_VERBOSE+"device"+'->\tdate->\t'+
                str(self.deviceResult.date)[:-7],
            self.STOP_VERBOSE+"device"+'->\taddress->\t127.0.0.1',
            self.STOP_VERBOSE+"device"+'->\tport->\t1234',
            self.STOP_VERBOSE+"device"+'->\tdescription->\tNone',
            self.STOP_VERBOSE+self._MINOR_BREAK,
            '']
        string = cStringIO.StringIO()
        channel = StreamChannel("Test", verbose=True, stream=string)
        channel.stopTest(self.stepResult, self.deviceResult)
        value = string.getvalue()
        self._compare(value, expectedValue)

if __name__ == "__main__":
    unittest.main()

