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
import difflib
import datetime

from tadek.core import utils
from tadek.engine import testexec
from tadek.engine import testresult

from engine.commons import FakeDevice

_PATH = os.path.abspath(os.path.curdir)
_STEP_FUNC = "tadek.teststeps.tests.stepFunc"

def assertOutput(test, expected, string):
    output = string.getvalue()
    if expected != output:
        test.failIf(True,
                    '\n'+''.join(difflib.unified_diff(expected.splitlines(1),
                                                      output.splitlines(1))))

def deviceDateTime(device, runTime=False):
    dt = device.date
    if runTime:
        dt += datetime.timedelta(seconds=device.time)
    return utils.timeToString(dt)

def deviceResult(name="Device", date=None, time=None, address=None,
                 port=None, status=testexec.STATUS_NOT_COMPLETED):
    device = testresult.DeviceExecResult(FakeDevice(name))
    device.description = "Description of device: %s" % name
    device.date = date if date else datetime.datetime.now()
    if time:
        device.time = time
    if address:
        device.address = address
    if port:
        device.port = port
    device.status = status
    device.cores = []
    return device

def stepResult(name="Step", parent=None):
    attrs = {
        "name": "Real name of test step: %s" % name,
        "description": "Description of test step: %s" % name,
    }
    args = {
        "arg1": "Text argument of %s" % name,
        "arg2": 124.875,
    }
    return testresult.TestStepResult(id=name, path=_PATH, func=_STEP_FUNC,
                                     parent=parent, attrs=attrs, args=args)

def caseResult(name="Case", parent=None):
    attrs = {
        "name": "Real name of test case: %s" % name,
        "description": "Description of test case: %s" % name,
    }
    return testresult.TestCaseResult(id=name, path=_PATH,
                                     parent=parent, attrs=attrs)

def suiteResult(name="Suite", parent=None):
    attrs = {
        "name": "Real name of test suite: %s" % name,
        "description": "Description of test suite: %s" % name,
    }
    return testresult.TestSuiteResult(id=name, path=_PATH,
                                      parent=parent, attrs=attrs)

def structResult(nsuites=0, ncases=0, nsteps=0):
    suites = [suiteResult("Suite%d" % (i + 1)) for i in xrange(nsuites)]
    if nsuites:
        cases = [caseResult("Case%d" % (i + 1), suite) for i in xrange(ncases)
                                                        for suite in suites]
    else:
        cases = [caseResult("Case%d" % (i + 1)) for i in xrange(ncases)]
    steps = [stepResult("Step%d" % (i + 1), case) for i in xrange(nsteps)
                                                  for case in cases]
    return suites, cases, steps

