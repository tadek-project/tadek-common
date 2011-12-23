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

from tadek.connection import protocol
from tadek.connection.protocol import message
from tadek.connection.protocol import extension
from tadek.connection.protocol import parameters
from tadek.core.accessible import Path, Accessible

__all__ = ["ProtocolTest", "MessagesTest", "ExtensionsTest"]


class ProtocolTest(unittest.TestCase):
    def testCreateInvalidType(self):
        try:
            protocol.create("InvalidType",
                            protocol.MSG_TARGET_SYSTEM,
                            protocol.MSG_NAME_GET, parameter=True)
        except protocol.UnsupportedMessageError, err:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testCreateInvalidTarget(self):
        try:
            protocol.create(protocol.MSG_TYPE_REQUEST,
                            "InvalidTarget",
                            protocol.MSG_NAME_GET, parameter=True)
        except protocol.UnsupportedMessageError, err:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testCreateInvalidName(self):
        try:
            protocol.create(protocol.MSG_TYPE_REQUEST,
                            protocol.MSG_TARGET_SYSTEM,
                            "InvalidName", parameter=True)
        except protocol.UnsupportedMessageError, err:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testCreateInvalidParameter(self):
        try:
            protocol.create(protocol.MSG_TYPE_REQUEST,
                            protocol.MSG_TARGET_SYSTEM,
                            protocol.MSG_NAME_GET, parameter=True)
        except protocol.UnsupportedMessageError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testClassConflict(self):
        message.registerRequest("TestTarget", "TestName",
                                parameter=parameters.IntParameter())
        try:
            message.registerRequest("TestTarget", "TestName",
                                    parameter=parameters.FloatParameter())
        except message.MessageClassConflictError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)


class MessagesTest(unittest.TestCase):
    # REQUSTS
    def testParseDefaultRequest(self):
        req1 = message.DefaultRequest("TestTarget", "TestName")
        req2 = protocol.parse(req1.marshal(), message.DefaultRequest)
        self.failUnless(isinstance(req2, message.DefaultRequest))
        self.failUnlessEqual(req1.id, req2.id)

    def testParseDefaultRequestError(self):
        req = message.DefaultRequest("TestTarget", "TestName")
        try:
            protocol.parse(req.marshal())
        except protocol.UnsupportedMessageError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testGetA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "depth": 3,
            "include": (u"name", u"role", u"count", u"text")
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_GET, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testSearchA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "method": protocol.MHD_SEARCH_SIMPLE,
            "predicates": {
                            "name": u"TestName",
                            "role": u"TestRole",
                            "count": 3,
                            "text": u"TestText"
            }
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_SEARCH, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testPutTextA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "text": u"TestText"
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_PUT, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testPutValueA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "value": 3.0
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_PUT, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testExecActionA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "action": u"TestAction"
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_EXEC, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testExecKeyboardA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "keycode": 123,
            "modifiers": (234, 345, 456)
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_EXEC, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testExecMouseA11yRequest(self):
        params = {
            "path": Path(0, 1, 2, 3),
            "button": u"TestButton",
            "event": u"TestEvent",
            "coordinates": (1024, 800)
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_EXEC, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testGetSysRequest(self):
        params = {
            "path": u"TestPath"
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_GET, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testPutSysRequest(self):
        params = {
            "path": u"TestPath",
            "data": u"TestData"
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_PUT, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    def testExecSysRequest(self):
        params = {
            "command": u"TestCommand",
            "wait": True
        }
        req = protocol.create(protocol.MSG_TYPE_REQUEST,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_EXEC, **params)
        self.failUnless(isinstance(req, message.Request))
        cls = type(req)
        req = protocol.parse(req.marshal())
        self.failUnless(isinstance(req, cls))
        for name in params:
            self.failUnlessEqual(getattr(req, name), params[name])

    # RESPONSES:
    def testParseDefaultResponse(self):
        res1 = message.DefaultResponse("TestTarget", "TestName", status=True)
        res2 = protocol.parse(res1.marshal(), message.DefaultResponse)
        self.failUnless(isinstance(res2, message.DefaultResponse))
        self.failUnlessEqual(res1.id, res2.id)
        self.failUnlessEqual(res2.status, True)

    def testParseDefaultResponseError(self):
        res = message.DefaultResponse("TestTarget", "TestName", status=True)
        try:
            protocol.parse(res.marshal())
        except protocol.UnsupportedMessageError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

    def testGetA11yResponse(self):
        accessible = Accessible(Path(0, 1, 2, 3))
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_GET,
                              accessible=accessible, status=True)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        self.failUnlessEqual(res.accessible.path, accessible.path)
        self.failUnlessEqual(res.status, True)

    def testSearchA11yResponse(self):
        accessible = Accessible(Path(0, 1, 2, 3))
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_SEARCH,
                              accessible=accessible, status=True)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        self.failUnlessEqual(res.accessible.path, accessible.path)
        self.failUnlessEqual(res.status, True)

    def testPutA11yResponse(self):
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_PUT, status=False)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        self.failUnlessEqual(res.status, False)

    def testExecA11yResponse(self):
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_ACCESSIBILITY,
                              protocol.MSG_NAME_EXEC, status=False)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        self.failUnlessEqual(res.status, False)

    def testGetSysResponse(self):
        params = {
            "data": u"TestData",
            "status": True
        }
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_GET, **params)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        for name in params:
            self.failUnlessEqual(getattr(res, name), params[name])

    def testPutSysResponse(self):
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_PUT, status=False)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        self.failUnlessEqual(res.status, False)

    def testExecSysResponse(self):
        params = {
            "stdout": u"TestStdout",
            "stderr": u"TestStderr",
            "status": True
        }
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_EXEC, **params)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        for name in params:
            self.failUnlessEqual(getattr(res, name), params[name])

    def testInfoSysResponse(self):
        params = {
            "version": u"TestVersion",
            "locale": u"TestLocale",
            "extensions": (u"TestExtension1", u"TestExtension2"),
            "status": True
        }
        res = protocol.create(protocol.MSG_TYPE_RESPONSE,
                              protocol.MSG_TARGET_SYSTEM,
                              protocol.MSG_NAME_INFO, **params)
        self.failUnless(isinstance(res, message.Response))
        cls = type(res)
        res = protocol.parse(res.marshal())
        self.failUnless(isinstance(res, cls))
        for name in params:
            self.failUnlessEqual(getattr(res, name), params[name])


class _TestProtocolExtension(extension.ProtocolExtension):
    name = "TestExtension"

    requestParams = {
        "parameter": parameters.IntParameter()
    }
    responseParams = {
        "parameter": parameters.IntParameter()
    }

    def response(self, parameter):
        return True, {"parameter": parameter + 1}


class ExtensionsTest(unittest.TestCase):
    def testGetExtensions(self):
        self.failUnless(_TestProtocolExtension.name in protocol.getExtensions())

    def testGetExtension(self):
        try:
            ext = protocol.getExtension(_TestProtocolExtension.name)
        except extension.UnsupportedProtocolExtensionError:
            self.failIf(True)
        self.failUnless(isinstance(ext, _TestProtocolExtension))

    def testUnsupportedProtocolExtensionError(self):
        try:
            protocol.getExtension("__invalid_extension__")
        except extension.UnsupportedProtocolExtensionError:
            pass
        except:
            self.failIf(True)
        else:
            self.failIf(True)

