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
import traceback
import cStringIO

from tadek.core import utils
from tadek.core.structs import FileDetails
from tadek.engine import testexec
from tadek.engine.channels import streamchannel

import helpers
from engine.commons import *

__all__ = ["StreamChannelTest", "StreamChannelTestVerbose",
           "StreamChannelTestErrorsCores"]

def _deviceDateTime(device, runTime=False):
    return helpers.deviceDateTime(device, runTime).split()

def _deviceAddress(device):
    return ':'.join([device.address, str(device.port)])

def _resultAttrs(result):
    return "\n\t\t".join([n + ": " + repr(v)
                          for n, v in result.attrs.iteritems()])

def _stepArgs(step):
    return ', '.join([n + '=' + repr(v) for n, v in step.args.iteritems()])


class StreamChannelTest(unittest.TestCase):
    def testWriteEncodingUTF(self):
        encoding = "UTF-8"
        data = u"\u2041\u4349\uf091\u0041"
        string = cStringIO.StringIO()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              encoding=encoding)
        channel.write(data)
        self.assertEqual(data, utils.decode(string.getvalue(), encoding))

    def testWriteEncodingISO8859(self):
        encoding = "ISO8859-1"
        data = u"\u0041\u0049\u00A1\u0041"
        string = cStringIO.StringIO()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              encoding=encoding)
        channel.write(data)
        self.assertEqual(data, utils.decode(string.getvalue(), encoding))

    def testStartStop(self):
        output = ''
        string = cStringIO.StringIO()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartTestStep(self):
        output = '''%s [%s] START %s
'''
        result = helpers.stepResult()
        string = cStringIO.StringIO()      
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        output %= (_deviceDateTime(device)[1], device.name, result.id)  
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStopTestStep(self):
        output = '''%s [%s] STOP  %s [%s]
'''
        result = helpers.stepResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult(time=2.6, status=testexec.STATUS_PASSED)
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.stopTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        output %= (_deviceDateTime(device, True)[1],
                   device.name, result.id, device.status)
        helpers.assertOutput(self, output, string)

    def testStartStopTestStep(self):
        output = '''%s [%s] START %s
%s [%s] STOP  %s [%s]
'''
        result = helpers.stepResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, device)
        device.time = 5.1
        device.status = testexec.STATUS_FAILED
        channel.stopTest(result, device)
        channel.stop()
        self.failUnless(channel.isActive())
        output %= (_deviceDateTime(device)[1], device.name, result.id,
                   _deviceDateTime(device, True)[1], device.name, result.id,
                   device.status)
        helpers.assertOutput(self, output, string)

    def testStartTestCase(self):
        output = '''%s [%s] START %s
'''
        result = helpers.caseResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        output %= (_deviceDateTime(device)[1], device.name, result.id)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStopTestCase(self):
        output = '''%s [%s] STOP  %s [%s]
'''
        result = helpers.caseResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult(time=5.6, status=testexec.STATUS_PASSED)
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.stopTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        output %= (_deviceDateTime(device, True)[1],
                   device.name, result.id, device.status)
        helpers.assertOutput(self, output, string)

    def testStartStopTestCase(self):
        output = '''%s [%s] START %s
%s [%s] STOP  %s [%s]
'''
        result = helpers.caseResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, device)
        device.time = 6.5
        device.status = testexec.STATUS_ERROR
        channel.stopTest(result, device)
        channel.stop()
        self.failUnless(channel.isActive())
        output %= (_deviceDateTime(device)[1], device.name, result.id,
                   _deviceDateTime(device, True)[1], device.name, result.id,
                    device.status)
        helpers.assertOutput(self, output, string)

    def testStartTestSuite(self):
        output = '''%s [%s] START %s
'''
        result = helpers.suiteResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        output %= (_deviceDateTime(device)[1], device.name, result.id)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStopTestSuite(self):
        output = '''%s [%s] STOP  %s [%s]
'''
        result = helpers.suiteResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult(time=3.4, status=testexec.STATUS_FAILED)
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.stopTest(result, device)
        self.failUnless(channel.isActive())
        channel.stop()
        output %= (_deviceDateTime(device, True)[1],
                   device.name, result.id, device.status)
        helpers.assertOutput(self, output, string)

    def testStartStopTestSuite(self):
        output = '''%s [%s] START %s
%s [%s] STOP  %s [%s]
'''
        result = helpers.suiteResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, device)
        device.time = 4.3
        device.status = testexec.STATUS_PASSED
        channel.stopTest(result, device)
        channel.stop()
        self.failUnless(channel.isActive())
        output %= (_deviceDateTime(device)[1], device.name, result.id,
                   _deviceDateTime(device, True)[1], device.name, result.id,
                   device.status)
        helpers.assertOutput(self, output, string)

    def testStartTest1Suite1Case(self):
        output = '''%s [%s] START %s
%s [%s] START %s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1)
        suite, case = suites[0], cases[0]
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        output %= (_deviceDateTime(device)[1], device.name, suite.id,
                   _deviceDateTime(device)[1], device.name, case.id)
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTest1Suite1Case(self):
        output = '''%s [%s] START %s
%s [%s] START %s
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1)
        suite, case = suites[0], cases[0]
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        device.time = 2.7
        device.status = testexec.STATUS_PASSED
        channel.stopTest(case, device)
        channel.stopTest(suite, device)
        channel.stop()
        output %= (_deviceDateTime(device)[1], device.name, suite.id,
                   _deviceDateTime(device)[1], device.name, case.id,
                   _deviceDateTime(device, True)[1], device.name, case.id,
                   device.status, _deviceDateTime(device, True)[1],
                   device.name, suite.id, device.status)
        helpers.assertOutput(self, output, string)

    def testStartStopTest1Suite3Cases_3Devices(self):
        output = '''%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
%s [%s] STOP  %s [%s]
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 3)
        suite, case1, case2, case3 = suites[0], cases[0], cases[1], cases[2]
        device1 = helpers.deviceResult("Device1")
        device2 = helpers.deviceResult("Device2")
        device3 = helpers.deviceResult("Device3")
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite, device1)
        channel.startTest(case1, device1)
        channel.startTest(suite, device2)
        channel.startTest(case2, device2)
        channel.startTest(suite, device3)
        channel.startTest(case3, device3)
        device1.status = testexec.STATUS_PASSED
        device1.time = 3.125
        device2.status = testexec.STATUS_FAILED
        device2.time = 2.25
        device3.status = testexec.STATUS_ERROR
        device3.time = 1.875
        channel.stopTest(case1, device1)
        channel.stopTest(suite, device1)
        channel.stopTest(case3, device3)
        channel.stopTest(suite, device3)
        channel.stopTest(case2, device2)
        channel.stopTest(suite, device2)
        channel.stop()
        output %= (_deviceDateTime(device1)[1], device1.name, suite.id,
                   _deviceDateTime(device1)[1], device1.name, case1.id,
                   _deviceDateTime(device2)[1], device2.name, suite.id,
                   _deviceDateTime(device2)[1], device2.name, case2.id,
                   _deviceDateTime(device3)[1], device3.name, suite.id,
                   _deviceDateTime(device3)[1], device3.name, case3.id,
                   _deviceDateTime(device1, True)[1], device1.name, case1.id,
                   device1.status, _deviceDateTime(device1, True)[1],
                   device1.name, suite.id, device1.status,
                   _deviceDateTime(device3, True)[1], device3.name, case3.id,
                   device3.status, _deviceDateTime(device3, True)[1],
                   device3.name, suite.id, device3.status,
                   _deviceDateTime(device2, True)[1], device2.name, case2.id,
                   device2.status, _deviceDateTime(device2, True)[1],
                   device2.name, suite.id, device2.status)
        helpers.assertOutput(self, output, string)

    def testStartTest1Suite1Case1Step(self):
        output = '''%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        output %= (_deviceDateTime(device)[1], device.name, suite.id,
                   _deviceDateTime(device)[1], device.name, case.id,
                   _deviceDateTime(device)[1], device.name, step.id)
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        channel.startTest(step, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTest2Suites2Cases2Steps(self):
        output = '''%(deviceTime)s [%(deviceName)s] START %(suite1Id)s
%(deviceTime)s [%(deviceName)s] START %(case11Id)s
%(deviceTime)s [%(deviceName)s] START %(step111Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step111Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(step112Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step112Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(case11Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(case12Id)s
%(deviceTime)s [%(deviceName)s] START %(step121Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step121Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(step122Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step122Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(case12Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(suite1Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(suite2Id)s
%(deviceTime)s [%(deviceName)s] START %(case21Id)s
%(deviceTime)s [%(deviceName)s] START %(step211Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step211Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(step212Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step212Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(case21Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(case22Id)s
%(deviceTime)s [%(deviceName)s] START %(step221Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step221Id)s [%(deviceStatus)s]
%(deviceTime)s [%(deviceName)s] START %(step222Id)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(step222Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(case22Id)s [%(deviceStatus)s]
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(suite2Id)s [%(deviceStatus)s]
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(2, 2, 2)
        suite1, suite2 = suites
        case11, case21, case12, case22 = cases
        step111,step211,step121,step221, step112,step212,step122,step222 = steps
        device = helpers.deviceResult(status=testexec.STATUS_PASSED)
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite1, device)
        channel.startTest(case11, device)
        channel.startTest(step111, device)
        device.time = 2.15
        channel.stopTest(step111, device)
        device.time = 0.0
        channel.startTest(step112, device)
        device.time = 2.15
        channel.stopTest(step112, device)
        channel.stopTest(case11, device)
        device.time = 0.0
        channel.startTest(case12, device)
        channel.startTest(step121, device)
        device.time = 2.15
        channel.stopTest(step121, device)
        device.time = 0.0
        channel.startTest(step122, device)
        device.time = 2.15
        channel.stopTest(step122, device)
        channel.stopTest(case12, device)
        channel.stopTest(suite1, device)
        device.time = 0.0
        channel.startTest(suite2, device)
        channel.startTest(case21, device)
        channel.startTest(step211, device)
        device.time = 2.15
        channel.stopTest(step211, device)
        device.time = 0.0
        channel.startTest(step212, device)
        device.time = 2.15
        channel.stopTest(step212, device)
        channel.stopTest(case21, device)
        device.time = 0.0
        channel.startTest(case22, device)
        channel.startTest(step221, device)
        device.time = 2.15
        channel.stopTest(step221, device)
        device.time = 0.0
        channel.startTest(step222, device)
        device.time = 2.15
        channel.stopTest(step222, device)
        channel.stopTest(case22, device)
        channel.stopTest(suite2, device)
        channel.stop()
        output %= {
            "suite1Id": suite1.id, "case11Id": case11.id,
            "step111Id": step111.id, "step112Id": step112.id,
            "case12Id": case12.id, "step121Id": step121.id,
            "step122Id": step122.id, "suite2Id": suite2.id,
            "case21Id": case21.id, "step211Id": step211.id,
            "step212Id": step212.id, "case22Id": case22.id,
            "step221Id": step221.id, "step222Id": step222.id,
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceTime": _deviceDateTime(device)[1],
            "deviceTimeEnd": _deviceDateTime(device, True)[1]
        }
        helpers.assertOutput(self, output, string)


class StreamChannelTestVerbose(unittest.TestCase):
    def testStartTestStep(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test step ID: %s
	Function: %s(%s)
	Path: %s
		%s
'''
        result = helpers.stepResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.func, _stepArgs(result),
                   result.path, _resultAttrs(result))
        channel.start(None)
        channel.startTest(result, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTestStep(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test step ID: %s
	Function: %s(%s)
	Path: %s
		%s
%s -------------------- STOP -------------------- [%s]
	%s: [%s] %s
	Test step ID: %s
	Function: %s(%s)
	Path: %s
		%s
'''
        result = helpers.stepResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(result, device)
        device.time = 5.1
        device.status = testexec.STATUS_FAILED
        channel.stopTest(result, device)
        channel.stop()
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.func, _stepArgs(result),
                   result.path, _resultAttrs(result),
                   helpers.deviceDateTime(device, True), device.status,
                   device.name, _deviceAddress(device), device.description,
                   result.id, result.func, _stepArgs(result),
                   result.path, _resultAttrs(result))
        helpers.assertOutput(self, output, string)

    def testStartTestCase(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test case ID: %s
	Path: %s
		%s
'''
        result = helpers.caseResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result))
        channel.start(None)
        channel.startTest(result, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTestCase(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test case ID: %s
	Path: %s
		%s
%s -------------------- STOP -------------------- [%s]
	%s: [%s] %s
	Test case ID: %s
	Path: %s
		%s
'''
        result = helpers.caseResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(result, device)
        device.time = 6.5
        device.status = testexec.STATUS_ERROR
        channel.stopTest(result, device)
        channel.stop()
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result),
                   helpers.deviceDateTime(device, True), device.status,
                   device.name, _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result))
        helpers.assertOutput(self, output, string)

    def testStartTestSuite(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test suite ID: %s
	Path: %s
		%s
'''
        result = helpers.suiteResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result))
        channel.start(None)
        channel.startTest(result, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTestSuite(self):
        output = '''%s -------------------- START --------------------
	%s: [%s] %s
	Test suite ID: %s
	Path: %s
		%s
%s -------------------- STOP -------------------- [%s]
	%s: [%s] %s
	Test suite ID: %s
	Path: %s
		%s
'''
        result = helpers.suiteResult()
        string = cStringIO.StringIO()
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(result, device)
        device.time = 4.3
        device.status = testexec.STATUS_PASSED
        channel.stopTest(result, device)
        channel.stop()
        output %= (helpers.deviceDateTime(device), device.name,
                   _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result),
                   helpers.deviceDateTime(device, True), device.status,
                   device.name, _deviceAddress(device), device.description,
                   result.id, result.path, _resultAttrs(result))
        helpers.assertOutput(self, output, string)

    def testStartTest1Suite1Case1Step(self):
        output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteAttrs": _resultAttrs(suite),
            "caseId": case.id, "casePath": case.path,
            "caseAttrs": _resultAttrs(case),
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepAttrs": _resultAttrs(step), "stepArgs": _stepArgs(step),
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceDate": helpers.deviceDateTime(device),
            "deviceAddr": _deviceAddress(device),
            "deviceDesc": device.description
        }
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        channel.startTest(step, device)
        channel.stop()
        helpers.assertOutput(self, output, string)

    def testStartStopTest1Suite1Case1Step(self):
        output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = helpers.deviceResult()
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        channel.startTest(step, device)
        device.time = 7.5
        device.status = testexec.STATUS_PASSED
        channel.stopTest(step, device)
        channel.stopTest(case, device)
        channel.stopTest(suite, device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteAttrs": _resultAttrs(suite),
            "caseId": case.id, "casePath": case.path,
            "caseAttrs": _resultAttrs(case),
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepAttrs": _resultAttrs(step), "stepArgs": _stepArgs(step),
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceDate": helpers.deviceDateTime(device),
            "deviceDateEnd": helpers.deviceDateTime(device, True),
            "deviceAddr": _deviceAddress(device),
            "deviceDesc": device.description, "deviceStatus": device.status
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTest1Suite1Case1Step_NoAttrsNoArgs(self):
        output = output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] 
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] 
	Test case ID: %(caseId)s
	Path: %(casePath)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] 
	Test step ID: %(stepId)s
	Function: %(stepFunc)s
	Path: %(stepPath)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] 
	Test step ID: %(stepId)s
	Function: %(stepFunc)s
	Path: %(stepPath)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] 
	Test case ID: %(caseId)s
	Path: %(casePath)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] 
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        suite.attrs = case.attrs = step.attrs = step.args = {}
        device = helpers.deviceResult()
        device.description = None
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, device)
        channel.startTest(case, device)
        channel.startTest(step, device)
        device.time = 7.5
        device.status = testexec.STATUS_PASSED
        channel.stopTest(step, device)
        channel.stopTest(case, device)
        channel.stopTest(suite, device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceDate": helpers.deviceDateTime(device),
            "deviceDateEnd": helpers.deviceDateTime(device, True),
            "deviceAddr": _deviceAddress(device), "deviceStatus": device.status
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTest1Suite3Cases3Steps_3Devices(self):
        output = '''%(device1Date)s -------------------- START --------------------
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(device1Date)s -------------------- START --------------------
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test case ID: %(case1Id)s
	Path: %(case1Path)s
		%(case1Attrs)s
%(device1Date)s -------------------- START --------------------
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test step ID: %(step1Id)s
	Function: %(step1Func)s(%(step1Args)s)
	Path: %(step1Path)s
		%(step1Attrs)s
%(device2Date)s -------------------- START --------------------
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(device2Date)s -------------------- START --------------------
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test case ID: %(case2Id)s
	Path: %(case2Path)s
		%(case2Attrs)s
%(device2Date)s -------------------- START --------------------
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test step ID: %(step2Id)s
	Function: %(step2Func)s(%(step2Args)s)
	Path: %(step2Path)s
		%(step2Attrs)s
%(device1DateEnd)s -------------------- STOP -------------------- [%(device1Status)s]
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test step ID: %(step1Id)s
	Function: %(step1Func)s(%(step1Args)s)
	Path: %(step1Path)s
		%(step1Attrs)s
%(device1DateEnd)s -------------------- STOP -------------------- [%(device1Status)s]
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test case ID: %(case1Id)s
	Path: %(case1Path)s
		%(case1Attrs)s
%(device1DateEnd)s -------------------- STOP -------------------- [%(device1Status)s]
	%(device1Name)s: [%(device1Addr)s] %(device1Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(device3Date)s -------------------- START --------------------
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(device3Date)s -------------------- START --------------------
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test case ID: %(case3Id)s
	Path: %(case3Path)s
		%(case3Attrs)s
%(device3Date)s -------------------- START --------------------
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test step ID: %(step3Id)s
	Function: %(step3Func)s(%(step3Args)s)
	Path: %(step3Path)s
		%(step3Attrs)s
%(device3DateEnd)s -------------------- STOP -------------------- [%(device3Status)s]
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test step ID: %(step3Id)s
	Function: %(step3Func)s(%(step3Args)s)
	Path: %(step3Path)s
		%(step3Attrs)s
%(device3DateEnd)s -------------------- STOP -------------------- [%(device3Status)s]
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test case ID: %(case3Id)s
	Path: %(case3Path)s
		%(case3Attrs)s
%(device3DateEnd)s -------------------- STOP -------------------- [%(device3Status)s]
	%(device3Name)s: [%(device3Addr)s] %(device3Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(device2DateEnd)s -------------------- STOP -------------------- [%(device2Status)s]
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test step ID: %(step2Id)s
	Function: %(step2Func)s(%(step2Args)s)
	Path: %(step2Path)s
		%(step2Attrs)s
%(device2DateEnd)s -------------------- STOP -------------------- [%(device2Status)s]
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test case ID: %(case2Id)s
	Path: %(case2Path)s
		%(case2Attrs)s
%(device2DateEnd)s -------------------- STOP -------------------- [%(device2Status)s]
	%(device2Name)s: [%(device2Addr)s] %(device2Desc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 3, 1)
        suite = suites[0]
        case1, case2, case3 = cases
        step1, step2, step3 = steps
        device1 = helpers.deviceResult("Device1", address="192.168.1.101",
                                       port=1101, status=testexec.STATUS_PASSED)
        device2 = helpers.deviceResult("Device2", address="192.168.1.102",
                                       port=1102, status=testexec.STATUS_FAILED)
        device3 = helpers.deviceResult("Device3", address="192.168.1.103",
                                       port=1103, status=testexec.STATUS_ERROR)
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, device1)
        channel.startTest(case1, device1)
        channel.startTest(step1, device1)
        channel.startTest(suite, device2)
        channel.startTest(case2, device2)
        channel.startTest(step2, device2)
        device1.time = 1.125
        channel.stopTest(step1, device1)
        channel.stopTest(case1, device1)
        channel.stopTest(suite, device1)
        channel.startTest(suite, device3)
        channel.startTest(case3, device3)
        channel.startTest(step3, device3)
        device2.time = 15.25
        device3.time = 8.875
        channel.stopTest(step3, device3)
        channel.stopTest(case3, device3)
        channel.stopTest(suite, device3)
        channel.stopTest(step2, device2)
        channel.stopTest(case2, device2)
        channel.stopTest(suite, device2)
        channel.stop()
        output %= {
          "suiteId": suite.id, "suitePath": suite.path,
          "suiteAttrs": _resultAttrs(suite),
          "case1Id": case1.id, "case1Path": case1.path,
          "case1Attrs": _resultAttrs(case1),
          "case2Id": case2.id, "case2Path": case2.path,
          "case2Attrs": _resultAttrs(case2),
          "case3Id": case3.id, "case3Path": case3.path,
          "case3Attrs": _resultAttrs(case3),
          "step1Id": step1.id, "step1Path": step1.path, "step1Func":step1.func,
          "step1Attrs": _resultAttrs(step1), "step1Args": _stepArgs(step1),
          "step2Id":step2.id, "step2Path":step2.path, "step2Func":step2.func,
          "step2Attrs": _resultAttrs(step2), "step2Args": _stepArgs(step2),
          "step3Id":step3.id, "step3Path":step3.path, "step3Func":step3.func,
          "step3Attrs": _resultAttrs(step3), "step3Args": _stepArgs(step3),
          "device1Name": device1.name, "device1Status": device1.status,
          "device1Date": helpers.deviceDateTime(device1),
          "device1DateEnd": helpers.deviceDateTime(device1, True),
          "device1Addr": _deviceAddress(device1),
          "device1Desc": device1.description,
          "device2Name": device2.name, "device2Status": device2.status,
          "device2Date": helpers.deviceDateTime(device2),
          "device2DateEnd": helpers.deviceDateTime(device2, True),
          "device2Addr": _deviceAddress(device2),
          "device2Desc": device2.description, "device2Time": device2.time,
          "device3Name": device3.name, "device3Status": device3.status,
          "device3Date": helpers.deviceDateTime(device3),
          "device3DateEnd": helpers.deviceDateTime(device3, True),
          "device3Addr": _deviceAddress(device3),
          "device3Desc": device3.description
        }
        helpers.assertOutput(self, output, string)


class StreamChannelTestErrorsCores(unittest.TestCase):
    def setUp(self):
        self.device = helpers.deviceResult(status=testexec.STATUS_ERROR)
        self.errors = [
            ''.join(traceback.format_stack()),
            ''.join(traceback.format_stack()),
            ''.join(traceback.format_stack())
        ]
        self.cores = [
            FileDetails("/tmp/core.1", mtime=time.time(), size=1024),
            FileDetails("/tmp/core.2", mtime=(time.time() + 10), size=3527),
            FileDetails("/tmp/core.3", mtime=(time.time() + 20), size=843159)
        ]

    def testStartTestErrors(self):
        output = '''%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        self.device.errors = self.errors
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        output %= (_deviceDateTime(self.device)[1], self.device.name, suite.id,
                   _deviceDateTime(self.device)[1], self.device.name, case.id,
                   _deviceDateTime(self.device)[1], self.device.name, step.id)
        helpers.assertOutput(self, output, string)

    def testStartStopTestErrors(self):
        output = '''%(deviceTime)s [%(deviceName)s] START %(suiteId)s
%(deviceTime)s [%(deviceName)s] START %(caseId)s
%(deviceTime)s [%(deviceName)s] START %(stepId)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(stepId)s [%(deviceStatus)s]
%(error1)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(caseId)s [%(deviceStatus)s]
%(error1)s
%(error2)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(suiteId)s [%(deviceStatus)s]
%(error1)s
%(error2)s
%(error3)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 3.75
        self.device.errors.append(self.errors[0])
        channel.stopTest(step, self.device)
        self.device.errors.append(self.errors[1])
        channel.stopTest(case, self.device)
        self.device.errors.append(self.errors[2])
        channel.stopTest(suite, self.device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "caseId": case.id, "stepId": step.id,
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceTime": _deviceDateTime(self.device)[1],
            "deviceTimeEnd": _deviceDateTime(self.device, True)[1],
            "error1": self.errors[0], "error2": self.errors[1],
            "error3": self.errors[2]
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTestErrorsVerbose(self):
        output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(error1)s
%(error2)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(error3)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(error1)s
%(error2)s
%(error3)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 3.75
        self.device.errors = self.errors[:2]
        channel.stopTest(step, self.device)
        self.device.errors = self.errors[2:]
        channel.stopTest(case, self.device)
        self.device.errors = self.errors
        channel.stopTest(suite, self.device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteAttrs": _resultAttrs(suite),
            "caseId": case.id, "casePath": case.path,
            "caseAttrs": _resultAttrs(case),
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepAttrs": _resultAttrs(step), "stepArgs": _stepArgs(step),
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": helpers.deviceDateTime(self.device),
            "deviceDateEnd": helpers.deviceDateTime(self.device, True),
            "deviceAddr": _deviceAddress(self.device),
            "deviceDesc": self.device.description,
            "deviceStatus": self.device.status, "error1": self.errors[0],
            "error2": self.errors[1], "error3": self.errors[2]
        }
        helpers.assertOutput(self, output, string)

    def testStartTestCores(self):
        output = '''%s [%s] START %s
%s [%s] START %s
%s [%s] START %s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        self.device.cores = self.cores
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        output %= (_deviceDateTime(self.device)[1], self.device.name, suite.id,
                   _deviceDateTime(self.device)[1], self.device.name, case.id,
                   _deviceDateTime(self.device)[1], self.device.name, step.id)
        helpers.assertOutput(self, output, string)

    def testStartStopTestCores(self):
        output = '''%(deviceTime)s [%(deviceName)s] START %(suiteId)s
%(deviceTime)s [%(deviceName)s] START %(caseId)s
%(deviceTime)s [%(deviceName)s] START %(stepId)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(stepId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
	Core dump: %(core2Path)s
	Core dump: %(core3Path)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(caseId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
	Core dump: %(core2Path)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(suiteId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 3.75
        self.device.cores = self.cores
        channel.stopTest(step, self.device)
        self.device.cores = self.cores[:2]
        channel.stopTest(case, self.device)
        self.device.cores = self.cores[:1]
        channel.stopTest(suite, self.device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "caseId": case.id, "stepId": step.id,
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceTime": _deviceDateTime(self.device)[1],
            "deviceTimeEnd": _deviceDateTime(self.device, True)[1],
            "core1Path": self.cores[0].path, "core2Path": self.cores[1].path,
            "core3Path": self.cores[2].path
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTestCoresVerbose(self):
        output = output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
	Core dump: %(core2Date)s [%(core2Path)s] %(core2Size)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
	Core dump: %(core2Date)s [%(core2Path)s] %(core2Size)s
	Core dump: %(core3Date)s [%(core3Path)s] %(core3Size)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 3.75
        self.device.cores = self.cores[:1]
        channel.stopTest(step, self.device)
        self.device.cores = self.cores[:2]
        channel.stopTest(case, self.device)
        self.device.cores = self.cores
        channel.stopTest(suite, self.device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteAttrs": _resultAttrs(suite),
            "caseId": case.id, "casePath": case.path,
            "caseAttrs": _resultAttrs(case),
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepAttrs": _resultAttrs(step), "stepArgs": _stepArgs(step),
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": helpers.deviceDateTime(self.device),
            "deviceDateEnd": helpers.deviceDateTime(self.device, True),
            "deviceAddr": _deviceAddress(self.device),
            "deviceDesc": self.device.description,
            "deviceStatus": self.device.status,
            "core1Path": self.cores[0].path,
            "core1Date": ' '.join(utils.localTime(self.cores[0].mtime)),
            "core1Size": utils.sizeToString(self.cores[0].size),
            "core2Path": self.cores[1].path,
            "core2Date": ' '.join(utils.localTime(self.cores[1].mtime)),
            "core2Size": utils.sizeToString(self.cores[1].size),
            "core3Path": self.cores[2].path,
            "core3Date": ' '.join(utils.localTime(self.cores[2].mtime)),
            "core3Size": utils.sizeToString(self.cores[2].size)
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTestErrorsCores(self):
        output = '''%(deviceTime)s [%(deviceName)s] START %(suiteId)s
%(deviceTime)s [%(deviceName)s] START %(caseId)s
%(deviceTime)s [%(deviceName)s] START %(stepId)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(stepId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
	Core dump: %(core2Path)s
	Core dump: %(core3Path)s
%(error1)s
%(error2)s
%(error3)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(caseId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
	Core dump: %(core2Path)s
	Core dump: %(core3Path)s
%(error1)s
%(error2)s
%(error3)s
%(deviceTimeEnd)s [%(deviceName)s] STOP  %(suiteId)s [%(deviceStatus)s]
	Core dump: %(core1Path)s
	Core dump: %(core2Path)s
	Core dump: %(core3Path)s
%(error1)s
%(error2)s
%(error3)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 3.75
        self.device.errors = self.errors
        self.device.cores = self.cores
        channel.stopTest(step, self.device)
        channel.stopTest(case, self.device)
        channel.stopTest(suite, self.device)
        channel.stop()
        output %= {
            "suiteId": suite.id, "caseId": case.id, "stepId": step.id,
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceTime": _deviceDateTime(self.device)[1],
            "deviceTimeEnd": _deviceDateTime(self.device, True)[1],
            "error1": self.errors[0], "error2": self.errors[1],
            "error3": self.errors[2], "core1Path": self.cores[0].path,
            "core2Path": self.cores[1].path, "core3Path": self.cores[2].path
        }
        helpers.assertOutput(self, output, string)

    def testStartStopTestErrorsCoresVerbose(self):
        output = '''%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
%(deviceDate)s -------------------- START --------------------
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test step ID: %(stepId)s
	Function: %(stepFunc)s(%(stepArgs)s)
	Path: %(stepPath)s
		%(stepAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
	Core dump: %(core2Date)s [%(core2Path)s] %(core2Size)s
	Core dump: %(core3Date)s [%(core3Path)s] %(core3Size)s
%(error1)s
%(error2)s
%(error3)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test case ID: %(caseId)s
	Path: %(casePath)s
		%(caseAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
	Core dump: %(core2Date)s [%(core2Path)s] %(core2Size)s
	Core dump: %(core3Date)s [%(core3Path)s] %(core3Size)s
%(error1)s
%(error2)s
%(error3)s
%(deviceDateEnd)s -------------------- STOP -------------------- [%(deviceStatus)s]
	%(deviceName)s: [%(deviceAddr)s] %(deviceDesc)s
	Test suite ID: %(suiteId)s
	Path: %(suitePath)s
		%(suiteAttrs)s
	Core dump: %(core1Date)s [%(core1Path)s] %(core1Size)s
	Core dump: %(core2Date)s [%(core2Path)s] %(core2Size)s
	Core dump: %(core3Date)s [%(core3Path)s] %(core3Size)s
%(error1)s
%(error2)s
%(error3)s
'''
        string = cStringIO.StringIO()
        suites, cases, steps = helpers.structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        output %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteAttrs": _resultAttrs(suite),
            "caseId": case.id, "casePath": case.path,
            "caseAttrs": _resultAttrs(case),
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepAttrs": _resultAttrs(step), "stepArgs": _stepArgs(step),
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": helpers.deviceDateTime(self.device),
            "deviceDateEnd": helpers.deviceDateTime(self.device, True),
            "deviceAddr": _deviceAddress(self.device),
            "deviceDesc": self.device.description,
            "deviceStatus": self.device.status, "error1": self.errors[0],
            "error2": self.errors[1], "error3": self.errors[2],
            "core1Path": self.cores[0].path,
            "core1Date": ' '.join(utils.localTime(self.cores[0].mtime)),
            "core1Size": utils.sizeToString(self.cores[0].size),
            "core2Path": self.cores[1].path,
            "core2Date": ' '.join(utils.localTime(self.cores[1].mtime)),
            "core2Size": utils.sizeToString(self.cores[1].size),
            "core3Path": self.cores[2].path,
            "core3Date": ' '.join(utils.localTime(self.cores[2].mtime)),
            "core3Size": utils.sizeToString(self.cores[2].size)
        }
        channel = streamchannel.StreamChannel("Test", stream=string,
                                              verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.errors = self.errors
        self.device.cores = self.cores
        channel.stopTest(step, self.device)
        channel.stopTest(case, self.device)
        channel.stopTest(suite, self.device)
        channel.stop()
        helpers.assertOutput(self, output, string)

