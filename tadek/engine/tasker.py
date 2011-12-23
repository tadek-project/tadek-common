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

import threading

from contexts import *
from testdefs import *
from testresult import *

__all__ = ["TestTasker", "CaseTask", "SuiteTask"]

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TestTasker:
    '''
    A class for managing tests to execute on many devices.
    '''
    _id = -1

    def __init__(self, *tests):
        self._tasks = []
        self._mutex = threading.RLock()
        # A list of top level suites
        self._suites = []
        # Fill a task queue with the tests
        # TODO: Put potential test require many devices first
        for task in self._add([(None, test) for test in tests], None):
            self.put(task)

    def _add(self, tests, parent):
        '''
        Adds the given tests to the tasker.
        '''
        tasks = []
        self._id += 1
        caseId = self._id
        for id, test in tests:
            result = test.result(parent and parent.result, id=id)
            if isinstance(test, TestSuite):
                self._id += 1
                task = SuiteTask(self._id, test, result, parent)
                if parent is None:
                    self._suites.append(task)
                tasks.append(self._add(iter(test), task))
            else:
                yield CaseTask(caseId, test, result, parent)
        while tasks:
            for task in tasks[:]:
                try:
                    yield task.next()
                except StopIteration:
                    tasks.remove(task)

    def _count(self, id=None):
        '''
        Counts tasks of the given id.
        '''
        return len(self._tasks) if id is None else self._tasks.count(id)

    def _put(self, task):
        '''
        Puts the given task to the queue.
        '''
        self._tasks.append(task)

    def _get(self, id=None, exclude=None):
        '''
        Gets a task of the given id.
        '''
        if not self._tasks or id is not None and id not in self._tasks:
            return None
        if exclude:
            for task in self._tasks[:]:
                if task not in exclude and (id is None or task == id):
                    self._tasks.remove(task)
                    return task
        else:
            return self._tasks.pop(0 if id is None else self._tasks.index(id))
        return None

    def count(self, id=None):
        '''
        Returns a number of tasks of the given id or total number of tasks
        in the queue if id is not specified.
        '''
        self._mutex.acquire()
        try:
            return self._count(id)
        finally:
            self._mutex.release()

    def put(self, task):
        '''
        Puts a task into the queue.
        '''
        if not isinstance(task, TestTask):
            raise TypeError("Invalid task type: %s" % type(task).__name__)
        self._mutex.acquire()
        try:
            self._put(task)
        finally:
            self._mutex.release()

    def get(self, id=None, exclude=None):
        '''
        Removes a task with the given id from the tasker and returns it
        provided that none of its ancestors is on exclude list. For id which
        is None it returns a first not excluded task in the tasker.
        '''
        self._mutex.acquire()
        try:
            return self._get(id, exclude)
        finally:
            self._mutex.release()

    def join(self, exclude):
        '''
        Returns True if join method for all groups without parents
        returns True.
        '''
        for suite in self._suites:
            if not suite.join(exclude):
                return False
        return True

    def results(self):
        '''
        An iterator that yields one root test suite result per iteration.
        '''
        for suite in self._suites:
            yield suite.result


# TEST TASKS:

class TestTask:
    '''
    A base class for test tasks.
    '''
    # A class of the task execution context
    contextClass = None

    def __init__(self, id, test, result, parent=None):
        self.id = id
        self.test = test
        self.result = result
        self.parent = parent
        if self.contextClass is None:
            raise NotImplementedError

    def __eq__(self, task):
        if hasattr(task, "id"):
            return self.id == task.id
        return self.id == task

    def __str__(self):
        return "<%s(%s)>" % (self.__class__.__name__, self.result.id)
    __repr__ = __str__

    def context(self, *args, **kwargs):
        '''
        Returns an execution context for the test task.
        '''
        return self.contextClass(self, *args, **kwargs)

    def done(self):
        '''
        Notifies the test task parent that the task is done.
        '''
        if self.parent:
            self.parent.done()

    def undone(self):
        '''
        Notifies the test task parent that the task is undone.
        '''
        if self.parent:
            self.parent.undone()


class CaseTask(TestTask):
    '''
    A class for managing a test case execution on a device.
    '''
    contextClass = CaseContext

    def __init__(self, *args, **kwargs):
        TestTask.__init__(self, *args, **kwargs)
        for i, step in enumerate(self.test):
            step.result(self.result, i+1)

    def __eq__(self, task):
        '''
        Compares two test case tasks. It returns True if self or one of its
        ancestors and the task have the same id.
        '''
        this = self
        id = task.id if hasattr(task, "id") else task
        while this:
            if this.id == id:
                return True
            this = this.parent
        return False


class SuiteTask(TestTask):
    '''
    A class for managing a test suite execution on many devices.
    '''
    contextClass = SuiteContext

    def __init__(self, *args, **kwargs):
        TestTask.__init__(self, *args, **kwargs)
        self._mutex = threading.RLock()
        self._done = threading.Condition(self._mutex)
        self._todo = self.test.count()
        self.caseSetUps = [self.test.setUpCase]
        self.caseTearDowns = [self.test.tearDownCase]
        if self.parent:
            self.caseSetUps = self.parent.caseSetUps + self.caseSetUps
            self.caseTearDowns += self.parent.caseTearDowns

    def done(self):
        '''
        Decreases the number of test cases to do in this test suite task
        and notifies all waiting devices (threads).
        '''
        TestTask.done(self)
        self._done.acquire()
        try:
            if self._todo:
                self._todo -= 1
            self._done.notifyAll()
        finally:
            self._done.release()

    def undone(self):
        '''
        Notifies all waiting devices (threads).
        '''
        TestTask.undone(self)
        self._done.acquire()
        try:
            self._done.notifyAll()
        finally:
            self._done.release()

    def todo(self):
        '''
        Returns a number of test cases in the task group.
        Subgroups and test cases inside them are not counted.
        '''
        self._mutex.acquire()
        try:
            return self._todo
        finally:
            self._mutex.release()

    def join(self, exclude=0):
        '''
        Returns True if the task is on the exclude list or there are
        no tests (children of the task, not all descendants) to run
        else it recursively invokes itself for children.
        '''
        self._done.acquire()
        try:
            if (self._todo - exclude) > 0:
                self._done.wait()
            return (self._todo - exclude) == 0
        finally:
            self._done.release()

