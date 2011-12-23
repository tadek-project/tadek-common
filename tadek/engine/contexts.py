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

import testexec

__all__ = ["CaseContext", "SuiteContext", "DeviceContext"]

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class TaskContext:
    '''
    A base class of task contexts.
    '''
    child = None

    def __init__(self, task):
        self.task = task

    def _runTask(self, test, device, result):
        '''
        Runs the related test task within the context.
        '''
        pass

    def run(self, test, device, result):
        '''
        Runs the task context.
        '''
        result.startTest(self.task.result, device)
        execResult = self.task.result.device(device)
        try:
            try:
                self._runTask(test, device, result)
            except testexec.TestAbortError, err:
                execResult.errors.append(testexec.errorInfo(err))
                execResult.status = err.status
                raise
            except testexec.TestAssertError, err:
                execResult.errors.append(testexec.errorInfo(err))
                execResult.status = err.status
            except KeyboardInterrupt, err:
                execResult.errors.append(testexec.errorInfo(err))
                execResult.status = testexec.STATUS_NOT_COMPLETED
                raise testexec.TestAbortError("Keyboard interrupt")
            except Exception, err:
                execResult.errors.append(testexec.errorInfo(err))
                execResult.status = testexec.STATUS_ERROR
                # FIXME
                # Shouldn't some exception be passed higher?
            else:
                execResult.status = testexec.STATUS_PASSED
        finally:
            result.stopTest(self.task.result, device)


class CaseContext(TaskContext):
    '''
    A class of test case contexts.
    '''
    def _runTask(self, test, device, result):
        '''
        Runs a related test case task within the context.
        '''
        idx = 0
        try:
            if self.task.parent:
                idx = len(self.task.parent.caseSetUps)
                for setUp in self.task.parent.caseSetUps:
                    setUp(test, device)
                    idx -= 1
            for step, stepResult in zip(self.task.test,
                                        self.task.result.children):
                result.startTest(stepResult, device)
                execResult = stepResult.device(device)
                try:
                    try:
                        step.run(test, device)
                    except testexec.TestFailThisError, err:
                        execResult.errors.append(testexec.errorInfo(err))
                        execResult.status = err.status
                    except KeyboardInterrupt, err:
                        execResult.errors.append(testexec.errorInfo(err))
                        execResult.status = testexec.STATUS_NOT_COMPLETED
                        raise testexec.TestAbortError("Keyboard interrupt")
                    except Exception, err:
                        execResult.errors.append(testexec.errorInfo(err))
                        execResult.status = getattr(err, "status",
                                                    testexec.STATUS_ERROR)
                        raise
                    else:
                        execResult.status = testexec.STATUS_PASSED
                finally:
                    result.stopTest(stepResult, device)
        finally:
            if self.task.parent:
                error = None
                for tearDown in self.task.parent.caseTearDowns[idx:]:
                    try:
                        tearDown(test, device)
                    except Exception, err:
                        # FIXME
                        # An exception raised by previous tearDownCase() should
                        # be also saved here.
                        error = err
                if error:
                    raise error

    def run(self, *args, **kwargs):
        '''
        Runs the test case context.
        '''
        self.task.done()
        TaskContext.run(self, *args, **kwargs)


class GroupContext:
    '''
    An interface class for contexts of task groups.
    '''
    parent = None
    tasker = None

    def __init__(self, parent=None):
        if parent:
            self.parent = parent
            self.tasker = parent.tasker
        self._forbidden = []

    def forbid(self, id):
        '''
        Forbids an execution of tasks of the given id in the group context.
        '''
        self._forbidden.append(id)
        if self.parent:
            self.parent.forbid(id)

    def taskContext(self, task, parent=None):
        '''
        Return an execution context for the given task.
        '''
        tasks = [task]
        while task.parent and task.parent != parent:
            task = task.parent
            tasks.insert(0, task)
        parent = None
        contexts = []
        while tasks:
            task = tasks.pop(0)
            context = task.context(parent or self) if tasks else task.context()
            contexts.append(context)
            if parent:
                parent.child = context
            parent = context
        return contexts[0]


class SuiteContext(TaskContext, GroupContext):
    '''
    A class of test suite contexts.
    '''
    def __init__(self, task, parent):
        TaskContext.__init__(self, task)
        GroupContext.__init__(self, parent)

    def _runTask(self, test, device, result):
        '''
        Runs the related test suite task within the context.
        '''
        # Set up the test suite
        try:
            self.task.test.setUpSuite(test, device)
        except:
            self.parent.forbid(self.task.id)
            # Put the target test case task back to the tasker
            context = self
            while context.child:
                context = context.child
            self.tasker.put(context.task)
            self.task.undone()
            raise
            # Run all test cases from the test suite
        try:
            child, self.child = self.child, None
            while child:
                child.run(test.child(), device, result)
                # Yes, now it is possible that a case defined directly in
                # the suite could be omitted here and executed after cases from
                # child suites. But I believe it is nothing bad, because
                # if thers are two device threads in the same suite it is not
                # important which one executes the suite child test cases.
                task = (self.tasker.get(child.task.id, self._forbidden) or
                        self.tasker.get(self.task.id, self._forbidden))
                while task is None:
                    n = 0
                    for id in self._forbidden:
                        n += self.tasker.count(id)
                    if self.task.join(n):
                        break
                    task = self.tasker.get(self.task.id, self._forbidden)
                child = self.taskContext(task, self.task) if task else None
        finally:
            # FIXME
            # Shouldn't the tearDownSuite() be always executed regardless
            # the setUpSuite() failed or not? Some activities from
            # the setUpSuite() could be done before it failed, which should be
            # cleaned up.
            #
            # Tear down the test suite
            self.task.test.tearDownSuite(test, device)


class DeviceContext(GroupContext):
    '''
    A class of device execution contexts.
    '''
    def __init__(self, device, tasker):
        GroupContext.__init__(self)
        self.device = device
        self.tasker = tasker

    def run(self, test, result):
        '''
        Runs the context for the given.
        '''
        try:
            while True:
                task = self.tasker.get(exclude=self._forbidden)
                if task is None:
                    n = 0
                    for id in self._forbidden:
                        n += self.tasker.count(id)
                    if self.tasker.join(n):
                        break
                else:
                    context = self.taskContext(task)
                    context.run(test.child(), self.device, result)
        except testexec.TestAbortError:
            pass

