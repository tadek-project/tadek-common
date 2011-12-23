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
import ConfigParser
import os

from tadek.core import config

__all__ = ["ConfigTest"]

_PROGRAM_NAME = 'unittest'

class ConfigTest(unittest.TestCase):
    _filenames = ('__testCaseConfig0__', '__testCaseConfig1__')
    _configCheck = ConfigParser.ConfigParser()
    _populated = False

    def _parserReload(self):
        self._configCheck = ConfigParser.ConfigParser()
        return self._configCheck.read((self._files), )

    def _setUpTestFiles(self):
        try:
            os.mkdir(os.path.dirname(self._files[1]))
        except OSError:
            pass
        test_file = open(self._files[1], 'w')
        configWriter = ConfigParser.ConfigParser()
        configWriter.add_section('Test_2')
        configWriter.set('Test_2', 'test2_1', '2')
        configWriter.set('Test_2', 'test2_2', '22')
        configWriter.set('Test_2', 'test2_3', 'True')
        configWriter.add_section('Test_3')
        configWriter.set('Test_3', 'test3_1', '3')
        configWriter.set('Test_3', 'test3_2', '33')
        configWriter.add_section('Test_4')
        configWriter.set('Test_4', 'test4_1', '4')
        configWriter.set('Test_4', 'test4_2', '44')
        configWriter.set('Test_4', 'test4_3', 'True')
        configWriter.set('Test_4', 'test4_4', 'Test')
        configWriter.write(test_file)
        test_file.close()
        test_file = open(self._files[1],'r')
        config.update(self._filenames[1], test_file)
        test_file.close()

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

    def tearDown(self):
        for file_ in self._files:
            try:
                os.remove(file_)
            except OSError:
                pass

    def testGetProgramName(self):
        self.assertEqual(_PROGRAM_NAME, config.getProgramName())

    def testFileCreation(self):
        config.set(self._filenames[0])
        files = self._parserReload()
        self.assertTrue(self._files[0] in files)

    def testValueAddToNewFile(self):
        config.set(self._filenames[0], 'Test_0')
        config.set(self._filenames[0], 'Test_1', 'test1_1', 'True')
        config.set(self._filenames[0], 'Test_1', 'test1_2')
        self._parserReload()
        self.assertTrue(self._configCheck.has_section('Test_0'))
        self.assertTrue(self._configCheck.has_section('Test_1'))
        self.assertTrue(self._configCheck.get('Test_1', 'test1_1'))
        self.assertEqual('', self._configCheck.get('Test_1', 'test1_2'))

    def testValueAddExistingSection(self):
        self._setUpTestFiles()
        config.set(self._filenames[1], 'Test_5', 'test5_1', '5')
        self._parserReload()
        self.assertEqual('5', self._configCheck.get('Test_5', 'test5_1'))

    def testValueGet(self):
        self._setUpTestFiles()
        self.assertTrue(self._filenames[1] in config.get())
        self.assertTrue('Test_4' in config.get(self._filenames[1]))
        self.assertEqual(['test4_1', 'test4_2', 'test4_3', 'test4_4'],
                           sorted(config.get(self._filenames[1], 'Test_4')))
        self.assertEqual('44', config.get(self._filenames[1], 'Test_4',
                                                                    'test4_2'))

    def testValueRemove(self):
        self._setUpTestFiles()
        self._parserReload()
        self.assertEqual('4', self._configCheck.get('Test_4', 'test4_1'))
        config.remove(self._filenames[1], 'Test_4', 'test4_1')
        self._parserReload()
        self.assertRaises(ConfigParser.NoOptionError,
                            self._configCheck.get,'Test_4', 'test4_1')

        self.assertTrue('Test_4' in self._configCheck.sections())
        config.remove(self._filenames[1], 'Test_4')
        self.assertTrue(self._files[1] in self._parserReload())
        self.assertFalse('Test_4' in self._configCheck.sections())

        config.remove(self._filenames[1])
        self.assertFalse(self._files[1] in self._parserReload())

    def testGetBool(self):
        self._setUpTestFiles()
        self.assertEqual(True, config.getBool(self._filenames[1],
                                                         'Test_4', 'test4_3'))
        self.assertEqual(None, config.getBool(self._filenames[1],
                                                         'Test_4', 'test4_4'))

    def testListValue(self):
        self._setUpTestFiles()
        value = ["item1", "item2", "item3"]
        config.set(self._filenames[1], "Test_5", "test5_1", value)
        self.failUnlessEqual(value, config.getList(self._filenames[1],
                                                  "Test_5", "test5_1"))

    def testTupleValue(self):
        self._setUpTestFiles()
        value = (1, "item2", False)
        config.set(self._filenames[1], "Test_5", "test5_2", value)
        self.failUnlessEqual(["1", "item2", "False"],
                     config.getList(self._filenames[1], "Test_5", "test5_2"))

if __name__ == "__main__":
    unittest.main()

