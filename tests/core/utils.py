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

import datetime

from tadek.core.utils import timeToString, timeFromString, runTimeToString, \
                          _DATE_FORMAT, _TIME_FORMAT, _TIME_DATE_SEPARATOR

__all__ = ["TimeFunctTest"]


class TimeFunctTest(unittest.TestCase):
    def testtimeToString(self):
        datetime0 = datetime.datetime.now()
        self.assertEqual(datetime0.strftime(_TIME_DATE_SEPARATOR.join(
                    (_DATE_FORMAT, _TIME_FORMAT))), timeToString(datetime0))

    def testtimeToStringNoDate(self):
        time0 = datetime.datetime.now().time()
        self.assertEqual(time0.strftime(_TIME_DATE_SEPARATOR.join(
                        (_DATE_FORMAT, _TIME_FORMAT))), timeToString(time0))

    def testtimeToStringNoTime(self):
        date0 = datetime.datetime.now().date()
        self.assertEqual(date0.strftime(_TIME_DATE_SEPARATOR.join(
                        (_DATE_FORMAT, _TIME_FORMAT))), timeToString(date0))

    def testtimeToStringWithNone(self):
        self.assertEqual("", timeToString(None))

    def testtimeFromString(self):
        dateTimeStr = "2010-12-11 16:45:08"
        self.assertEqual(datetime.datetime.strptime(dateTimeStr,
                    _TIME_DATE_SEPARATOR.join((_DATE_FORMAT, _TIME_FORMAT))),
                                                timeFromString(dateTimeStr))

    def testtimeFromStringWithNone(self):
        self.assertEqual(None, timeFromString(""))

    def testSanity(self):
        dateTimeStr = "2010-12-11 16:45:08"
        self.assertEqual(dateTimeStr, timeToString(timeFromString(dateTimeStr)))

    def testRunTimeToString(self):
        seconds = 8642.10982
        self.assertEqual("2h 24m 2s", runTimeToString(seconds))

    def testRunTimeToStringNoHours(self):
        seconds = 1444.12982
        self.assertEqual("24m 4s", runTimeToString(seconds))

    def testRunTimeToStringSecondsOnly(self):
        seconds = 46.99982
        self.assertEqual("46s", runTimeToString(seconds))

    def testRunTimeToStringMoreThan24h(self):
        seconds = 398770.112366
        self.assertEqual("110h 46m 10s", runTimeToString(seconds))



if __name__ == "__main__":
    unittest.main()

