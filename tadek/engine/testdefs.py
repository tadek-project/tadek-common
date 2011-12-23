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

__all__ = ["testStep", "testCase", "TestCase", "TestSuite"]

import os
import sys

from tadek import testsuites
from tadek.core.locale import escape

from testresult import *

# A common id prefix of all test definitions
_ID_PREFIX = testsuites.__name__ + '.'

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TestBase:
    '''
    A base class of test definitions.
    '''
    #: A class of test execution results
    resultClass = None

    def __init__(self, **attrs):
        self.attrs = attrs

    def count(self):
        '''
        Counts how many devices are required to execute the test.
        '''
        return 0

    def result(self, parent=None, **kwargs):
        '''
        Returns a test execution result for the test.
        '''
        if self.resultClass is None:
            raise NotImplementedError
        return self.resultClass(attrs=self.attrs.copy(),
                                parent=parent, **kwargs)


# TEST STEP DEFINITIONS:

_STEP_REQ_ARGS = (
    "test",
    "device"
)

def testStep(**attrs):
    '''
    A decorator that makes a function a test step.
    '''
    # TODO: Check if all required attributes are provided
    def testStepPrototype(func):
        # Validate arguments of the test step function
        nargs = func.func_code.co_argcount
        if func.func_defaults:
            nargs -= len(func.func_defaults)
        args = func.func_code.co_varnames[:func.func_code.co_argcount][:nargs]
        if args != _STEP_REQ_ARGS:
            raise ValueError("Test step function must take following positional"
                             " arguments: %s" % ", ".join(_STEP_REQ_ARGS))
        return TestStepPrototype(func, **attrs)
    return testStepPrototype


class TestStepPrototype:
    '''
    Defines a test step prototype.
    '''
    def __init__(self, func, **attrs):
        self.func = func
        self.attrs = attrs

    def __call__(self, **kwargs):
        '''
        Creates a test step based on the test step prototype and the given
        keyword arguments.
        '''
        return TestStep(self.func, self.attrs.copy(), kwargs)

    def run(self, test, device, **args):
        '''
        Runs the corresponding test step function with the given arguments.
        '''
        for name, value in args.iteritems():
            args[name] = escape(value, device)
        return self.func(test, device, **args)


class TestStep(TestBase):
    '''
    Defines a test step in a test case.
    '''
    resultClass = TestStepResult

    _ID_PATTERN = "step%d"

    def __init__(self, func, attrs, args):
        # Add not provided arguments with their default values
        if func.func_defaults:
            kwargs = func.func_code.co_varnames[:func.func_code.co_argcount]
            kwargs = kwargs[-len(func.func_defaults):]
            for i, arg in enumerate(kwargs):
                if arg not in args:
                    args[arg] = func.func_defaults[i]
        # Update the test step attributes
        for name, value in attrs.iteritems():
            if isinstance(value, basestring):
                try:
                    attrs[name] %= args
                except (KeyError, ValueError):
                    pass
        TestBase.__init__(self, **attrs)
        self.func = func
        self.args = args

    def count(self):
        '''
        Counts how many devices is required to execute the test step.
        '''
        return 1

    def result(self, parent=None, id=None, **kwargs):
        '''
        Returns a test execution result for the test step.
        '''
        if id is not None:
            id = self._ID_PATTERN % id
        func = '.'.join([self.func.func_globals["__name__"],
                         self.func.func_name])
        return TestBase.result(self, func=func, args=self.args.copy(),
                                     id=id, parent=parent, **kwargs)

    def run(self, test, device):
        '''
        Runs the corresponding test step function with provided arguments.
        '''
        args = {}
        for name, value in self.args.iteritems():
            args[name] = escape(value, device)
        test["result"] = self.func(test, device, **args)


# TEST CASE DEFINITIONS:

def testCase(**attrs):
    '''
    A decorator that makes a function a test case.
    '''
    # TODO: Check if all required attributes are provided
    def testStep(func):
        return TestCase(TestStep(func, {}, {}), **attrs)
    return testStep


class TestCase(TestBase):
    '''
    Defines a single test case.
    '''
    resultClass = TestCaseResult

    def __init__(self, *steps, **attrs):
        TestBase.__init__(self, **attrs)
        self._steps = []
        for step in steps:
            if isinstance(step, TestStep):
                self._steps.append(step)
            elif isinstance(step, TestCase):
                self._steps.extend(step)
            else:
                raise ValueError("Test step must be of type TestStep"
                                 " or TestCase")
        self._steps = tuple(self._steps)

    def __iter__(self):
        '''
        An iterator that yields one test step per iteration.
        '''
        return iter(self._steps)

    def __call__(self, **kwargs):
        '''
        Returns itself to make it compatible with test step.
        '''
        return self

    def count(self):
        '''
        Counts how many devices is required to execute the test case.
        '''
        return 1

    def run(self, test, device):
        '''
        Runs all steps of the test case.
        '''
        for step in self:
            step.run(test, device)


# TEST SUITE DEFINITIONS:

if sys.version_info >= (2, 6):
    def testSuite(**attrs):
        '''
        A decorator that makes a class a test suite.
        '''
        # TODO: Check if all required attributes are provided
        def addAttrs(cls):
            if issubclass(cls, TestSuite):
                for name, value in attrs.iteritems():
                    setattr(cls, name, value)
            return cls
        return addAttrs
    __all__.append("testSuite")


class TestSuite(TestBase):
    '''
    Defines a test suite with test cases and other test suites.
    '''
    resultClass = TestSuiteResult

    def __init__(self, *cases):
        suite = {}
        attrs = {}
        for name, attr in vars(self.__class__).iteritems():
            if name.startswith('_'):
                continue
            if isinstance(attr, basestring):
                attrs[name] = attr
            elif isinstance(attr, (TestCase, TestSuite)):
                suite[name] = attr
        TestBase.__init__(self, **attrs)
        if cases:
            caseMap = {}
            for case in cases:
                case = case.strip().strip('.')
                if not case:
                    continue
                names = case.split('.', 1)
                if names[0] not in suite:
                    raise AttributeError("Suite '%s' has no case '%s'"
                                          % (self.__class__.__name__, names[0]))
                case = suite[names[0]]
                if names[1:]:
                    if not isinstance(case, TestSuite):
                        raise AttributeError("Suite '%s' has no suite '%s'"
                                          % (self.__class__.__name__, names[0]))
                if names[0] in caseMap:
                    caseMap[names[0]][1].extend(names[1:])
                else:
                    caseMap[names[0]] = (case, names[1:])
            suite = {}
            for name, pair in caseMap.iteritems():
                case, names = pair
                suite[name] = case(*names) if names else case
        self._cases = suite

    def __iter__(self):
        '''
        An iterator that yields one test case name per iteration.
        '''
        for id, case in sorted(self._cases.iteritems()):
            yield id, case

    def __call__(self, *cases):
        '''
        Returns a new instance of the test suite containing specified cases.
        '''
        return self.__class__(*cases)

    def count(self):
        '''
        Counts how many devices are required to execute the test suite.
        '''
        n = 0
        for id, case in self:
            n += case.count()
        return n

    def result(self, parent=None, id=None, path=None, **kwargs):
        '''
        Returns a test execution result for the test suite.
        '''
        if id is None:
            module = self.__class__.__module__
            if module.startswith(_ID_PREFIX):
                module = module[len(_ID_PREFIX):]
            id = "%s.%s" % (module, self.__class__.__name__)
            module = sys.modules.get(self.__class__.__module__)
            if module:
                path = os.path.dirname(module.__file__)
        return TestBase.result(self, id=id, path=path, parent=parent, **kwargs)

    def setUpSuite(self, test, device):
        '''
        Sets up the test suite fixture on the given device.
        '''
        pass

    def setUpCase(self, test, device):
        '''
        Sets up a fixture of each test case from the test suite.
        '''
        pass

    def tearDownCase(self, test, device):
        '''
        Tears down a fixture of each test case from the test suite.
        '''
        pass

    def tearDownSuite(self, test, device):
        '''
        Tears down the test suite fixture on the given device.
        '''
        pass

