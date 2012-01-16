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
import traceback

from tadek import engine
from tadek.core.utils import encode

__all__ = ["TestExec", "TestAssertError",
           "STATUS_NO_RUN", "STATUS_NOT_COMPLETED",
           "STATUS_PASSED", "STATUS_FAILED", "STATUS_ERROR"]

# Test execution statuses:
STATUS_NO_RUN = "No Run"
STATUS_NOT_COMPLETED  = "Not Completed"
STATUS_PASSED = "Passed"
STATUS_FAILED = "Failed"
STATUS_ERROR = "Error"

# Test execution debug mode
_DEBUG = False

_SYSTEM_DIR = os.path.abspath(os.path.dirname(traceback.__file__))
_ENGINE_DIR = os.path.abspath(os.path.dirname(engine.__file__))

def _stack(entries, strings):
    '''
    Returns a list of strings representing the given stack frame containing
    only relevant entries.
    '''
    if _DEBUG:
        return strings
    start = 0
    for entry in entries:
        dirname = os.path.abspath(os.path.dirname(entry[0]))
        if (not dirname.startswith(_SYSTEM_DIR) and
            not dirname.startswith(_ENGINE_DIR)):
            break
        start += 1
    end = start
    for entry in entries[start:]:
        dirname = os.path.abspath(os.path.dirname(entry[0]))
        if dirname.startswith(_ENGINE_DIR):
            break
        end += 1
    return strings[start:end]

def errorInfo(error):
    '''
    Returns information about the given error.
    '''
    if hasattr(error, "stack"):
        stack = error.stack
    else:
        tb = sys.exc_info()[2]
        stack = _stack(traceback.extract_tb(tb), traceback.format_tb(tb))
    exception = traceback.format_exception_only(type(error), error)
    return ''.join(stack + exception).strip()


# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TestAssertError(Exception):
    '''
    A base exception class for test assertions.
    '''
    #: A status of a test result
    status = None

    def __init__(self, msg, stack=None):
        Exception.__init__(self, msg)
        self.stack = stack or _stack(traceback.extract_stack(),
                                     traceback.format_stack())

class TestNotCompletedError(TestAssertError):
    '''
    A class of exceptions raised when a test cannot be completed.
    '''
    status = STATUS_NOT_COMPLETED

class TestAbortError(TestAssertError):
    '''
    A class of exceptions raised to abort a test execution.
    '''
    status = STATUS_NOT_COMPLETED

class TestFailError(TestAssertError):
    '''
    A class of exceptions raised to fail a test.
    '''
    status = STATUS_FAILED

class TestFailThisError(TestAssertError):
    '''
    A class of exceptions raised to fail only this test.
    '''
    status = STATUS_FAILED


class TestExec:
    '''
    A class for controlling test executions.
    '''
    def __init__(self, context=None):
        self._context = context or {}

    def __contains__(self, name):
        '''
        Returns True if an item of the given name exists, False otherwise.
        '''
        return name in self._context

    def __getitem__(self, name):
        '''
        Gets an item value of the given name.
        '''
        return self._context.get(name)

    def __setitem__(self, name, value):
        '''
        Sets an item of the given name to the specified value.
        '''
        self._context[name] = value

    def _assert(self, expr, msg, etype):
        '''
        Asserts the expression using the given exception type and message.
        '''
        if not expr:
            raise etype(encode(msg))

    def abort(self, expr, msg):
        '''
        Aborts the test with the given message unless the expression is true.
        It aborts an execution of this test and all its ancestors.
        '''
        self._assert(expr, msg, TestAbortError)

    def abortIf(self, expr, msg):
        '''
        Aborts the test with the given message if the expression is true.
        It aborts an execution of this test and all its ancestors.
        '''
        self._assert(not expr, msg, TestAbortError)

    def fail(self, expr, msg):
        '''
        Fails the test with the given message unless the expression is true.
        It fails an execution of this test and its direct parent.
        '''
        self._assert(expr, msg, TestFailError)

    def failIf(self, expr, msg):
        '''
        Fails the test with the given message if the expression is true.
        It fails an execution of this test and its direct parent.
        '''
        self._assert(not expr, msg, TestFailError)

    def failThis(self, expr, msg):
        '''
        Fails the test with the given message unless the expression is true.
        It fails only an execution of this test, it does not affect its parent.
        '''
        self._assert(expr, msg, TestFailThisError)

    def failThisIf(self, expr, msg):
        '''
        Fails the test with the given message if the expression is true.
        It fails only an execution of this test, it does not affect its parent.
        '''
        self._assert(not expr, msg, TestFailThisError)

    def child(self):
        '''
        Returns a child instance basing on the test execution.
        '''
        return self.__class__(self._context.copy())

