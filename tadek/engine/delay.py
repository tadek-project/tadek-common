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

import time

class Delay(object):
    '''
    A class of delays executing given functions until they return positive
    results with a defined interval between successive executions.
    '''
    def __init__(self, attempts, interval):
        '''
        Stores maximum number of attempts of a function execution before returns
        a result and the interval between successive executions.

        :param attempts: The maximum number of attempts
        :type attempts: integer
        :param interval: The interval between successive executions of functions
        :type interval: float
        '''
        self._attempts = attempts
        self._interval = interval

    def __call__(self, func, expectedFailure=False):
        '''
        Executes the given function until it returns a positive result.
        If expectedFailure is True then the function is executed till it returns
        a negative result.
        Maximum number of execution attempts and the interval between successive
        executions are defined in the Delay instance.

        :param func: A function to execute
        :type func: function
        :param expectedFailure: True if a negative result of the function is
            expected, False otherwise
        :type expectedFailure: boolean
        :return: A result of an execution of a given function
        :rtype: Not specified
        '''
        result = None
        attempt = 1
        while attempt <= self._attempts:
            result = func()
            if ((result and not expectedFailure) or
                (not result and expectedFailure)):
                break
            time.sleep(self._interval)
            attempt += 1
        return result

    def __mul__(self, n):
        '''
        Returns a new Delay instance with a multiplied number of attempts by
        the given number.

        :param n: A multiplier of the number of attempts
        :type n: integer
        :return: A multiplied Delay instance
        :rtype: Delay
        '''
        return Delay(n*self._attempts, self._interval)

    def __rmul__(self, n):
        '''
        Returns a new Delay instance with a multiplied number of attempts by
        the given number.

        :param n: A multiplier of the number of attempts
        :type n: integer
        :return: A multiplied Delay instance
        :rtype: Delay
        '''
        return self*n

    def wait(self):
        '''
        Waits for number of attempts * interval seconds idly.
        '''
        time.sleep(self._attempts * self._interval)


#: A default delay for actions
action = Delay(1, 0.5)
#: A default delay for standard operations
default = Delay(10, 0.4)
#: A default delay for immediate operations
immediate = Delay(1, 0.1)
#: A default delay for initial issues
initial = Delay(2, 0.5)
#: A default delay for slow operations
slow = Delay(10, 1)
#: A default delay for checking states
state = Delay(5, 0.4)
#: A default delay for checking text
text = Delay(5, 0.5)

