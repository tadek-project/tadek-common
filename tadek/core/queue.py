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

__all__ = ["Queue", "QueueItem"]

import time
import threading


class QueueItem(object):
    '''
    A base class fo items stored in queue objects.
    '''
    def __init__(self, id):
        self.id = id

    def __eq__(self, item):
        if hasattr(item, "id"):
            return self.id == item.id
        return self.id == item

    def __str__(self):
        return ("<%s(id=%s) at 0x%x>"
                 % (self.__class__.__name__, self.id, id(self)))
    __repr__ = __str__


class Queue(object):
    '''
    Creates a queue object of identified items with an infinite size.
    '''
    def __init__(self):
        self._queue = []
        self._mutex = threading.RLock()
        self._not_empty = threading.Condition(self._mutex)
        self._all_done = threading.Condition(self._mutex)

    def __str__(self):
        strq = [str(item) for item in self._queue]
        return ("<%s%s at 0x%x>"
                 % (self.__class__.__name__, tuple(strq), id(self)))

    def _qsize(self, id):
        '''
        Returns a number of items in queue of the given id.
        '''
        if id is None:
            return len(self._queue)
        else:
            return self._queue.count(id)

    def _empty(self, id=None):
        '''
        Checks whether the queue does not contain items of the given id.
        '''
        if id is None:
            return not self._queue
        else:
            return id not in self._queue

    def _put(self, item):
        '''
        Puts a new item in the queue.
        '''
        self._queue.append(item)

    def _get(self, id):
        '''
        Gets an item of the given id from the queue.
        '''
        if id is None:
            return self._queue.pop(0)
        else:
            return self._queue.pop(self._queue.index(id))

    def _notifyNotEmpty(self, id):
        '''
        Notifies the queue is not empty.
        '''
        self._not_empty.notifyAll()

    def _notifyAllDone(self, id):
        '''
        Notifies all tasks of the given id are done in queue.
        '''
        self._all_done.notifyAll()

    def qsize(self, id=None):
        '''
        Returns the approximate number of items in the queue of the given id
        (not reliable!).
        '''
        self._mutex.acquire()
        n = self._qsize(id)
        self._mutex.release()
        return n

    def empty(self, id=None):
        '''
        Returns True if the queue does not contain an item of the given id or
        if the queue is empty in case id equals None, False otherwise
        (not reliable!).
        '''
        self._mutex.acquire()
        n = self._empty(id)
        self._mutex.release()
        return n

    def put(self, item):
        '''
        Puts a new item into the queue.
        '''
        if not isinstance(item, QueueItem):
            raise TypeError("Invalid item type: %s" % type(item).__name__)
        self._mutex.acquire()
        try:
            self._put(item)
            self._notifyNotEmpty(item.id)
        finally:
            self._mutex.release()

    def get(self, id=None, block=True, timeout=None):
        '''
        Removes and returns an item of the given id from the queue, if id is
        None returns a first item in the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a positive number, it blocks at most 'timeout' seconds and returns None
        if no item was available within that time. Otherwise ('block' is false),
        returns an item if one is immediately available, else returns None
        ('timeout' is ignored in that case).
        '''
        self._not_empty.acquire()
        try:
            if not block:
                if self._empty(id):
                    return None
            elif timeout is None:
                while self._empty(id):
                    self._not_empty.wait()
            else:
                if timeout < 0:
                    timeout = -timeout
                endtime = time.time() + timeout
                while self._empty(id):
                    remaining = endtime - time.time()
                    if remaining <= 0.0:
                        return None
                    self._not_empty.wait(remaining)
            return self._get(id)
        finally:
            self._not_empty.release()

    def done(self, id=None):
        '''
        Indicate that a formerly enqueued item is processed.

        Used by Queue consumer threads.  For each get() used to fetch an item,
        a subsequent call to done() tells the queue that the processing on
        the item is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed.
        '''
        self._all_done.acquire()
        try:
            if self._empty(id):
                self._notifyAllDone(id)
        finally:
            self._all_done.release()

    def join(self, id=None):
        '''
        Blocks until all items in the Queue of the given id have been gotten and
        processed.

        A consumer thread calls done() to indicate the item was retrieved and
        all work on it is complete. When a number of items in the queque of
        the given id drops to zero, join() unblocks.
        '''
        self._all_done.acquire()
        try:
            while not self._empty(id):
                self._all_done.wait()
        finally:
            self._all_done.release()

