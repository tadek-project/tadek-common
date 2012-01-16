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
                          DATE_FORMAT, TIME_FORMAT, DATE_TIME_SEPARATOR

__all__ = ["TimeFunctTest"]


class TimeFunctTest(unittest.TestCase):
    def testtimeToString(self):
        datetime0 = datetime.datetime.now()
        self.assertEqual(datetime0.strftime(DATE_TIME_SEPARATOR.join(
                    (DATE_FORMAT, TIME_FORMAT))), timeToString(datetime0))

    def testtimeToStringNoDate(self):
        time0 = datetime.datetime.now().time()
        self.assertEqual(time0.strftime(DATE_TIME_SEPARATOR.join(
                        (DATE_FORMAT, TIME_FORMAT))), timeToString(time0))

    def testtimeToStringNoTime(self):
        date0 = datetime.datetime.now().date()
        self.assertEqual(date0.strftime(DATE_TIME_SEPARATOR.join(
                        (DATE_FORMAT, TIME_FORMAT))), timeToString(date0))

    def testtimeToStringWithNone(self):
        self.assertEqual("", timeToString(None))

    def testtimeFromString(self):
        dateTimeStr = "2011-12-21 16:45:08"
        self.assertEqual(datetime.datetime.strptime(dateTimeStr,
                    DATE_TIME_SEPARATOR.join((DATE_FORMAT, TIME_FORMAT))),
                                             timeFromString(dateTimeStr))

    def testtimeFromStringWithNone(self):
        self.assertEqual(None, timeFromString(""))

    def testSanity(self):
        dateTimeStr = "2011-12-21 16:45:08"
        self.assertEqual(dateTimeStr, timeToString(timeFromString(dateTimeStr)))

    def testRunTimeToString(self):
        seconds = 8642.10982
        self.assertEqual("2h 24m 2.11s", runTimeToString(seconds))

    def testRunTimeToStringNoHours(self):
        seconds = 1444.37982
        self.assertEqual("24m 4.38s", runTimeToString(seconds))

    def testRunTimeToStringSecondsOnly(self):
        seconds = 46.99982
        self.assertEqual("47.00s", runTimeToString(seconds))

    def testRunTimeToStringMoreThan24h(self):
        seconds = 398770.412366
        self.assertEqual("110h 46m 10.41s", runTimeToString(seconds))

if __name__ == "__main__":
    unittest.main()

