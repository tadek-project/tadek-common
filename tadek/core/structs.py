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
import traceback

__all__ = ["FileDetails", "ErrorBox"]

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class FileDetails:
    '''
    A simple class for storing details about a file.
    '''
    def __init__(self, path, mtime=None, size=None):
        self.path = path
        if mtime is None:
            mtime = os.path.getmtime(path)
        self.mtime = mtime
        if size is None:
            size = os.path.getsize(path)
        self.size = size

    def __eq__(self, file):
        return self.path == (file.path if hasattr(file, "path") else file)

    def __ne__(self, file):
        return not (self == file)


class ErrorBox:
    '''
    A simple class for storing all needed information about a raised exception.
    '''
    def __init__(self, **kwargs):
        self.traceback = traceback.format_exc()
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

