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

from tadek.connection import protocol

class ChildIter(object):
    '''
    A base class of iterators those iterate through children of the given
    accessible representing a widget object.
    '''
    def __init__(self, accessible, **params):
        self._accessible = accessible
        self._params = params

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration


class Children(ChildIter):
    '''
    A class of iterators those iterate only through direct children of the given
    accessible.
    '''
    def __init__(self, accessible, **params):
        ChildIter.__init__(self, accessible, **params)
        self._index = 0

    def next(self):
        if self._index >= self._accessible.count:
            raise StopIteration
        path = self._accessible.path.child(self._index)
        self._index += 1
        return self._accessible.device.getAccessible(path, **self._params)


class ChildrenBackwards(ChildIter):
    '''
    A class of backward iterators those iterate only through direct children of
    the given widget object (accessible) starting from the last child widget.
    '''
    def __init__(self, accessible, **params):
        ChildIter.__init__(self, accessible, **params)
        self._index = self._accessible.count

    def next(self):
        self._index -= 1
        if self._index < 0:
            raise StopIteration
        path = self._accessible.path.child(self._index)
        return self._accessible.device.getAccessible(path, **self._params)


class Descendants(ChildIter):
    '''
    A class of iterators those iterate level by level through descendants of
    the given widget object.
    '''
    def __init__(self, accessible, **params):
        ChildIter.__init__(self, accessible, **params)
        self._index = 0
        self._queue = []

    def next(self):
        if self._index >= self._accessible.count:
            if not self._queue:
                raise StopIteration
            self._accessible = self._queue.pop(0)
            self._index = 0
        path = self._accessible.path.child(self._index)
        self._index += 1
        child = self._accessible.device.getAccessible(path, **self._params)
        if child and child.count:
            self._queue.append(child)
        return child


_methodMap = {
    protocol.MHD_SEARCH_SIMPLE: Children,
    protocol.MHD_SEARCH_BACKWARDS: ChildrenBackwards,
    protocol.MHD_SEARCH_DEEP: Descendants
}

def getByMethod(method):
    '''
    Gets an iterator class by the given search method.

    :param method: A search method
    :type method: string
    :return: An iterator class
    :rtype: type
    '''
    return _methodMap.get(method, ChildIter)

