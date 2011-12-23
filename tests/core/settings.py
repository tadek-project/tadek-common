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

from tadek.core import config, settings
import pdb

__all__ = ["SettingsTest", "SettingsOptionTest", "SettingsSectionTest"]

_PROGRAM_NAME = 'unittest'

class SettingsTest(unittest.TestCase):
    _filenames = ('__testCaseSettings0__', '__testCaseSettings1__')
    _populated = False

    def setUp(self):
        files = []
        for file in self._filenames:
            files.append(os.path.join(config._USER_CONF_DIR, _PROGRAM_NAME,
                                      ''.join((file, config._CONF_FILE_EXT))))
        self._files = tuple(files)
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass
        config.reload()

    def tearDown(self):
        for file_ in self._files:
            try:
                os.remove(file_)
            except OSError:
                pass

    def testValueGet(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        config.set(TEST_FILE_NAME, "Test", "test_2", "11")
        self.assertTrue(TEST_FILE_NAME in settings.get())
        self.assertTrue("Test" in settings.get(TEST_FILE_NAME))
        self.assertEqual(["test_1", "test_2"],
                           sorted([s.name() for s in settings.get(
                                                    TEST_FILE_NAME, "Test")]))
        self.assertEqual("11", settings.get(TEST_FILE_NAME,
                                                      "Test", "test_2").get())

    def testValueGetNotSettingsName(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME)
        self.assertFalse(TEST_FILE_NAME in settings.get())
        self.assertTrue(TEST_FILE_NAME in settings.get(force=True))

    def testValueGetNotSettingsSections(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        config.set(TEST_FILE_NAME, "Test", "test_1", "11")
        self.assertFalse("Test" in settings.get(TEST_FILE_NAME))
        self.assertTrue("Test" in settings.get(TEST_FILE_NAME, force=True))

    def testValueGetNotSettings(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        config.set(TEST_FILE_NAME, "Test", "test_2", "11")
        self.assertEqual(None, settings.get(TEST_FILE_NAME,
                                                         "Test", "test_1"))
        self.assertEqual("1", settings.get(TEST_FILE_NAME,
                                         "Test", "test_1", force=True).get())
        self.assertTrue(settings._META_OPTION_NAME in config.get(
                                                    TEST_FILE_NAME, "Test"))
        self.assertEqual(config.get(
                        TEST_FILE_NAME, "Test", settings._META_OPTION_NAME),
                                                settings._META_OPTION_VALUE)

    def testSet(self):
        TEST_FILE_NAME = self._filenames[0]
        settings.set(TEST_FILE_NAME, "Test0")
        settings.set(TEST_FILE_NAME, "Test1", "test1_1", "1")
        self.assertTrue("Test0" in config.get(TEST_FILE_NAME))
        self.assertTrue("Test1" in config.get(TEST_FILE_NAME))
        self.assertTrue("test1_1" in config.get(TEST_FILE_NAME, "Test1"))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test1", "test1_1"))

    def testRemove(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test0", "test0_1", "10")
        config.set(TEST_FILE_NAME, "Test0", "test0_2", "110")
        config.set(TEST_FILE_NAME, "Test1", "test1_1", "1")
        config.set(TEST_FILE_NAME, "Test1", "test1_2", "11")
        config.set(TEST_FILE_NAME, "Test1", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        settings.remove(TEST_FILE_NAME, "Test0", "test0_2")
        settings.remove(TEST_FILE_NAME, "Test1", "test1_2")
        self.assertFalse("test0_2" in config.get(TEST_FILE_NAME, "Test0"))
        self.assertFalse("test1_2" in config.get(TEST_FILE_NAME, "Test1"))
        settings.remove(TEST_FILE_NAME, "Test0")
        settings.remove(TEST_FILE_NAME, "Test1")
        self.assertFalse("Test0" in config.get(TEST_FILE_NAME))
        self.assertFalse("Test1" in config.get(TEST_FILE_NAME))
        settings.remove(TEST_FILE_NAME)


class SettingsOptionTest(unittest.TestCase):
    _filenames = ('__testCaseSettings0__', '__testCaseSettings1__')
    _populated = False

    def setUp(self):
        files = []
        for file in self._filenames:
            files.append(os.path.join(config._USER_CONF_DIR, _PROGRAM_NAME,
                                      ''.join((file, config._CONF_FILE_EXT))))
        self._files = tuple(files)
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass
        config.reload()

    def tearDown(self):
        for file_ in self._files:
            try:
                os.remove(file_)
            except OSError:
                pass

    def testValueAddToNewFile(self):
        TEST_FILE_NAME = self._filenames[0]
        self.assertFalse("Test" in config.get(TEST_FILE_NAME))
        item = settings.get(TEST_FILE_NAME, "Test", "test_1", force=True)
        self.assertTrue("Test" in config.get(TEST_FILE_NAME))
        item.set("1")
        self.assertEqual(settings._META_OPTION_VALUE,
                config.get(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test", "test_1"))

    def testValueAddExistingSection(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test")
        settings.get(TEST_FILE_NAME, "Test", "test_1", force=True).set("1")
        self.assertEqual(settings._META_OPTION_VALUE,
                config.get(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test", "test_1"))

    def testAddSettingOption(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        self.assertFalse(settings._META_OPTION_NAME in config.get(
                                                       TEST_FILE_NAME, "Test"))
        settings.get(TEST_FILE_NAME, "Test", force=True)
        self.assertTrue(settings._META_OPTION_NAME in config.get(
                                                       TEST_FILE_NAME, "Test"))

    def testValueAddWrongSettOptVal(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME, "Test")
        self.assertNotEqual(settings._META_OPTION_VALUE,
            config.get(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        item = settings.get(TEST_FILE_NAME, "Test", "test_1", force=True)
        item.set("1")
        self.assertTrue(settings._META_OPTION_NAME in config.get(
                                                       TEST_FILE_NAME, "Test"))
        self.assertEqual(settings._META_OPTION_VALUE, config.get(
                           TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test", "test_1"))

    def testValueGet(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertEqual("1", item.get())
        self.assertEqual("1", str(item))
        self.assertEqual("", str(settings.get(TEST_FILE_NAME,
                                                        "Test", "test_2")))

    def testValueGetName(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertEqual("test_1", item.name())

    def testValueGetNotSettingsSection(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertEqual(None, item)

    def testValueGetSettingsOption(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        self.assertEqual(None, settings.get(TEST_FILE_NAME,
                                     "Test", settings._META_OPTION_NAME))

    def testGetBool(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "True")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertEqual(True, item.getBool())
        self.assertEqual(True, bool(item))
        config.set(TEST_FILE_NAME, "Test", "test_1", "False")
        self.assertEqual(False, item.getBool())
        self.assertEqual(False, bool(item))
        config.set(TEST_FILE_NAME, "Test", "test_1", "Name")
        self.assertEqual(None, item.getBool())
        self.assertEqual(False, bool(item))

    def testGetInt(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertEqual(1, item.getInt())
        self.assertEqual(1, int(item))
        config.set(TEST_FILE_NAME, "Test", "test_1", "True")
        self.assertTrue(item.getInt() is None)
        self.assertEqual(0, int(item))

    def testValueRemove(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item = settings.get(TEST_FILE_NAME, "Test", "test_1")
        self.assertTrue("test_1" in config.get(TEST_FILE_NAME, "Test"))
        item.remove()
        self.assertFalse("test_1" in config.get(TEST_FILE_NAME, "Test"))

    def testListValue(self):
        TEST_FILE_NAME = self._filenames[0]
        value = ["item1", "item2", "item3"]
        config.set(TEST_FILE_NAME, "Test", "test_1", value)
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        self.assertEqual(value, settings.get(self._filenames[0],
                                                  "Test", "test_1").getList())

    def testTupleValue(self):
        TEST_FILE_NAME = self._filenames[0]
        value = (1, "item2", False)
        config.set(TEST_FILE_NAME, "Test", "test_1", value)
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        self.assertEqual([str(v) for v in value], settings.get(
                               self._filenames[0], "Test", "test_1").getList())

    def testOptionsEqual(self):
        TEST_FILE_NAME0 = self._filenames[0]
        TEST_FILE_NAME1 = self._filenames[1]
        value = "item"
        config.set(TEST_FILE_NAME0, "Test0", "option0", value)
        config.set(TEST_FILE_NAME0, "Test0", settings._META_OPTION_NAME,
            settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME1, "Test1", "option1", value)
        config.set(TEST_FILE_NAME1, "Test1", settings._META_OPTION_NAME,
            settings._META_OPTION_VALUE)
        self.assertTrue(config.get(TEST_FILE_NAME0, "Test0", "option0")==
            config.get(TEST_FILE_NAME1, "Test1", "option1"))

    def testOptionValueEqual(self):
        TEST_FILE_NAME = self._filenames[0]
        value = "item"
        config.set(TEST_FILE_NAME, "Test", "option", value)
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
            settings._META_OPTION_VALUE)
        self.assertTrue(config.get(TEST_FILE_NAME, "Test", "option")==value)

class SettingsSectionTest(unittest.TestCase):
    _filenames = ('__testCaseSettings0__', '__testCaseSettings1__')
    _populated = False

    def setUp(self):
        files = []
        for file in self._filenames:
            files.append(os.path.join(config._USER_CONF_DIR, _PROGRAM_NAME,
                                      ''.join((file, config._CONF_FILE_EXT))))
        self._files = tuple(files)
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass
        config.reload()

    def tearDown(self):
        for file in self._files:
            try:
                os.remove(file)
            except OSError:
                pass

    def testValueAddExistingSection(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test")
        item = settings.get(TEST_FILE_NAME, "Test", force=True)
        item["test_1"] = "1"
        self.assertEqual(settings._META_OPTION_VALUE,
                config.get(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test", "test_1"))

    def testValueAddWrongSettOptVal(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME, "Test")
        self.assertNotEqual(settings._META_OPTION_VALUE,
                config.get(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        item = settings.get(TEST_FILE_NAME, "Test", force=True)
        item["test_1"] = "1"
        self.assertTrue(settings._META_OPTION_NAME in config.get(
                                                       TEST_FILE_NAME, "Test"))
        self.assertEqual(settings._META_OPTION_VALUE, config.get(
                           TEST_FILE_NAME, "Test", settings._META_OPTION_NAME))
        self.assertEqual("1", config.get(TEST_FILE_NAME, "Test", "test_1"))

    def testValueGet(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        config.set(TEST_FILE_NAME, "Test", "test_2", "11")
        item = settings.get(TEST_FILE_NAME, "Test")
        self.assertEqual("11", item["test_2"].get())
        self.assertTrue(item["test_5"].get() is None)

    def testRemoveSettings(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        config.set(TEST_FILE_NAME, "Test", "test_1", "1")
        item_1 = settings.get(TEST_FILE_NAME, "Test")
        item_1.remove()
        self.assertFalse("Test" in config.get(TEST_FILE_NAME))

    def testHaveSettings(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", "test_1", "True")
        self.assertTrue(settings.get(TEST_FILE_NAME, "Test") is None)
        self.assertTrue(settings.get(TEST_FILE_NAME, "Test", "test_1") is None)
        self.assertTrue(settings.get(TEST_FILE_NAME, "Test2") is None)
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        self.assertFalse(settings.get(TEST_FILE_NAME, "Test") is None)
        self.assertFalse(settings.get(TEST_FILE_NAME, "Test", "test_1") is None)
        self.assertTrue(settings.get(TEST_FILE_NAME, "Test2") is None)

    def testIter(self):
        TEST_FILE_NAME = self._filenames[0]
        config.set(TEST_FILE_NAME, "Test", settings._META_OPTION_NAME,
                                                 settings._META_OPTION_VALUE)
        refDict = {"test_1": "1", "test_2": "2"}
        for key, value in refDict.iteritems():
            config.set(TEST_FILE_NAME, "Test", key, value)
        item = settings.get(TEST_FILE_NAME, "Test")
        for option in item:
            self.assertTrue(option.name() in refDict, option)
            self.assertEqual(option.get(), refDict[option.name()])


if __name__ == "__main__":
    unittest.main()

