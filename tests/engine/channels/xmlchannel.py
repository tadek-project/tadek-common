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
import time
import difflib
import unittest
import datetime
import tempfile
import cStringIO

from tadek.core import utils
from tadek.core.config import Config
from tadek.core.structs import FileDetails
from tadek.engine import channels
from tadek.engine import testexec
from tadek.engine import testresult
from tadek.engine.channels.xmlchannel import XmlChannel

from engine.commons import FakeDevice

__all__ = ["XmlChannelTest", "XmlChannelTestVerbose", "XmlChannelTestRead",
           "XmlChannelTestAsymmetric", "XmlChannelTestErrorsCores"]

_PATH = os.path.abspath(os.path.curdir)
_STEP_FUNC = "tadek.teststeps.tests.stepFunc"


def _assertXML(expected, current):
    if expected != current:
        assert False, '\n'+''.join(difflib.unified_diff(expected.splitlines(1),
                                                        current.splitlines(1)))
    
def _stepResult(name="Step", parent=None):
    attrs = {
        "description": "Description of test step: %s" % name
    }
    args = {
        "kwarg": "Argument of test step: %s" % name
    }
    return testresult.TestStepResult(id=name, path=_PATH, func=_STEP_FUNC,
                                     parent=parent, attrs=attrs, args=args)

def _caseResult(name="Case", parent=None):
    attrs = {
        "description": "Description of test case: %s" % name
    }
    return testresult.TestCaseResult(id=name, path=_PATH,
                                     parent=parent, attrs=attrs)

def _suiteResult(name="Suite", parent=None):
    attrs = {
        "description": "Description of test suite: %s" % name
    }
    return testresult.TestSuiteResult(id=name, path=_PATH,
                                      parent=parent, attrs=attrs)

def _structResult(nsuites=0, ncases=0, nsteps=0):
    suites = [_suiteResult("Suite%d" % (i + 1)) for i in xrange(nsuites)]
    if nsuites:
        cases = [_caseResult("Case%d" % (i + 1), suite) for i in xrange(ncases)
                                                        for suite in suites]
    else:
        cases = [_caseResult("Case%d" % (i + 1)) for i in xrange(ncases)]
    steps = [_stepResult("Step%d" % (i + 1), case) for i in xrange(nsteps)
                                                   for case in cases]
    return suites, cases, steps


class TestXmlChannel(XmlChannel):
    def write(self):
        fd = self.filePath()
        fd.seek(0)
        utils.saveXml(self._root, fd, xslt=self._xslt)
        fd.truncate()


class XmlChannelTest(unittest.TestCase):
    def setUp(self):
        self.device = testresult.DeviceExecResult(FakeDevice("Device"))
        self.device.date = datetime.datetime.now()
        self.device.status = testexec.STATUS_NOT_COMPLETED

    def testStartStop(self):
        expectedXML = ''
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTestStep(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <step>
        <id>%s</id>
        <path>%s</path>
        <function>%s</function>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children />
    </step>
</results>
'''
        result = _stepResult()
        string = cStringIO.StringIO()
        expectedXML %= (result.id, result.path, result.func,
                        self.device.name, self.device.status)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTestStep(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <step>
        <id>%s</id>
        <path>%s</path>
        <function>%s</function>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </step>
</results>
'''
        result = _stepResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        self.device.time = 2.6
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        expectedXML %= (result.id, result.path, result.func,
                        self.device.name, self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestStep(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <step>
        <id>%s</id>
        <path>%s</path>
        <function>%s</function>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </step>
</results>
'''
        result = _stepResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 5.1
        self.device.status = testexec.STATUS_FAILED
        channel.stopTest(result, self.device)
        channel.stop()
        self.failUnless(channel.isActive())
        expectedXML %= (result.id, result.path, result.func,
                        self.device.name, self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartTestCase(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <case>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children />
    </case>
</results>
'''
        result = _caseResult()
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status)
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTestCase(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <case>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </case>
</results>
'''
        result = _caseResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        self.device.time = 5.6
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestCase(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <case>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </case>
</results>
'''
        result = _caseResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 6.5
        self.device.status = testexec.STATUS_ERROR
        channel.stopTest(result, self.device)
        channel.stop()
        self.failUnless(channel.isActive())
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartTestSuite(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        result = _suiteResult()
        string = cStringIO.StringIO()
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        channel.startTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTestSuite(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        result = _suiteResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.failIf(channel.isActive())
        self.device.time = 3.4
        self.device.status = testexec.STATUS_FAILED
        channel.stopTest(result, self.device)
        self.failUnless(channel.isActive())
        channel.stop()
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestSuite(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        result = _suiteResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        self.failIf(channel.isActive())
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 4.3
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(result, self.device)
        channel.stop()
        self.failUnless(channel.isActive())
        expectedXML %= (result.id, result.path, self.device.name,
                        self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartTest1Suite1Case(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                    </device>
                </devices>
                <children />
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1)
        suite, case = suites[0], cases[0]
        expectedXML %= (suite.id, suite.path, self.device.name,
                        self.device.status, case.id, case.path,
                        self.device.name, self.device.status)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest1Suite1Case(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1)
        suite, case = suites[0], cases[0]
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        self.device.time = 2.7
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(case, self.device)
        channel.stopTest(suite, self.device)
        channel.stop()
        expectedXML %= (suite.id, suite.path, self.device.name,
                        self.device.status, self.device.time,
                        case.id, case.path, self.device.name,
                        self.device.status, self.device.time)
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest1Suite3Cases_3Devices(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
            <device>
                <name>%s</name>
                <status>%s</status>
                <time>%s</time>
            </device>
        </devices>
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 3)
        suite, case1, case2, case3 = suites[0], cases[0], cases[1], cases[2]
        device1 = testresult.DeviceExecResult(FakeDevice("Device1"))
        device1.date = datetime.datetime.now()
        device1.status = testexec.STATUS_PASSED
        device1.time = 3.125
        device2 = testresult.DeviceExecResult(FakeDevice("Device2"))
        device2.date = datetime.datetime.now()
        device2.status = testexec.STATUS_FAILED
        device2.time = 2.25
        device3 = testresult.DeviceExecResult(FakeDevice("Device3"))
        device3.date = datetime.datetime.now()
        device3.status = testexec.STATUS_ERROR
        device3.time = 1.875
        expectedXML %= (suite.id, suite.path,
                        device1.name, device1.status, device1.time,
                        device2.name, device2.status, device2.time,
                        device3.name, device3.status, device3.time,
                        case1.id, case1.path,
                        device1.name, device1.status, device1.time,
                        case2.id, case2.path,
                        device2.name, device2.status, device2.time,
                        case3.id, case3.path,
                        device3.name, device3.status, device3.time)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, device1)
        channel.startTest(case1, device1)
        channel.startTest(suite, device2)
        channel.startTest(case2, device2)
        channel.startTest(suite, device3)
        channel.startTest(case3, device3)
        channel.stopTest(case1, device1)
        channel.stopTest(suite, device1)
        channel.stopTest(case3, device3)
        channel.stopTest(suite, device3)
        channel.stopTest(case2, device2)
        channel.stopTest(suite, device2)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTest1Suite1Case1Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "deviceName": self.device.name,
            "deviceStatus": self.device.status
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest2Suites2Cases2Steps(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suite1Id)s</id>
        <path>%(suite1Path)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <time>%(deviceTime)s</time>
            </device>
        </devices>
        <children>
            <case>
                <id>%(case11Id)s</id>
                <path>%(case11Path)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step111Id)s</id>
                        <path>%(step111Path)s</path>
                        <function>%(step111Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                    <step>
                        <id>%(step112Id)s</id>
                        <path>%(step112Path)s</path>
                        <function>%(step112Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
            <case>
                <id>%(case12Id)s</id>
                <path>%(case12Path)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step121Id)s</id>
                        <path>%(step121Path)s</path>
                        <function>%(step121Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                    <step>
                        <id>%(step122Id)s</id>
                        <path>%(step122Path)s</path>
                        <function>%(step122Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
    <suite>
        <id>%(suite2Id)s</id>
        <path>%(suite2Path)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <time>%(deviceTime)s</time>
            </device>
        </devices>
        <children>
            <case>
                <id>%(case21Id)s</id>
                <path>%(case21Path)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step211Id)s</id>
                        <path>%(step211Path)s</path>
                        <function>%(step211Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                    <step>
                        <id>%(step212Id)s</id>
                        <path>%(step212Path)s</path>
                        <function>%(step212Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
            <case>
                <id>%(case22Id)s</id>
                <path>%(case22Path)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step221Id)s</id>
                        <path>%(step221Path)s</path>
                        <function>%(step221Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                    <step>
                        <id>%(step222Id)s</id>
                        <path>%(step222Path)s</path>
                        <function>%(step222Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(2, 2, 2)
        suite1, suite2 = suites
        case11, case21, case12, case22 = cases
        step111,step211,step121,step221, step112,step212,step122,step222 = steps
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        self.device.time = 1.125
        self.device.status = testexec.STATUS_PASSED
        channel.startTest(suite1, self.device)
        channel.startTest(case11, self.device)
        channel.startTest(step111, self.device)
        channel.stopTest(step111, self.device)
        channel.startTest(step112, self.device)
        channel.stopTest(step112, self.device)
        channel.stopTest(case11, self.device)
        channel.startTest(case12, self.device)
        channel.startTest(step121, self.device)
        channel.stopTest(step121, self.device)
        channel.startTest(step122, self.device)
        channel.stopTest(step122, self.device)
        channel.stopTest(case12, self.device)
        channel.stopTest(suite1, self.device)
        channel.startTest(suite2, self.device)
        channel.startTest(case21, self.device)
        channel.startTest(step211, self.device)
        channel.stopTest(step211, self.device)
        channel.startTest(step212, self.device)
        channel.stopTest(step212, self.device)
        channel.stopTest(case21, self.device)
        channel.startTest(case22, self.device)
        channel.startTest(step221, self.device)
        channel.stopTest(step221, self.device)
        channel.startTest(step222, self.device)
        channel.stopTest(step222, self.device)
        channel.stopTest(case22, self.device)
        channel.stopTest(suite2, self.device)
        channel.stop()
        expectedXML %= {
            "suite1Id": suite1.id, "suite1Path": suite1.path,
            "case11Id": case11.id, "case11Path": case11.path,
            "step111Id": step111.id, "step111Path": step111.path,
            "step111Func": step111.func,
            "step112Id": step112.id, "step112Path": step112.path,
            "step112Func": step112.func,
            "case12Id": case12.id, "case12Path": case12.path,
            "step121Id": step121.id, "step121Path": step121.path,
            "step121Func": step121.func,
            "step122Id": step122.id, "step122Path": step122.path,
            "step122Func": step122.func,
            "suite2Id": suite2.id, "suite2Path": suite2.path,
            "case21Id": case21.id, "case21Path": case21.path,
            "step211Id": step211.id, "step211Path": step211.path,
            "step211Func": step211.func,
            "step212Id": step212.id, "step212Path": step212.path,
            "step212Func": step212.func,
            "case22Id": case22.id, "case22Path": case22.path,
            "step221Id": step221.id, "step221Path": step221.path,
            "step221Func": step221.func,
            "step222Id": step222.id, "step222Path": step222.path,
            "step222Func": step222.func,
            "deviceName": self.device.name,
            "deviceStatus": self.device.status,
            "deviceTime": self.device.time,
        }
        _assertXML(expectedXML, string.getvalue())


class XmlChannelTestVerbose(unittest.TestCase):
    def setUp(self):
        device = FakeDevice("Device")
        device.description = "Description of the device"
        self.device = testresult.DeviceExecResult(device)
        self.device.date = datetime.datetime.now()
        self.device.status = testexec.STATUS_NOT_COMPLETED

    def testStartTestStep(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <step>
        <id>%s</id>
        <path>%s</path>
        <function>%s</function>
        <attributes>
            <description>%s</description>
        </attributes>
        <arguments>
            <kwarg>%s</kwarg>
        </arguments>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </step>
</results>
'''
        result = _stepResult()
        string = cStringIO.StringIO()
        expectedXML %= (result.id, result.path, result.func,
                        result.attrs["description"], result.args["kwarg"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date),
                        self.device.address, self.device.port,
                        self.device.description)
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestStep(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <step>
        <id>%s</id>
        <path>%s</path>
        <function>%s</function>
        <attributes>
            <description>%s</description>
        </attributes>
        <arguments>
            <kwarg>%s</kwarg>
        </arguments>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <time>%s</time>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </step>
</results>
'''
        result = _stepResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 5.1
        self.device.status = testexec.STATUS_FAILED
        channel.stopTest(result, self.device)
        channel.stop()
        expectedXML %= (result.id, result.path, result.func,
                        result.attrs["description"], result.args["kwarg"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date), self.device.time,
                        self.device.address, self.device.port,
                        self.device.description)
        _assertXML(expectedXML, string.getvalue())

    def testStartTestCase(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <case>
        <id>%s</id>
        <path>%s</path>
        <attributes>
            <description>%s</description>
        </attributes>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </case>
</results>
'''
        result = _caseResult()
        expectedXML %= (result.id, result.path, result.attrs["description"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date),
                        self.device.address, self.device.port,
                        self.device.description)
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestCase(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <case>
        <id>%s</id>
        <path>%s</path>
        <attributes>
            <description>%s</description>
        </attributes>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <time>%s</time>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </case>
</results>
'''
        result = _caseResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 6.5
        self.device.status = testexec.STATUS_ERROR
        channel.stopTest(result, self.device)
        channel.stop()
        expectedXML %= (result.id, result.path, result.attrs["description"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date), self.device.time,
                        self.device.address, self.device.port,
                        self.device.description)
        _assertXML(expectedXML, string.getvalue())

    def testStartTestSuite(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <attributes>
            <description>%s</description>
        </attributes>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        result = _suiteResult()
        string = cStringIO.StringIO()
        expectedXML %= (result.id, result.path, result.attrs["description"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date),
                        self.device.address, self.device.port,
                        self.device.description)
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestSuite(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <attributes>
            <description>%s</description>
        </attributes>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
                <date>%s</date>
                <time>%s</time>
                <address>%s</address>
                <port>%s</port>
                <description>%s</description>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        result = _suiteResult()
        string = cStringIO.StringIO()
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(result, self.device)
        self.device.time = 4.3
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(result, self.device)
        channel.stop()
        expectedXML %= (result.id, result.path, result.attrs["description"],
                        self.device.name, self.device.status,
                        utils.timeToString(self.device.date), self.device.time,
                        self.device.address, self.device.port,
                        self.device.description)
        _assertXML(expectedXML, string.getvalue())

    def testStartTest1Suite1Case1Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes>
            <description>%(suiteDesc)s</description>
        </attributes>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <date>%(deviceDate)s</date>
                <address>%(deviceAddr)s</address>
                <port>%(devicePort)s</port>
                <description>%(deviceDesc)s</description>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <attributes>
                    <description>%(caseDesc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <date>%(deviceDate)s</date>
                        <address>%(deviceAddr)s</address>
                        <port>%(devicePort)s</port>
                        <description>%(deviceDesc)s</description>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <attributes>
                            <description>%(stepDesc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(stepArg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <date>%(deviceDate)s</date>
                                <address>%(deviceAddr)s</address>
                                <port>%(devicePort)s</port>
                                <description>%(deviceDesc)s</description>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        device = self.device
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteDesc": suite.attrs["description"],
            "caseId": case.id, "casePath": case.path,
            "caseDesc": case.attrs["description"],
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepDesc": step.attrs["description"],"stepArg": step.args["kwarg"],
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceDate": utils.timeToString(device.date),
            "deviceAddr": device.address, "devicePort": device.port,
            "deviceDesc": device.description
        }
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest1Suite1Case1Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes>
            <description>%(suiteDesc)s</description>
        </attributes>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <date>%(deviceDate)s</date>
                <time>%(deviceTime)s</time>
                <address>%(deviceAddr)s</address>
                <port>%(devicePort)s</port>
                <description>%(deviceDesc)s</description>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <attributes>
                    <description>%(caseDesc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <date>%(deviceDate)s</date>
                        <time>%(deviceTime)s</time>
                        <address>%(deviceAddr)s</address>
                        <port>%(devicePort)s</port>
                        <description>%(deviceDesc)s</description>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <attributes>
                            <description>%(stepDesc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(stepArg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <date>%(deviceDate)s</date>
                                <time>%(deviceTime)s</time>
                                <address>%(deviceAddr)s</address>
                                <port>%(devicePort)s</port>
                                <description>%(deviceDesc)s</description>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        device = self.device
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 7.5
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(step, self.device)
        channel.stopTest(case, self.device)
        channel.stopTest(suite, self.device)
        channel.stop()
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteDesc": suite.attrs["description"],
            "caseId": case.id, "casePath": case.path,
            "caseDesc": case.attrs["description"],
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepDesc": step.attrs["description"],"stepArg": step.args["kwarg"],
            "deviceName": device.name, "deviceStatus": device.status,
            "deviceDate": utils.timeToString(device.date),
            "deviceAddr": device.address, "devicePort": device.port,
            "deviceDesc": device.description, "deviceTime": device.time
        }
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest1Suite1Case1Step_NoAttrsNoArgs(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes />
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <date>%(deviceDate)s</date>
                <time>%(deviceTime)s</time>
                <address>%(deviceAddr)s</address>
                <port>%(devicePort)s</port>
                <description />
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <attributes />
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <date>%(deviceDate)s</date>
                        <time>%(deviceTime)s</time>
                        <address>%(deviceAddr)s</address>
                        <port>%(devicePort)s</port>
                        <description />
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <attributes />
                        <arguments />
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <date>%(deviceDate)s</date>
                                <time>%(deviceTime)s</time>
                                <address>%(deviceAddr)s</address>
                                <port>%(devicePort)s</port>
                                <description />
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        suite.attrs = case.attrs = step.attrs = step.args = {}
        self.device.description = None
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.time = 7.5
        self.device.status = testexec.STATUS_PASSED
        channel.stopTest(step, self.device)
        channel.stopTest(case, self.device)
        channel.stopTest(suite, self.device)
        channel.stop()
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": utils.timeToString(self.device.date),
            "deviceAddr": self.device.address, "devicePort": self.device.port,
            "deviceTime": self.device.time
        }
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTest1Suite3Cases3Steps_3Devices(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes>
            <description>%(suiteDesc)s</description>
        </attributes>
        <devices>
            <device>
                <name>%(device1Name)s</name>
                <status>%(device1Status)s</status>
                <date>%(device1Date)s</date>
                <time>%(device1Time)s</time>
                <address>%(device1Addr)s</address>
                <port>%(device1Port)s</port>
                <description>%(device1Desc)s</description>
            </device>
            <device>
                <name>%(device2Name)s</name>
                <status>%(device2Status)s</status>
                <date>%(device2Date)s</date>
                <time>%(device2Time)s</time>
                <address>%(device2Addr)s</address>
                <port>%(device2Port)s</port>
                <description>%(device2Desc)s</description>
            </device>
            <device>
                <name>%(device3Name)s</name>
                <status>%(device3Status)s</status>
                <date>%(device3Date)s</date>
                <time>%(device3Time)s</time>
                <address>%(device3Addr)s</address>
                <port>%(device3Port)s</port>
                <description>%(device3Desc)s</description>
            </device>
        </devices>
        <children>
            <case>
                <id>%(case1Id)s</id>
                <path>%(case1Path)s</path>
                <attributes>
                    <description>%(case1Desc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(device1Name)s</name>
                        <status>%(device1Status)s</status>
                        <date>%(device1Date)s</date>
                        <time>%(device1Time)s</time>
                        <address>%(device1Addr)s</address>
                        <port>%(device1Port)s</port>
                        <description>%(device1Desc)s</description>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step1Id)s</id>
                        <path>%(step1Path)s</path>
                        <function>%(step1Func)s</function>
                        <attributes>
                            <description>%(step1Desc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(step1Arg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(device1Name)s</name>
                                <status>%(device1Status)s</status>
                                <date>%(device1Date)s</date>
                                <time>%(device1Time)s</time>
                                <address>%(device1Addr)s</address>
                                <port>%(device1Port)s</port>
                                <description>%(device1Desc)s</description>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
            <case>
                <id>%(case2Id)s</id>
                <path>%(case2Path)s</path>
                <attributes>
                    <description>%(case2Desc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(device2Name)s</name>
                        <status>%(device2Status)s</status>
                        <date>%(device2Date)s</date>
                        <time>%(device2Time)s</time>
                        <address>%(device2Addr)s</address>
                        <port>%(device2Port)s</port>
                        <description>%(device2Desc)s</description>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step2Id)s</id>
                        <path>%(step2Path)s</path>
                        <function>%(step2Func)s</function>
                        <attributes>
                            <description>%(step2Desc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(step2Arg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(device2Name)s</name>
                                <status>%(device2Status)s</status>
                                <date>%(device2Date)s</date>
                                <time>%(device2Time)s</time>
                                <address>%(device2Addr)s</address>
                                <port>%(device2Port)s</port>
                                <description>%(device2Desc)s</description>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
            <case>
                <id>%(case3Id)s</id>
                <path>%(case3Path)s</path>
                <attributes>
                    <description>%(case3Desc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(device3Name)s</name>
                        <status>%(device3Status)s</status>
                        <date>%(device3Date)s</date>
                        <time>%(device3Time)s</time>
                        <address>%(device3Addr)s</address>
                        <port>%(device3Port)s</port>
                        <description>%(device3Desc)s</description>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step3Id)s</id>
                        <path>%(step3Path)s</path>
                        <function>%(step3Func)s</function>
                        <attributes>
                            <description>%(step3Desc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(step3Arg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(device3Name)s</name>
                                <status>%(device3Status)s</status>
                                <date>%(device3Date)s</date>
                                <time>%(device3Time)s</time>
                                <address>%(device3Addr)s</address>
                                <port>%(device3Port)s</port>
                                <description>%(device3Desc)s</description>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        device = self.device
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 3, 1)
        suite = suites[0]
        case1, case2, case3 = cases
        step1, step2, step3 = steps
        device1 = testresult.DeviceExecResult(FakeDevice("Device1"))
        device1.address = "192.168.1.101"
        device1.port = 10001
        device1.description = "Description of the device1"
        device1.date = datetime.datetime.now()
        device1.status = testexec.STATUS_PASSED
        device1.time = 3.125
        device2 = testresult.DeviceExecResult(FakeDevice("Device2"))
        device2.address = "192.168.1.102"
        device2.port = 10002
        device2.description = "Description of the device2"
        device2.date = datetime.datetime.now()
        device2.status = testexec.STATUS_FAILED
        device2.time = 2.25
        device3 = testresult.DeviceExecResult(FakeDevice("Device3"))
        device3.address = "192.168.1.103"
        device3.port = 10003
        device3.description = "Description of the device3"
        device3.date = datetime.datetime.now()
        device3.status = testexec.STATUS_ERROR
        device3.time = 1.875
        expectedXML %= {
          "suiteId": suite.id, "suitePath": suite.path,
          "suiteDesc": suite.attrs["description"],
          "case1Id": case1.id, "case1Path": case1.path,
          "case1Desc": case1.attrs["description"],
          "case2Id": case2.id, "case2Path": case2.path,
          "case2Desc": case2.attrs["description"],
          "case3Id": case3.id, "case3Path": case3.path,
          "case3Desc": case3.attrs["description"],
          "step1Id":step1.id, "step1Path":step1.path, "step1Func":step1.func,
          "step1Desc":step1.attrs["description"],"step1Arg":step1.args["kwarg"],
          "step2Id":step2.id, "step2Path":step2.path, "step2Func":step2.func,
          "step2Desc":step2.attrs["description"],"step2Arg":step2.args["kwarg"],
          "step3Id":step3.id, "step3Path":step3.path, "step3Func":step3.func,
          "step3Desc":step3.attrs["description"],"step3Arg":step3.args["kwarg"],
          "device1Name": device1.name, "device1Status": device1.status,
          "device1Date": utils.timeToString(device1.date),
          "device1Addr": device1.address, "device1Port": device1.port,
          "device1Desc": device1.description, "device1Time": device1.time,
          "device2Name": device2.name, "device2Status": device2.status,
          "device2Date": utils.timeToString(device2.date),
          "device2Addr": device2.address, "device2Port": device2.port,
          "device2Desc": device2.description, "device2Time": device2.time,
          "device3Name": device3.name, "device3Status": device3.status,
          "device3Date": utils.timeToString(device3.date),
          "device3Addr": device3.address, "device3Port": device3.port,
          "device3Desc": device3.description, "device3Time": device3.time
        }
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(suite, device1)
        channel.startTest(case1, device1)
        channel.startTest(step1, device1)
        channel.startTest(suite, device2)
        channel.startTest(case2, device2)
        channel.startTest(step2, device2)
        channel.startTest(suite, device3)
        channel.startTest(case3, device3)
        channel.startTest(step3, device3)
        channel.stopTest(step3, device3)
        channel.stopTest(case3, device3)
        channel.stopTest(suite, device3)
        channel.stopTest(step1, device1)
        channel.stopTest(case1, device1)
        channel.stopTest(suite, device1)
        channel.stopTest(step2, device2)
        channel.stopTest(case2, device2)
        channel.stopTest(suite, device2)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())


class XmlChannelTestAsymmetric(unittest.TestCase):
    def setUp(self):
        device = FakeDevice("Device")
        self.deviceStart = testresult.DeviceExecResult(device)
        self.deviceStart.date = datetime.datetime.now()
        self.deviceStart.status = testexec.STATUS_NOT_COMPLETED
        self.deviceStop = testresult.DeviceExecResult(device)
        self.deviceStop.date = self.deviceStart.date
        self.deviceStop.time = 2.875
        self.deviceStop.status = testexec.STATUS_PASSED

    def testStartTestSuite_1Suite1Case(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children />
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1)
        suite, case = suites[0], cases[0]
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        expectedXML %= (suite.id, suite.path,
                        self.deviceStart.name, self.deviceStart.status)
        channel.start(None)
        channel.startTest(suite, self.deviceStart)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTestCase_1Suite1Case(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices />
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1)
        suite, case = suites[0], cases[0]
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        expectedXML %= (suite.id, suite.path, case.id, case.path,
                        self.deviceStop.name, self.deviceStop.status,
                        self.deviceStop.time)
        channel.start(None)
        channel.stopTest(case, self.deviceStop)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTestStep_1Suite1Case1Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices />
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices />
                <children>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices>
                            <device>
                                <name>%s</name>
                                <status>%s</status>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= (suite.id, suite.path, case.id, case.path,
                        step.id, step.path, step.func,
                        self.deviceStart.name, self.deviceStart.status)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(step, self.deviceStart)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTestCase_1Suite1Case2Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices />
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices />
                        <children />
                    </step>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices />
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 2)
        suite, case, step1, step2 = suites[0], cases[0], steps[0], steps[1]
        expectedXML %= (suite.id, suite.path, case.id, case.path,
                        self.deviceStop.name, self.deviceStop.status,
                        self.deviceStop.time, step1.id, step1.path, step1.func,
                        step2.id, step2.path, step2.func)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.stopTest(case, self.deviceStop)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTest2Step_1Suite1Case2Step(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices />
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices />
                <children>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices />
                        <children />
                    </step>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices>
                            <device>
                                <name>%s</name>
                                <status>%s</status>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 2)
        suite, case, step1, step2 = suites[0], cases[0], steps[0], steps[1]
        expectedXML %= (suite.id, suite.path, case.id, case.path,
                        step1.id, step1.path, step1.func,
                        step2.id, step2.path, step2.func,
                        self.deviceStart.name, self.deviceStart.status)
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(step2, self.deviceStart)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStopTest1Step_1Suite2Cases2Steps(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices />
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices />
                <children>
                    <step>
                        <id>%s</id>
                        <path>%s</path>
                        <function>%s</function>
                        <devices>
                            <device>
                                <name>%s</name>
                                <status>%s</status>
                                <time>%s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 2, 1)
        suite, case, step = suites[0], cases[1], steps[1]
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        expectedXML %= (suite.id, suite.path, case.id, case.path,
                        step.id, step.path, step.func,
                        self.deviceStop.name, self.deviceStop.status,
                        self.deviceStop.time)
        channel.start(None)
        channel.stopTest(step, self.deviceStop)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTest1Suite1Case_StopTest1Case_1Suite2Cases(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%s</id>
        <path>%s</path>
        <devices>
            <device>
                <name>%s</name>
                <status>%s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%s</id>
                <path>%s</path>
                <devices>
                    <device>
                        <name>%s</name>
                        <status>%s</status>
                        <time>%s</time>
                    </device>
                </devices>
                <children />
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 2)
        suite, case = suites[0], cases[0]
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        expectedXML %= (suite.id, suite.path, self.deviceStart.name,
                        self.deviceStart.status, case.id, case.path,
                        self.deviceStop.name, self.deviceStop.status,
                        self.deviceStop.time)
        channel.start(None)
        channel.startTest(suite, self.deviceStart)
        channel.startTest(case, self.deviceStart)
        channel.stopTest(case, self.deviceStop)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTest1Suite1Case1Step_StopTest1Step_1Suite1Case2Steps(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(step1Id)s</id>
                        <path>%(step1Path)s</path>
                        <function>%(step1Func)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus1)s</status>
                                <time>%(deviceTime1)s</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                    <step>
                        <id>%(step2Id)s</id>
                        <path>%(step2Path)s</path>
                        <function>%(step2Func)s</function>
                        <devices />
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 2)
        suite, case = suites[0], cases[0]
        step1, step2 = steps
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "step1Id":step1.id, "step1Path":step1.path, "step1Func":step1.func,
            "step2Id":step2.id, "step2Path":step2.path, "step2Func":step2.func,
            "deviceName": self.deviceStart.name,
            "deviceStatus": self.deviceStart.status,
            "deviceStatus1":self.deviceStop.status,
            "deviceTime1":self.deviceStop.time,
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.deviceStart)
        channel.startTest(case, self.deviceStart)
        channel.startTest(step1, self.deviceStart)
        channel.stopTest(step1, self.deviceStop)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())


class XmlChannelTestErrorsCores(unittest.TestCase):
    def setUp(self):
        self.device = testresult.DeviceExecResult(FakeDevice("Device"))
        self.device.date = datetime.datetime.now()
        self.device.status = testexec.STATUS_ERROR
        self.device.time = 3.25
        self.errors = [
            "Error message 1",
            "Error message 2",
            "Error message 3"
        ]
        self.cores = [
            FileDetails("/tmp/core.1", mtime=time.time(), size=1024),
            FileDetails("/tmp/core.2", mtime=(time.time() + 10), size=3527),
            FileDetails("/tmp/core.3", mtime=(time.time() + 20), size=843159)
        ]

    def testStartTestErrors(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "deviceName": self.device.name, "deviceStatus": self.device.status
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        self.device.errors = self.errors
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestErrors(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <time>%(deviceTime)s</time>
                <errors>
                    <error>%(error1)s</error>
                    <error>%(error2)s</error>
                    <error>%(error3)s</error>
                </errors>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                        <errors>
                            <error>%(error1)s</error>
                            <error>%(error2)s</error>
                        </errors>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                                <errors>
                                    <error>%(error1)s</error>
                                </errors>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path, "caseId": case.id,
            "casePath": case.path, "stepId": step.id, "stepPath": step.path,
            "stepFunc": step.func, "deviceName": self.device.name,
            "deviceStatus": self.device.status, "deviceTime": self.device.time,
            "error1": self.errors[0], "error2": self.errors[1],
            "error3": self.errors[2]
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.errors.append(self.errors[0])
        channel.stopTest(step, self.device)
        self.device.errors.append(self.errors[1])
        channel.stopTest(case, self.device)
        self.device.errors.append(self.errors[2])
        channel.stopTest(suite, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartTestCores(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "caseId": case.id, "casePath": case.path,
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "deviceName": self.device.name, "deviceStatus": self.device.status
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        self.device.cores = self.cores
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestCores(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <time>%(deviceTime)s</time>
                <cores>
                    <core>
                        <path>%(core1Path)s</path>
                    </core>
                </cores>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                        <cores>
                            <core>
                                <path>%(core1Path)s</path>
                            </core>
                            <core>
                                <path>%(core2Path)s</path>
                            </core>
                        </cores>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                                <cores>
                                    <core>
                                        <path>%(core1Path)s</path>
                                    </core>
                                    <core>
                                        <path>%(core2Path)s</path>
                                    </core>
                                    <core>
                                        <path>%(core3Path)s</path>
                                    </core>
                                </cores>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path, "caseId": case.id,
            "casePath": case.path, "stepId": step.id, "stepPath": step.path,
            "stepFunc": step.func, "deviceName": self.device.name,
            "deviceStatus": self.device.status, "deviceTime": self.device.time,
            "core1Path": self.cores[0].path, "core2Path": self.cores[1].path,
            "core3Path": self.cores[2].path
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.cores = self.cores
        channel.stopTest(step, self.device)
        self.device.cores = self.cores[:2]
        channel.stopTest(case, self.device)
        self.device.cores = self.cores[:1]
        channel.stopTest(suite, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestCoresVerbose(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes>
            <description>%(suiteDesc)s</description>
        </attributes>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <date>%(deviceDate)s</date>
                <time>%(deviceTime)s</time>
                <address>%(deviceAddr)s</address>
                <port>%(devicePort)s</port>
                <description />
                <cores>
                    <core>
                        <path>%(core1Path)s</path>
                        <date>%(core1Date)s</date>
                        <size>%(core1Size)s</size>
                    </core>
                    <core>
                        <path>%(core2Path)s</path>
                        <date>%(core2Date)s</date>
                        <size>%(core2Size)s</size>
                    </core>
                    <core>
                        <path>%(core3Path)s</path>
                        <date>%(core3Date)s</date>
                        <size>%(core3Size)s</size>
                    </core>
                </cores>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <attributes>
                    <description>%(caseDesc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <date>%(deviceDate)s</date>
                        <time>%(deviceTime)s</time>
                        <address>%(deviceAddr)s</address>
                        <port>%(devicePort)s</port>
                        <description />
                        <cores>
                            <core>
                                <path>%(core1Path)s</path>
                                <date>%(core1Date)s</date>
                                <size>%(core1Size)s</size>
                            </core>
                            <core>
                                <path>%(core2Path)s</path>
                                <date>%(core2Date)s</date>
                                <size>%(core2Size)s</size>
                            </core>
                        </cores>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <attributes>
                            <description>%(stepDesc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(stepArg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <date>%(deviceDate)s</date>
                                <time>%(deviceTime)s</time>
                                <address>%(deviceAddr)s</address>
                                <port>%(devicePort)s</port>
                                <description />
                                <cores>
                                    <core>
                                        <path>%(core1Path)s</path>
                                        <date>%(core1Date)s</date>
                                        <size>%(core1Size)s</size>
                                    </core>
                                </cores>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteDesc": suite.attrs["description"],
            "caseId": case.id, "casePath": case.path,
            "caseDesc": case.attrs["description"],
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepDesc": step.attrs["description"],"stepArg": step.args["kwarg"],
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": utils.timeToString(self.device.date),
            "deviceTime": self.device.time, "deviceAddr": self.device.address,
            "devicePort": self.device.port, "core1Path": self.cores[0].path,
            "core1Date": ' '.join(utils.localTime(self.cores[0].mtime)),
            "core1Size": self.cores[0].size, "core2Path": self.cores[1].path,
            "core2Date": ' '.join(utils.localTime(self.cores[1].mtime)),
            "core2Size": self.cores[1].size, "core3Path": self.cores[2].path,
            "core3Date": ' '.join(utils.localTime(self.cores[2].mtime)),
            "core3Size": self.cores[2].size
        }
        channel = TestXmlChannel("Test", filename=string, verbose=True)
        channel.start(None)
        channel.startTest(suite, self.device)
        channel.startTest(case, self.device)
        channel.startTest(step, self.device)
        self.device.cores = self.cores[:1]
        channel.stopTest(step, self.device)
        self.device.cores = self.cores[:2]
        channel.stopTest(case, self.device)
        self.device.cores = self.cores
        channel.stopTest(suite, self.device)
        channel.stop()
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestErrorsCores(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <time>%(deviceTime)s</time>
                <errors>
                    <error>%(error1)s</error>
                    <error>%(error2)s</error>
                    <error>%(error3)s</error>
                </errors>
                <cores>
                    <core>
                        <path>%(core1Path)s</path>
                    </core>
                    <core>
                        <path>%(core2Path)s</path>
                    </core>
                    <core>
                        <path>%(core3Path)s</path>
                    </core>
                </cores>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <time>%(deviceTime)s</time>
                        <errors>
                            <error>%(error1)s</error>
                            <error>%(error2)s</error>
                            <error>%(error3)s</error>
                        </errors>
                        <cores>
                            <core>
                                <path>%(core1Path)s</path>
                            </core>
                            <core>
                                <path>%(core2Path)s</path>
                            </core>
                            <core>
                                <path>%(core3Path)s</path>
                            </core>
                        </cores>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <time>%(deviceTime)s</time>
                                <errors>
                                    <error>%(error1)s</error>
                                    <error>%(error2)s</error>
                                    <error>%(error3)s</error>
                                </errors>
                                <cores>
                                    <core>
                                        <path>%(core1Path)s</path>
                                    </core>
                                    <core>
                                        <path>%(core2Path)s</path>
                                    </core>
                                    <core>
                                        <path>%(core3Path)s</path>
                                    </core>
                                </cores>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path, "caseId": case.id,
            "casePath": case.path, "stepId": step.id, "stepPath": step.path,
            "stepFunc": step.func, "deviceName": self.device.name,
            "deviceStatus": self.device.status, "deviceTime": self.device.time,
            "error1": self.errors[0], "error2": self.errors[1],
            "error3": self.errors[2], "core1Path": self.cores[0].path,
            "core2Path": self.cores[1].path, "core3Path": self.cores[2].path
        }
        channel = TestXmlChannel("Test", filename=string, verbose=False)
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
        _assertXML(expectedXML, string.getvalue())

    def testStartStopTestErrorsCoresVerbose(self):
        expectedXML = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>%(suiteId)s</id>
        <path>%(suitePath)s</path>
        <attributes>
            <description>%(suiteDesc)s</description>
        </attributes>
        <devices>
            <device>
                <name>%(deviceName)s</name>
                <status>%(deviceStatus)s</status>
                <date>%(deviceDate)s</date>
                <time>%(deviceTime)s</time>
                <address>%(deviceAddr)s</address>
                <port>%(devicePort)s</port>
                <description />
                <errors>
                    <error>%(error1)s</error>
                    <error>%(error2)s</error>
                    <error>%(error3)s</error>
                </errors>
                <cores>
                    <core>
                        <path>%(core1Path)s</path>
                        <date>%(core1Date)s</date>
                        <size>%(core1Size)s</size>
                    </core>
                    <core>
                        <path>%(core2Path)s</path>
                        <date>%(core2Date)s</date>
                        <size>%(core2Size)s</size>
                    </core>
                    <core>
                        <path>%(core3Path)s</path>
                        <date>%(core3Date)s</date>
                        <size>%(core3Size)s</size>
                    </core>
                </cores>
            </device>
        </devices>
        <children>
            <case>
                <id>%(caseId)s</id>
                <path>%(casePath)s</path>
                <attributes>
                    <description>%(caseDesc)s</description>
                </attributes>
                <devices>
                    <device>
                        <name>%(deviceName)s</name>
                        <status>%(deviceStatus)s</status>
                        <date>%(deviceDate)s</date>
                        <time>%(deviceTime)s</time>
                        <address>%(deviceAddr)s</address>
                        <port>%(devicePort)s</port>
                        <description />
                        <errors>
                            <error>%(error1)s</error>
                            <error>%(error2)s</error>
                            <error>%(error3)s</error>
                        </errors>
                        <cores>
                            <core>
                                <path>%(core1Path)s</path>
                                <date>%(core1Date)s</date>
                                <size>%(core1Size)s</size>
                            </core>
                            <core>
                                <path>%(core2Path)s</path>
                                <date>%(core2Date)s</date>
                                <size>%(core2Size)s</size>
                            </core>
                            <core>
                                <path>%(core3Path)s</path>
                                <date>%(core3Date)s</date>
                                <size>%(core3Size)s</size>
                            </core>
                        </cores>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>%(stepId)s</id>
                        <path>%(stepPath)s</path>
                        <function>%(stepFunc)s</function>
                        <attributes>
                            <description>%(stepDesc)s</description>
                        </attributes>
                        <arguments>
                            <kwarg>%(stepArg)s</kwarg>
                        </arguments>
                        <devices>
                            <device>
                                <name>%(deviceName)s</name>
                                <status>%(deviceStatus)s</status>
                                <date>%(deviceDate)s</date>
                                <time>%(deviceTime)s</time>
                                <address>%(deviceAddr)s</address>
                                <port>%(devicePort)s</port>
                                <description />
                                <errors>
                                    <error>%(error1)s</error>
                                    <error>%(error2)s</error>
                                    <error>%(error3)s</error>
                                </errors>
                                <cores>
                                    <core>
                                        <path>%(core1Path)s</path>
                                        <date>%(core1Date)s</date>
                                        <size>%(core1Size)s</size>
                                    </core>
                                    <core>
                                        <path>%(core2Path)s</path>
                                        <date>%(core2Date)s</date>
                                        <size>%(core2Size)s</size>
                                    </core>
                                    <core>
                                        <path>%(core3Path)s</path>
                                        <date>%(core3Date)s</date>
                                        <size>%(core3Size)s</size>
                                    </core>
                                </cores>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        expectedXML %= {
            "suiteId": suite.id, "suitePath": suite.path,
            "suiteDesc": suite.attrs["description"],
            "caseId": case.id, "casePath": case.path,
            "caseDesc": case.attrs["description"],
            "stepId": step.id, "stepPath": step.path, "stepFunc": step.func,
            "stepDesc": step.attrs["description"],"stepArg": step.args["kwarg"],
            "deviceName": self.device.name, "deviceStatus": self.device.status,
            "deviceDate": utils.timeToString(self.device.date),
            "deviceTime": self.device.time, "deviceAddr": self.device.address,
            "devicePort": self.device.port, "error1": self.errors[0],
            "error2": self.errors[1], "error3": self.errors[2],
            "core1Path": self.cores[0].path, "core3Size": self.cores[2].size,
            "core1Date": ' '.join(utils.localTime(self.cores[0].mtime)),
            "core1Size": self.cores[0].size, "core2Path": self.cores[1].path,
            "core2Date": ' '.join(utils.localTime(self.cores[1].mtime)),
            "core2Size": self.cores[1].size, "core3Path": self.cores[2].path,
            "core3Date": ' '.join(utils.localTime(self.cores[2].mtime))
        }
        channel = TestXmlChannel("Test", filename=string, verbose=True)
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
        _assertXML(expectedXML, string.getvalue())


class XmlChannelTestRead(unittest.TestCase):
    _xmlFile = "/tmp/_test_xmlchannel.xml"

    def _device(self, name="Device", description=True,
                status=testexec.STATUS_NOT_COMPLETED, time=0.0):
        device = testresult.DeviceExecResult(FakeDevice(name))
        if description:
            device.description = "Description of %s" % name
        device.status = status
        dt = datetime.datetime.now()
        device.date = datetime.datetime(dt.year, dt.month, dt.day,
                                        dt.hour, dt.minute, dt.second)
        if time:
            device.time = time
        return device

    def _compareDevices(self, device1, device2):
        for attr in ("name", "description", "address", "port",
                     "status", "date", "time", "errors"):
            self.failUnlessEqual(getattr(device1, attr), getattr(device2, attr))
        if device1.cores:
            self.failUnless(device2.cores)
            for core1, core2 in zip(device1.cores, device2.cores):
                self.failUnlessEqual(core1.path, core2.path)
                self.failUnlessEqual(core1.mtime, core2.mtime)
                self.failUnlessEqual(core1.size, core2.size)

    def _compareResults(self, result1, result2):
        self.failUnlessEqual(result1.__class__, result2.__class__)
        attrs = ["id", "path", "attrs"]
        if isinstance(result1, testresult.TestStepResult):
            attrs.extend(("func", "args"))
        for attr in attrs:
            self.failUnlessEqual(getattr(result1, attr), getattr(result2, attr))
        self.failUnlessEqual(len(result1.devices), len(result2.devices))
        for device1, device2 in zip(result1.devices, result2.devices):
            self._compareDevices(device1, device2)
        self.failUnlessEqual(len(result1.children), len(result2.children))
        for child1, child2 in zip(result1.children, result2.children):
            self._compareResults(child1, child2)

    def setUp(self):
        self.channel = XmlChannel("Test", filename=self._xmlFile,
                                  verbose=False, unique=False)
        self.errors = [
            "Error message 1",
            "Error message 2",
            "Error message 3"
        ]
        self.cores = [
            FileDetails("/tmp/core.1", size=1024,
                        mtime=(int(time.time()) + 10.0)),
            FileDetails("/tmp/core.2", size=3527, 
                        mtime=(int(time.time()) + 20.0)),
            FileDetails("/tmp/core.3", size=843159,
                        mtime=(int(time.time()) + 30.0))
        ]

    def tearDown(self):
        path = self.channel.filePath() or self._xmlFile
#        if os.path.exists(path):
#            os.remove(path)

    def testStartTest1Suite1Case(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1)
        suite, case = suites[0], cases[0]
        device = self._device()
        self.channel.start(None)
        self.channel.startTest(suite, device)
        self.channel.startTest(case, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        device.description = device.address = device.port = device.date = None
        suite.attrs = case.attrs = {}
        suite.devices = case.devices = [device]
        self._compareResults(suite, container.children[0])

    def testStartTest1Suite1Case_1Suite1Case1Step(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = self._device()
        self.channel.start(None)
        self.channel.startTest(suite, device)
        self.channel.startTest(case, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        device.description = device.address = device.port = device.date = None
        suite.attrs = case.attrs = step.attrs = step.args = {}
        suite.devices = case.devices = [device]
        self._compareResults(suite, container.children[0])

    def testStartStopTest1Suite1Case1StepVerbose(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = self._device(status=testexec.STATUS_PASSED, time=5.65)
        self.channel.setVerbose(True)
        self.channel.start(None)
        self.channel.startTest(suite, device)
        self.channel.startTest(case, device)
        self.channel.startTest(step, device)
        self.channel.stopTest(step, device)
        self.channel.stopTest(case, device)
        self.channel.stopTest(suite, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        suite.devices = case.devices = step.devices = [device]
        self._compareResults(suite, container.children[0])

    def testStartStopTest1Suite2Cases2StepsVerboseErrors_2Devices(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 2, 1)
        suite, case1, case2, step1, step2 = suites + cases + steps
        device1 = self._device("Device1", time=5.415,
                                status=testexec.STATUS_PASSED)
        device2 = self._device("Device2", time=6.125,
                                status=testexec.STATUS_FAILED)
        device2.errors = self.errors
        self.channel.setVerbose(True)
        self.channel.start(None)
        self.channel.startTest(suite, device1)
        self.channel.startTest(case1, device1)
        self.channel.startTest(step1, device1)
        self.channel.startTest(suite, device2)
        self.channel.startTest(case2, device2)
        self.channel.startTest(step2, device2)
        self.channel.stopTest(step2, device2)
        self.channel.stopTest(case2, device2)
        self.channel.stopTest(suite, device2)
        self.channel.stopTest(step1, device1)
        self.channel.stopTest(case1, device1)
        self.channel.stopTest(suite, device1)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        suite.devices = [device1, device2]
        case1.devices = step1.devices = [device1]
        case2.devices = step2.devices = [device2]
        self._compareResults(suite, container.children[0])

    def testStartStopTest1Suite1Case1StepCores(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = self._device(status=testexec.STATUS_ERROR, time=3.25)
        device.cores = self.cores
        self.channel.start(None)
        self.channel.startTest(suite, device)
        self.channel.startTest(case, device)
        self.channel.startTest(step, device)
        self.channel.stopTest(step, device)
        self.channel.stopTest(case, device)
        self.channel.stopTest(suite, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        device.description = device.address = device.port = device.date = None
        suite.attrs = case.attrs = step.attrs = step.args = {}
        suite.devices = case.devices = step.devices = [device]
        for core in self.cores:
            core.mtime = 0.0
            core.size = 0
        self._compareResults(suite, container.children[0])

    def testStartStopTest1Suite1Case1StepCoresVerbose(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(1, 1, 1)
        suite, case, step = suites[0], cases[0], steps[0]
        device = self._device(status=testexec.STATUS_ERROR, time=8.1)
        device.cores = self.cores
        self.channel.setVerbose(True)
        self.channel.start(None)
        self.channel.startTest(suite, device)
        self.channel.startTest(case, device)
        self.channel.startTest(step, device)
        self.channel.stopTest(step, device)
        self.channel.stopTest(case, device)
        self.channel.stopTest(suite, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failUnlessEqual(len(container.children), 1)
        suite.devices = case.devices = step.devices = [device]
        self._compareResults(suite, container.children[0])

    def testStartStopTest2Cases2StepsVerbose(self):
        string = cStringIO.StringIO()
        suites, cases, steps = _structResult(0, 2, 1)
        case1, case2, step1, step2 = cases + steps
        device = self._device(status=testexec.STATUS_PASSED, time=1.875)
        self.channel.setVerbose(True)
        self.channel.start(None)
        self.channel.startTest(case1, device)
        self.channel.startTest(step1, device)
        self.channel.startTest(case2, device)
        self.channel.startTest(step2, device)
        self.channel.stopTest(step2, device)
        self.channel.stopTest(case2, device)
        self.channel.stopTest(step1, device)
        self.channel.stopTest(case1, device)
        self.channel.stop()
        container = self.channel.read(self.channel.filePath())
        self.failIf(container.children)

    def testInvalidTestStepResult(self):
        resultXml = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>Suite1</id>
        <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
        <devices>
            <device>
                <name>Device</name>
                <status>Passed</status>
                <time>3.25</time>
            </device>
        </devices>
        <children>
            <case>
                <id>Suite1.Case1</id>
                <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                <devices>
                    <device>
                        <name>Device</name>
                        <status>Passed</status>
                        <time>3.25</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>Suite1.Case1.Step1</id>
                        <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                        <devices>
                            <device>
                                <name>Device</name>
                                <status>Passed</status>
                                <time>3.25</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        
        fd = open(self._xmlFile, "wb")
        fd.write(resultXml)
        fd.close()
        try:
            self.channel.read(self._xmlFile)
        except channels.TestResultChannelError, err:
            self.failUnlessEqual(err.args[0], "Missing tag: step/function")
        except Exception, err:
            self.failIf(True, err)
        else:
            self.failIf(True)

    def testInvalidTestCaseResult(self):
        resultXml = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>Suite1</id>
        <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
        <devices>
            <device>
                <name>Device</name>
                <status>Passed</status>
                <time>3.25</time>
            </device>
        </devices>
        <children>
            <case>
                <id>Suite1.Case1</id>
                <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                <devices>
                    <device>
                        <name>Device</name>
                        <time>3.25</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>Suite1.Case1.Step1</id>
                        <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                        <function>tadek.teststeps.tests.stepFunc</function>
                        <devices>
                            <device>
                                <name>Device</name>
                                <status>Passed</status>
                                <time>3.25</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        
        fd = open(self._xmlFile, "wb")
        fd.write(resultXml)
        fd.close()
        try:
            self.channel.read(self._xmlFile)
        except channels.TestResultChannelError, err:
            self.failUnlessEqual(err.args[0], "Missing tag: device/status")
        except Exception, err:
            self.failIf(True, err)
        else:
            self.failIf(True)

    def testInvalidTestSuiteResult(self):
        resultXml = '''<?xml version='1.0' encoding='utf-8'?>
<results>
    <suite>
        <id>Suite1</id>
        <devices>
            <device>
                <name>Device</name>
                <status>Passed</status>
                <time>3.25</time>
            </device>
        </devices>
        <children>
            <case>
                <id>Suite1.Case1</id>
                <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                <devices>
                    <device>
                        <name>Device</name>
                        <status>Passed</status>
                        <time>3.25</time>
                    </device>
                </devices>
                <children>
                    <step>
                        <id>Suite1.Case1.Step1</id>
                        <path>/home/mlyko/projects/tadek/repo-devel/tadek-common</path>
                        <function>tadek.teststeps.tests.stepFunc</function>
                        <devices>
                            <device>
                                <name>Device</name>
                                <status>Passed</status>
                                <time>3.25</time>
                            </device>
                        </devices>
                        <children />
                    </step>
                </children>
            </case>
        </children>
    </suite>
</results>
'''
        
        fd = open(self._xmlFile, "wb")
        fd.write(resultXml)
        fd.close()
        try:
            self.channel.read(self._xmlFile)
        except channels.TestResultChannelError, err:
            self.failUnlessEqual(err.args[0], "Missing tag: suite/path")
        except Exception, err:
            self.failIf(True, err)
        else:
            self.failIf(True)

if __name__ == "__main__":
    unittest.main()

