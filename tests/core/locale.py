# -*- coding: utf-8 -*-

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
import unittest

from tadek.core import locale

__all__ = ["LocaleTest"]

_MSG1_ID = "hello"
_TRANS1 = u"witaj"
_MSG2_ID = "stranger"
_TRANS2 = u"nieznajomy"
_SING_ID = u"there is only one way"
_SING_TRANS = u"jest tylko jeden sposób"
_PLUR_ID = u"there are many ways"
_PLUR_TRANS = u"jest wiele sposobów"

_LOCALES_DIR = os.path.join("tests", "locales")

class _Device:
    locale = "pl_PL"


class LocaleTest(unittest.TestCase):
    def _addLocaleDir(self, localedir):
        locale.add(os.path.abspath(os.path.join(_LOCALES_DIR, localedir)))

    def _removeLocaleDir(self, localedir):
        locale.remove(os.path.abspath(os.path.join(_LOCALES_DIR, localedir)))

    def tearDown(self):
        for localedir in ["locale1", "locale2", "locale3"]:
            self._removeLocaleDir(localedir)

    def testNoLocalePath(self):
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _MSG1_ID)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _MSG2_ID)

    def testGetTextMsg1(self):
        self._addLocaleDir("locale1")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _TRANS1)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _MSG2_ID)

    def testGetTextMsg2(self):
        self._addLocaleDir("locale2")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _MSG1_ID)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _TRANS2)

    def testGetTextMsg12(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _TRANS1)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _TRANS2)

    def testGetTextMsg2Lazy(self):
        self._addLocaleDir("locale2")
        device = _Device()
        msg = locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(msg(device), _TRANS2)

    def testGetTextMsg2LazyFail(self):
        self._addLocaleDir("locale1")
        device = _Device()
        msg = locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(msg(device), _MSG2_ID)

    def testGetTextMsg12Fail(self):
        self._addLocaleDir("locale3")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _MSG1_ID)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _MSG2_ID)

    def testGetTextMsg12Remove1(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _TRANS1)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _TRANS2)
        self._removeLocaleDir("locale1")
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _MSG1_ID)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _TRANS2)

    def testGetTextMsg1Reset(self):
        self._addLocaleDir("locale1")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _TRANS1)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _MSG2_ID)
        locale.reset()
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _TRANS1)
        self.failUnlessEqual(locale.gettext(_MSG2_ID, device), _MSG2_ID)

    def testGetTextTranslatedMsg1(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        self._addLocaleDir("locale3")
        device = _Device()
        self.failUnlessEqual(locale.gettext(_TRANS1, device), _TRANS1)

    def testNGetTextSingMsg(self):
        self._addLocaleDir("locale1")
        device = _Device()
        self.failUnlessEqual(locale.ngettext(_SING_ID, _PLUR_ID, 1, device), _SING_TRANS)

    def testNGetTextPlurMsg(self):
        self._addLocaleDir("locale1")
        device = _Device()
        self.failUnlessEqual(locale.ngettext(_SING_ID, _PLUR_ID, 5, device), _PLUR_TRANS)

    def testNGetTextPlurMsgLazy(self):
        self._addLocaleDir("locale1")
        device = _Device()
        msg = locale.ngettext__(_SING_ID, _PLUR_ID, 5)
        self.failUnless(isinstance(msg, locale.LazyNTranslation))
        self.failUnlessEqual(msg(device), _PLUR_TRANS)

    def testNGetTextSingMsgLazy(self):
        self._addLocaleDir("locale1")
        device = _Device()
        msg = locale.ngettext__(_SING_ID, _PLUR_ID, 1)
        self.failUnless(isinstance(msg, locale.LazyNTranslation))
        self.failUnlessEqual(msg(device), _SING_TRANS)

    def testNGetTextPlurMsgFail(self):
        self._addLocaleDir("locale3")
        device = _Device()
        self.failUnlessEqual(locale.ngettext(_SING_ID, _PLUR_ID, 5, device), _PLUR_ID)

    def testNGetTextSingMsgLazyFail(self):
        self._addLocaleDir("locale3")
        device = _Device()
        msg = locale.ngettext__(_SING_ID, _PLUR_ID, 1)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(msg(device), _SING_ID)

    def testGetTextMsg12LazySum(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        msg = locale.gettext__(_MSG1_ID) + locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), _TRANS1 + _TRANS2)

    def testGetTextMsg2LazyStrSum(self):
        self._addLocaleDir("locale2")
        device = _Device()
        string = "ch"
        msg = locale.gettext__(_MSG2_ID) + string
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), _TRANS2 + string)

    def testGetTextStrMsg1LazySum(self):
        self._addLocaleDir("locale1")
        device = _Device()
        string = "za"
        msg = string + locale.gettext__(_MSG1_ID)
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), string + _TRANS1)

    def testNGetTextStrPlurMsgLazySum(self):
        self._addLocaleDir("locale1")
        device = _Device()
        string = "Ale "
        msg = string + locale.ngettext__(_SING_ID, _PLUR_ID, 5)
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), string + _PLUR_TRANS)

    def testGetTextMsg12LazyStrsMixedSum(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        msg = "*" + locale.gettext__(_MSG1_ID) + " " + locale.gettext__(_MSG2_ID) + "!*"
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), "*" + _TRANS1 + " " + _TRANS2 + "!*")

    def testNGetTextMsg2SingLazyStrsMixedSum(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        msg = u"Więc " + locale.ngettext__(_SING_ID, _PLUR_ID, 1) + ", " + locale.gettext__(_MSG2_ID) + "!"
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), u"Więc " + _SING_TRANS + ", " + _TRANS2 + "!")

    def testGetTextMsg12LazySumFail(self):
        self._addLocaleDir("locale1")
        device = _Device()
        msg = locale.gettext__(_MSG1_ID) + locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), _TRANS1 + _MSG2_ID)

    def testGetTextMsg1LazyStrSumFail(self):
        self._addLocaleDir("locale2")
        device = _Device()
        string = "..."
        msg = locale.gettext__(_MSG1_ID) + string
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(msg(device), _MSG1_ID + string)

    def testGetTextMsg1EmptyLocale(self):
        self._addLocaleDir("locale1")
        device = _Device()
        device.locale = ''
        self.failUnlessEqual(locale.gettext(_MSG1_ID, device), _MSG1_ID)

    def testGetTextMsg1LazyEmptyLocale(self):
        self._addLocaleDir("locale1")
        device = _Device()
        device.locale = ''
        msg = locale.gettext__(_MSG1_ID)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(msg(device), _MSG1_ID)

    def testNGetTextPlurMsgEmptyLocale(self):
        self._addLocaleDir("locale1")
        device = _Device()
        device.locale = ''
        self.failUnlessEqual(locale.ngettext(_SING_ID, _PLUR_ID, 5, device), _PLUR_ID)

    def testNGetTextSingMsgLazyFail(self):
        self._addLocaleDir("locale1")
        device = _Device()
        device.locale = ''
        msg = locale.ngettext__(_SING_ID, _PLUR_ID, 1)
        self.failUnless(isinstance(msg, locale.LazyNTranslation))
        self.failUnlessEqual(msg(device), _SING_ID)

    def testGetTextMsg2LazyGetText(self):
        self._addLocaleDir("locale2")
        device = _Device()
        msg = locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(locale.gettext(msg, device), _TRANS2)

    def testMsg1LazyEscape(self):
        self._addLocaleDir("locale1")
        device = _Device()
        msg = locale.gettext__(_MSG1_ID)
        self.failUnless(isinstance(msg, locale.LazyTranslation))
        self.failUnlessEqual(locale.escape(msg, device), _TRANS1)

    def testStrEscape(self):
        device = _Device()
        self.failUnlessEqual(locale.escape(_MSG2_ID, device), _MSG2_ID)

    def testStrOfGetTextMsg12LazyStrMixedSum(self):
        self._addLocaleDir("locale1")
        self._addLocaleDir("locale2")
        device = _Device()
        msg = locale.gettext__(_MSG1_ID) + " " + locale.gettext__(_MSG2_ID)
        self.failUnless(isinstance(msg, locale.MessageSum))
        self.failUnlessEqual(str(msg),  _MSG1_ID + " " + _MSG2_ID)

