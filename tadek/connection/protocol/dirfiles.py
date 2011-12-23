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
import re
from xml.etree import cElementTree as etree

from tadek.connection.protocol import extension
from tadek.connection.protocol import parameters
from tadek.core.structs import FileDetails
from tadek.core.utils import decode

class FileDetailsParameter(parameters.MessageParameter):
    '''
    A class of file details message parameters.
    '''
    type = FileDetails

    def marshal(self, element, value):
        etree.SubElement(element, "path").text = decode(value.path)
        etree.SubElement(element, "mtime").text = decode(value.mtime)
        etree.SubElement(element, "size").text = decode(value.size)

    def unmarshal(self, element):
        path = element.findtext("path")
        mtime = float(element.findtext("mtime"))
        size = int(element.findtext("size"))
        return self.type(path, mtime=mtime, size=size)


class DirFilesExtension(extension.ProtocolExtension):
    '''
    A protocol extension class for listing directory files.
    '''
    name = u"dirfiles"

    requestParams = {
        "path": parameters.UnicodeParameter(),
        "pattern": parameters.UnicodeParameter(),
        "recursive": parameters.BooleanParameter(),
        "links": parameters.BooleanParameter()
    }

    responseParams = {
        "files": parameters.ListParameter(FileDetailsParameter(), iname="file")
    }

    def request(self, path, pattern=".+", recursive=False, links=False):
        '''
        Provides a full list of the file details request.

        :param path: A name of the directory with files
        :type path: string
        :param pattern: A pattern as regular expression of file names
        :type pattern: string
        :param recursive: True if the result should include files from all
                          subdirectories
        :type recursive: boolean
        :param links: True if the result should include symbolic links
        :type links: boolen
        :return: A dictionary containing all request parameters
        :rtype: dictionary
        '''
        return extension.ProtocolExtension.request(self, path=path,
                                                         pattern=pattern,
                                                         recursive=recursive,
                                                         links=links)

    def response(self, path, pattern, recursive, links):
        '''
        Gets list of directory files specified by the path according to
        the given parameters.
        '''
        def getDirFiles(dirpath, pattern):
            files = []
            try:
                names = os.listdir(dirpath)
            except IOError:
                return files
            for name in names:
                path = os.path.join(dirpath, name)
                if os.path.islink(path) and not links:
                    continue
                if os.path.isfile(path):
                    match = pattern.match(name)
                    if match and match.span() == (0, len(name)):
                        files.append(FileDetails(path))
                elif os.path.isdir(path) and recursive:
                    files.extend(getDirFiles(path, pattern))
            return files
        files = []
        status = True
        if os.path.isdir(path):
            files = getDirFiles(os.path.abspath(path), re.compile(pattern))
        else:
            status = False
        return status, {"files": files}

