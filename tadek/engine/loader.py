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

import sys

from tadek import testsuites
from tadek.core import location
from tadek.core.structs import ErrorBox

from testdefs import TestSuite

class TestLoader(object):
    '''
    A class responsible for loading test cases.
    '''
    # A base class of test suites
    suiteClass = TestSuite

    def _isTestSuite(self, mdl, obj):
        '''
        Checks if the given object is a test suite.
        '''
        return (isinstance(obj, type) and
                mdl.__name__ == obj.__module__ and
                issubclass(obj, self.suiteClass))

    def loadFromModule(self, module, names=None):
        '''
        Loads tests from a module of the given names.
        '''
        tests = []
        errors = []
        module = '.'.join([testsuites.__name__, module])
        try:
            __import__(module)
        except:
            errors.append(ErrorBox(name=module))
            return tests, errors
        mdl = sys.modules[module]
        if names:
            suites = {}
            for name in names:
                parts = name.split('.', 1)
                name, parts = parts[0], parts[1:]
                if name not in suites:
                    suites[name] = []
                if parts:
                    suites[name].append(parts[0])
            for name in suites:
                try:
                    suite = getattr(mdl, name)
                    if not self._isTestSuite(mdl, suite):
                        raise AttributeError("Module '%s' has no suite '%s'"
                                              % (module, name))
                    tests.append(suite(*suites[name]))
                except:
                    errors.append(ErrorBox(name='.'.join([module, name])))
        else:
            for name, suite in vars(mdl).iteritems():
                if self._isTestSuite(mdl, suite):
                    try:
                        tests.append(suite())
                    except:
                        errors.append(ErrorBox(name='.'.join([module, name])))
        return tests, errors

    def loadFromNames(self, *names):
        '''
        Loads tests of the given names.
        '''
        location.clear()
        # Make sure that all names are not related
        tests = []
        errors = []
        names = names or None
        if names:
            nms = []
            for name in names:
                name = name.strip().strip('.')
                if not name:
                    continue
                ok = True
                for nm in nms[:]:
                    if name == nm or name.startswith(nm + '.'):
                        ok = False
                        break
                    if nm.startswith(name + '.'):
                        nms.remove(nm)
                if ok:
                    nms.append(name)
            names = nms
        # Load tests from given names
        modules = {}
        for mdl in sorted(location.getSuites(), reverse=True):
            if names is None:
                modules[mdl] = None
            else:
                for name in names[:]:
                    if mdl == name or mdl.startswith(name + '.'):
                        modules[mdl] = None
                        if mdl == name:
                            names.remove(name)
                    elif name.startswith(mdl + '.'):
                        if mdl not in modules:
                            modules[mdl] = []
                        modules[mdl].append(name[len(mdl)+1:])
                        names.remove(name)
        if names:
            for name in names:
                modules[name] = None
        for mdl, nms in modules.iteritems():
            mtests, merrs = self.loadFromModule(mdl, nms)
            tests.extend(mtests)
            errors.extend(merrs)
        return tests, errors

    def loadTree(self, name=None):
        '''
        Loads tests into a tree from the given directory of the specified name.
        '''
        tree = {}
        errors = []
        loaded = False
        location.clear()
        for mdl in sorted(location.getSuites(), reverse=True):
            if name:
                if (name != mdl and not name.startswith(mdl + '.')
                    and not mdl.startswith(name + '.')):
                    continue
            loaded = True
            parts = mdl.split('.')
            branch = tree
            for nm in parts:
                if nm not in branch:
                    branch[nm] = {}
                branch = branch[nm]
            nm = name[len(mdl)+1:] if name and len(name) > len(mdl) else None
            branch[None], merrs = self.loadFromModule(mdl, nm and [nm])
            errors.extend(merrs)
            if name and len(name) >= len(mdl):
                break
        if name and not loaded:
            errors = self.loadFromModule(name)[1]
        return tree, errors

