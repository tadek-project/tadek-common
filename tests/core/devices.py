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
from tadek.core import devices
from tadek.core import config

__all__ = ["DevicesTest"]

_DEVICE_NAME = "unittest"
_DEVICE_PARAS = {
    "address": "unittest",
    "port": "12345",
    "description": "Device for unit tests"
}

class DevicesTest(unittest.TestCase):
    def setUp(self):
        for param, value in _DEVICE_PARAS.iteritems():
            config.set(devices.CONFIG_NAME, _DEVICE_NAME, param, value)
        devices.reset()

    def tearDown(self):
        config.remove(devices.CONFIG_NAME, _DEVICE_NAME)

    def testLoad(self):
        device = devices.get(_DEVICE_NAME)
        self.failUnless(device)
        devices.load()
        self.failUnlessEqual(device, devices.get(_DEVICE_NAME))

    def testRemove(self):
        devices.remove(_DEVICE_NAME)
        self.failIf(devices.get(_DEVICE_NAME))

    def testUpdate(self):
        devices.update(_DEVICE_NAME, boolean=True)
        device = devices.get(_DEVICE_NAME)
        self.failUnless(device)
        self.failUnless("boolean" in device.params)
        self.failUnlessEqual(device.params["boolean"].getBool(), True)


class AddDevicesTest(unittest.TestCase):
    def setUp(self):
        devices.reset()

    def tearDown(self):
        config.remove(devices.CONFIG_NAME, _DEVICE_NAME)

    def testAdd(self):
        device = devices.add(_DEVICE_NAME, **_DEVICE_PARAS)
        self.failUnless(device)
        self.failUnlessEqual(device, devices.get(_DEVICE_NAME))


class InvalidDevicesTest(unittest.TestCase):
    def setUp(self):
        for param, value in _DEVICE_PARAS.iteritems():
            if param == "address":
                continue
            config.set(devices.CONFIG_NAME, _DEVICE_NAME, param, value)
        devices.reset()

    def tearDown(self):
        config.remove(devices.CONFIG_NAME, _DEVICE_NAME)

    def testLoadInvalid(self):
        devices.load()
        self.failIf(devices.get(_DEVICE_NAME))

