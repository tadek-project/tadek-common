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

from tadek.core import accessible

import delay
import searchers

class Path(object):
    '''
    A class of paths consisting of searchers pointing to GUI elements (widgets).
    '''
    class PathDevice(object):
        '''
        Calls the search() method of a given path with a specified device.
        '''
        def __init__(self, path, device):
            self.path = path
            self.device = device

        def __call__(self):
            return self.path.search(self.device)

    def __init__(self, *path):
        '''
        Stores a base of path (a start point) and a list of searchers defining
        the path to a widget.

        :param path: A list of the path elements
        :type path: tuple
        '''
        self._base = None
        self._searchers = []
        # First element might be a reference to other path
        if path and  hasattr(path[0], "getPath"):
            self._base = path[0]
            path = path[1:]
        for item in path:
            if isinstance(item, searchers.BaseSearcher):
                self._searchers.append(item)
            elif isinstance(item, int):
                self._searchers.append(searchers.searcher(index=item))
            elif isinstance(item, basestring):
                self._searchers.append(searchers.searcher__(name=item))
            else:
                raise TypeError("Invalid path item: %s" % item)

    def getPath(self):
        '''
        Returns the path - itself in this case.

        :return: The path
        :rtype: Path
        '''
        return self

    def setBase(self, base):
        '''
        Sets a new base of the path to a widget, if the base has an attribute
        'getPath'.

        :param base: The new base of the path
        :type base: Path
        '''
        if not hasattr(base, "getPath"):
            raise TypeError("Invalid base for the path: %s" % base)
        self._base = base

    def __call__(self, device, execdelay=None, expectedFailure=False):
        '''
        Executes a searching of widget pointed by the path using the given delay
        object.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param execdelay: A delay instance used to execute the searching
        :type execdelay: Delay
        :param expectedFailure: Specifies if the searching of a widget by
            the path should fail
        :type expectedFailure: boolean
        :return: A result of the searching of a widget
        :rtype: Widget or NoneType
        '''
        if execdelay is None:
            execdelay = delay.default
        if not isinstance(execdelay, delay.Delay):
            raise TypeError
        return execdelay(self.PathDevice(self, device), expectedFailure)

    def search(self, device):
        '''
        Performs a searching of a widget pointed by the path.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A searching widget or None if fails
        :rtype: Widget or NoneType
        '''
        if self._base is None:
            acc = accessible.Accessible(accessible.Path())
            acc.device = device
        else:
            acc = self._base.getPath().search(device)
        for searcher in self._searchers:
            if acc is None:
                return None
            acc = searcher.find(acc)
        return acc


class Object(object):
    '''
    A base class for representing any UI object.
    '''
    def __init__(self, *path):
        '''
        Stores a path to the represented object.

        :param path: A list of path elements, each of which can be either
            a BaseSearcher or an integer that is interpreted as a searcher with
            constant index parameter or a string that is interpreted as
            a searcher__ with constant name parameter
        :type path: tuple
        '''
        self._path = Path(*path)

    def getPath(self):
        '''
        Gets a path to the represented object.

        :return: A path to the represented object
        :rtype: Object
        '''
        return self._path

    def addPath(self, *path):
        '''
        Returns a new instance of Object class representing a child object of
        the base object, pointed by the given relative path of searchers.

        :param path: A relative path to the child widget given as a list
            of searchers
        :type path: tuple
        :return: A new Object instance
        :rtype: Object
        '''
        return Object(self, *path)

    def define(self, pathname, obj, relative=True):
        '''
        Adds the given Object instance to the current Object as an attribute
        of the specified name or path of names.

        :param pathname: A name of the child object, if the name is dotted
            then the name also contains a names of ancestors of the object
        :type pathname: string
        :param obj: The object to add
        :type obj: Object
        :param relative: If True then a base of a path to the child object is
            the current object, False means that the child object contains
            an absolute path
        :type relative: boolean
        '''
        if not hasattr(obj, "getPath"):
            obj = Object(obj)
        path = pathname.split('.')
        base = self
        for name in path[:-1]:
            base = getattr(base, name)
        if relative:
            obj.getPath().setBase(base.getPath())
        setattr(base, path[-1], obj)

