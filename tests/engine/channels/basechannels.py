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
import shutil
import unittest
import traceback

from tadek.core import settings
from tadek.engine import channels
from tadek.engine import testresult

from engine.commons import FakeDevice, createRandomSizeFile
from testchannels import TestClass01, TestClass11

__all__ = ["ChannelsTest", "CoreDumpsChannelTest"]

class MetaTest(type):
    def __new__(mcs, name, bases, dict):
        dict["channel"] = channels.get()[int(dict["channelIdx"])]
        dict["channelClass"] = channels.get()[
                                int(dict["channelIdx"])].__class__
        return type.__new__(mcs, name, bases, dict)


def getBaseClass():
    class ChannelTest(unittest.TestCase):
        def testIsEnabled(self):
            channel = self.channelClass("Test")
            self.assertEqual(True, channel.isEnabled())
            channel._enabled = False
            self.assertEqual(False, channel.isEnabled())
            channel._enabled = True
            self.assertEqual(True, channel.isEnabled())

        def testIsVerbose(self):
            channel = self.channelClass("Test")
            self.assertEqual(False, channel.isVerbose())
            channel._verbose = True
            self.assertEqual(True, channel.isVerbose())
            channel._verbose = False
            self.assertEqual(False, channel.isVerbose())

    return ChannelTest

testedChannels = []
for idx, name in enumerate(channels.get()):
    if name.__class__.__name__ not in testedChannels:
        exec('''class T%s(getBaseClass()):
                channelIdx = "%d"
                __metaclass__ = MetaTest''' % (name.name, idx))
        testedChannels.append(name.__class__.__name__)


class TestClass0:
    pass


class TestClass1(channels.TestResultChannel):
    def __init__(self, name):
        self.name = name


class ChannelsTest(unittest.TestCase):
    def configureChannel(self, name, clsname, **params):
        section = settings.get(channels.CONFIG_NAME, name, force=True)
        section["class"] = clsname
        for param, value in params.iteritems():
            section[param] = value
        self.configChannels.append(name)

    def setUp(self):
        self.configChannels = []
        self.existingChannels = channels._cache.keys()
        self.registeredClasses = channels._registry.keys()

    def tearDown(self):
        channelsNames = channels._cache.keys()
        classesNames = channels._registry.keys()
        for channelName in channelsNames:
            if channelName not in self.existingChannels:
                channels.remove(channelName)
        for className in classesNames:
            if className not in self.registeredClasses:
                del channels._registry[className]
        for channelName in self.configChannels:
            settings.remove(channels.CONFIG_NAME, channelName)

    def assertRaises(self, exc, fun, *args, **kwargs):
        try:
            fun(*args, **kwargs)
        except exc:
            # We expect the exception is raised
            # inside the given function body but
            # not in the above line itself.
            if (len(traceback.extract_tb(sys.exc_info()[2]))<2 or
                    (hasattr(self, "exceptionMessage") and
                    not str(sys.exc_info()[1]).startswith(
                        self.exceptionMessage))):
                raise
            else:
                pass

    def testRegister(self):
        self.assertRaises(TypeError, channels.register, TestClass0)
        self.assertTrue(channels.register(TestClass1))
        self.assertTrue(TestClass1.__name__ in channels._registry)
        self.assertEqual(False, channels.register(TestClass1))

    def testAdd1(self):
        self.exceptionMessage = "Invalid channel class:"
        self.assertRaises(TypeError, channels.add, TestClass0, "test0")
        self.exceptionMessage = "Invalid channel class name:"
        self.assertRaises(TypeError, channels.add, "TestClass0", "test0")

    def testAdd2(self):
        name1 = "test1"
        name2 = "test2"
        params = {'a':1}
        channels.add(TestClass1, name1, **params)
        self.assertTrue(name1 in channels._cache)
        self.assertEqual(TestClass1, channels._cache[name1][0])
        self.assertTrue('a' in channels._cache[name1][1])
        self.assertEqual(1, channels._cache[name1][1]['a'])
        length = len(channels._cache)
        self.exceptionMessage = "Channel with such a name already exists:"
        self.assertRaises(ValueError, channels.add, TestClass1, name1)
        channels.add(TestClass1, name2)
        self.assertEqual(len(channels._cache), length+1)

    def testAdd3(self):
        name1 = "test1"
        name2 = "test2"
        self.exceptionMessage = "Invalid channel class name:"
        self.assertRaises(TypeError, channels.add, "TestClass1", "test1")
        channels.register(TestClass1)
        className1 = TestClass1.__name__
        channels.add(className1, name1)
        self.assertTrue(name1 in channels._cache)
        self.assertEqual(TestClass1, channels._cache[name1][0])
        length = len(channels._cache)
        self.exceptionMessage = "Channel with such a name already exists:"
        self.assertRaises(ValueError, channels.add, className1, name1)
        channels.add(TestClass1, name2)
        self.assertEqual(len(channels._cache), length+1)

    def testRemove(self):
        channel = TestClass1("Test")
        channels._cache[channel.name] = channel
        self.assertEqual(None, channels.remove("TestName"))
        self.assertEqual(channel, channels.remove("Test"))
        self.assertFalse(channel.name in channels._cache)

    def testGetConfigured(self):
        _channelMaps = (("_testchl1", TestClass01),
                        ("_testchl2", TestClass11),
                        ("_testchl4", TestClass01),
                        ("_testchl5", TestClass11))
        for name, cls in _channelMaps:
            self.configureChannel(name, cls.__name__)
        self.configureChannel("_testchl3", "TestClass03")
        channelList = channels.get()
        for channel in channelList:
            self.failIfEqual(channel.name, "_testchl3")
        for name, cls in _channelMaps:
            for channel in channelList:
                if channel.name == name:
                    break
            self.failUnlessEqual(channel.name, name)
            self.failUnless(isinstance(channel, cls))

    def testGetPredefined(self):
        channels.add(TestClass1, "_testchl1")
        channels.add("TestClass01", "_testchl2", arg2=0)
        channelList = channels.get()
        for channel in channelList:
            if channel.name == "_testchl1":
                break
        self.failUnlessEqual(channel.name, "_testchl1")
        self.failUnless(isinstance(channel, TestClass1))
        for channel in channelList:
            if channel.name == "_testchl2":
                break
        self.failUnlessEqual(channel.name, "_testchl2")
        self.failUnless(isinstance(channel, TestClass01))

class CoreDumpsChannelTest(unittest.TestCase):
    _TEST_CORE_DIR = os.path.abspath(os.path.join("tests", "_coredumps"))
    _TEST_CORE_EXT = "core"
    _TEST_CORE_PATTERN = ".+\." + _TEST_CORE_EXT

    def _createCore(self, dirname, name):
        dirpath = os.path.join(self._TEST_CORE_DIR, dirname)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            dirs = [d for d in self.coreDumps._dirs]
            dirs.append(dirpath)
            self.coreDumps._dirs.set(','.join(dirs))
        path = os.path.join(dirpath, name + '.' + self._TEST_CORE_EXT)
        createRandomSizeFile(path)
        return path

    def setUp(self):
        self.coreDumps = channels.CoreDumpsChannel()
        section = settings.get(channels.CONFIG_NAME,
                               self.coreDumps.name, force=True)
        self._origDirs = str(section["dirs"])
        section["dirs"] = ''
        self._origPattern = str(section["pattern"])
        section["pattern"] = self._TEST_CORE_PATTERN
        self.coreDumps.start(None)

    def tearDown(self):
        self.coreDumps.stop()
        section = settings.get(channels.CONFIG_NAME,
                               self.coreDumps.name, force=True)
        section["dirs"] = self._origDirs
        section["pattern"] = self._origPattern
        if os.path.exists(self._TEST_CORE_DIR):
            shutil.rmtree(self._TEST_CORE_DIR)

    def testEmptyCoreDirs(self):
        device = FakeDevice()
        result = testresult.DeviceExecResult(device)
        self.coreDumps.startTest(result, device)
        self.coreDumps.stopTest(result, device)
        self.failIf(result.cores)

    def testCoreBeforeStart(self):
        device = FakeDevice()
        result = testresult.DeviceExecResult(device)
        core = self._createCore("coredir1", "corefile11")
        self.coreDumps.startTest(result, device)
        self.failIf(result.cores)
        self.coreDumps.stopTest(result, device)
        self.failIf(result.cores)

    def testCoreAfterStart(self):
        device = FakeDevice()
        result = testresult.DeviceExecResult(device)
        self.coreDumps.startTest(result, device)
        self.failIf(result.cores)
        core = self._createCore("coredir1", "corefile11")
        self.coreDumps.stopTest(result, device)
        self.failUnless(core in result.cores)

    def testCoresBeforeAfterStart(self):
        device = FakeDevice()
        result = testresult.DeviceExecResult(device)
        cores = []
        self._createCore("coredir1", "corefile11")
        self._createCore("coredir2", "corefile21")
        self.coreDumps.startTest(result, device)
        self.failIf(result.cores)
        cores.append(self._createCore("coredir1", "corefile12"))
        cores.append(self._createCore("coredir2", "corefile22"))
        self.coreDumps.stopTest(result, device)
        self.failUnlessEqual(len(result.cores), 2)
        for core in cores:
            self.failUnless(core in result.cores)

    def testCoresAfterStart1(self):
        device = FakeDevice()
        result1 = testresult.DeviceExecResult(device)
        result2 = testresult.DeviceExecResult(device)
        cores = []
        self.coreDumps.startTest(result1, device)
        self.failIf(result1.cores)
        cores.append(self._createCore("coredir1", "corefile11"))
        cores.append(self._createCore("coredir1", "corefile12"))
        self.coreDumps.startTest(result2, device)
        self.failUnlessEqual(len(result2.cores), 2)
        for core in cores:
            self.failUnless(core in result2.cores)
        self.coreDumps.stopTest(result2, device)
        self.failIf(result2.cores)
        self.coreDumps.stopTest(result1, device)
        self.failUnlessEqual(len(result1.cores), 2)
        for core in cores:
            self.failUnless(core in result1.cores)

    def testCoresAfterStart1AfterStart2(self):
        device = FakeDevice()
        result1 = testresult.DeviceExecResult(device)
        result2 = testresult.DeviceExecResult(device)
        cores1 = []
        cores2 = []
        self.coreDumps.startTest(result1, device)
        self.failIf(result1.cores)
        cores1.append(self._createCore("coredir1", "corefile11"))
        cores1.append(self._createCore("coredir2", "corefile21"))
        self.coreDumps.startTest(result2, device)
        self.failUnlessEqual(len(result2.cores), 2)
        for core in cores1:
            self.failUnless(core in result2.cores)
        cores2.append(self._createCore("coredir1", "corefile12"))
        cores2.append(self._createCore("coredir2", "corefile22"))
        self.coreDumps.stopTest(result2, device)
        self.failUnlessEqual(len(result2.cores), 2)
        for core in cores2:
            self.failUnless(core in result2.cores)
        self.coreDumps.stopTest(result1, device)
        self.failUnlessEqual(len(result1.cores), 2)
        for core in cores1:
            self.failUnless(core in result1.cores)

    def testCoreAfterStart1OverwriteAfterStart2(self):
        device = FakeDevice()
        result1 = testresult.DeviceExecResult(device)
        result2 = testresult.DeviceExecResult(device)
        self.coreDumps.startTest(result1, device)
        self.failIf(result1.cores)
        core = self._createCore("coredir1", "corefile11")
        self.coreDumps.startTest(result2, device)
        self.failUnlessEqual(len(result2.cores), 1)
        self.failUnless(core in result2.cores)
        core = self._createCore("coredir1", "corefile11")
        self.coreDumps.stopTest(result2, device)
        self.failUnlessEqual(len(result2.cores), 1)
        self.failUnless(core in result2.cores)
        self.coreDumps.stopTest(result1, device)
        self.failUnlessEqual(len(result1.cores), 1)
        self.failUnless(core in result1.cores)
        self.failIfEqual(id(result1.cores[0]), id(result2.cores[0]))

if __name__ == "__main__":
    unittest.main()

