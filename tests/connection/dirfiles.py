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
import time
import shutil
import random
import unittest
from xml.etree import cElementTree as etree

from tadek.connection import protocol
from tadek.connection.protocol import parameters
from tadek.connection.protocol import dirfiles

__all__ = ["FileDetailsParameterTest", "DirFilesExtensionTest"]

class FileDetailsParameterTest(unittest.TestCase):
    _TEST_FILE_PATH = os.path.abspath(os.path.join("tests", "file.dat"))

    def setUp(self):
        self.fd = dirfiles.FileDetails(self._TEST_FILE_PATH,
                                          time.time(), 1024)
        self.param = dirfiles.FileDetailsParameter()

    def testValidation(self):
        try:
            self.param.validate(self.fd)
        except parameters.ParameterError:
            self.failIf(True)
        try:
            self.param.validate(self._TEST_FILE_PATH)
        except parameters.ParameterError:
            pass
        else:
            self.failIf(True)

    def testMarshaling(self):
        element = etree.Element("file")
        self.param.marshal(element, self.fd)
        fd2 = self.param.unmarshal(element)
        self.failUnless(isinstance(fd2, dirfiles.FileDetails))
        self.failUnlessEqual(fd2, self.fd)
        self.failUnlessEqual(fd2.path, self.fd.path)
        self.failUnlessAlmostEqual(fd2.mtime, self.fd.mtime, 2)
        self.failUnlessEqual(fd2.size, self.fd.size)


class DirFilesExtensionTest(unittest.TestCase):
    _TEST_FILE_PATTERN = ".+\\.dat"
    _TEST_ROOT_DIR = os.path.abspath(os.path.join("tests", "_dirfiles"))
    _TEST_FILE_TREE = (
        ("dir1", "file11.dat"),
        ("dir1", "file12.txt"),
        ("dir1", "dir13", "file131.dat"),
        ("dir1", "file14.dat"),
        ("file2.txt",),
        ("file3.dat",),
        ("file4.txt",),
        ("dir5", "dir51", "file511.txt"),
        ("dir5", "file52.txt"),
        ("dir5", "file53.txt"),
        ("dir5", "file54.dat"),
        ("file6.dat",),
        (("dir7", ("dir1", "dir13")),),
        (("file8.dat", ("dir5", "dir51", "file511.txt")),)
    )
    _TEST_CHAR_SET = ''.join([chr(i) for i in xrange(ord('0'), ord('z')+1)])

    def setUp(self):
        self.dirFiles = protocol.getExtension("dirfiles")
        self.failUnless(self.dirFiles)
        self._fileNameMaps = {}
        for item in self._TEST_FILE_TREE:
            dir, file = item[:-1], item[-1]
            dir = os.path.join(self._TEST_ROOT_DIR, *dir)
            if not os.path.exists(dir):
                os.makedirs(dir)
            if isinstance(file, (tuple, list)):
                path = os.path.join(dir, file[0])
                os.symlink(os.path.join(*file[1]), path)
            else:
                path = os.path.join(dir, file)
                size = random.randint(256, 4096)
                fd = open(path, "wb")
                try:
                    n = 0
                    k = random.randint(len(self._TEST_CHAR_SET) / 4,
                                       len(self._TEST_CHAR_SET) / 2)
                    while n < size:
                        fd.write(''.join(random.sample(self._TEST_CHAR_SET, k)))
                        n += k
                finally:
                    fd.close()
            self._fileNameMaps[os.path.basename(path)] = path

    def tearDown(self):
        shutil.rmtree(self._TEST_ROOT_DIR)

    def testAllFiles(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 4)
        for name in ("file2.txt", "file3.dat", "file4.txt", "file6.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testPatternFiles(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR,
                                       self._TEST_FILE_PATTERN)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 2)
        for name in ("file3.dat", "file6.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testAllFilesLinks(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR, links=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 5)
        for name in ("file2.txt", "file3.dat", "file4.txt",
                     "file6.dat", "file8.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testAllFilesRecursive(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR, recursive=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 12)
        for name in ("file2.txt", "file3.dat", "file4.txt", "file6.dat",
                     "file11.dat", "file12.txt", "file131.dat", "file14.dat",
                     "file511.txt", "file52.txt", "file53.txt", "file54.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testPatternFilesLinks(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR,
                                       self._TEST_FILE_PATTERN, links=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 3)
        for name in ("file3.dat", "file6.dat", "file8.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testAllFilesLinksRecursive(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR, links=True,
                                       recursive=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 14)
        for name in ("file2.txt", "file3.dat", "file4.txt", "file6.dat",
                     "file8.dat", "file11.dat", "file12.txt", "file131.dat",
                     "file14.dat", "file511.txt", "file52.txt", "file53.txt",
                     "file54.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        self.failUnless(os.path.join(self._TEST_ROOT_DIR, "dir7", "file131.dat")
                        in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testPatternFilesRecursive(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR,
                                       self._TEST_FILE_PATTERN, recursive=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 6)
        for name in ("file3.dat", "file6.dat", "file11.dat",
                     "file131.dat", "file14.dat", "file54.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

    def testPatternFilesLinksRecursive(self):
        params = self.dirFiles.request(self._TEST_ROOT_DIR,
                                       self._TEST_FILE_PATTERN,
                                       links=True, recursive=True)
        status, result = self.dirFiles.response(**params)
        self.failUnless(status)
        self.failUnless("files" in result)
        files = result["files"]
        self.failUnlessEqual(len(files), 8)
        for name in ("file3.dat", "file6.dat", "file8.dat", "file11.dat",
                     "file131.dat", "file14.dat", "file54.dat"):
            self.failUnless(self._fileNameMaps[name] in files)
        self.failUnless(os.path.join(self._TEST_ROOT_DIR, "dir7", "file131.dat")
                        in files)
        for fd in files:
            self.failUnlessEqual(fd.mtime, os.path.getmtime(fd.path))
            self.failUnlessEqual(fd.size, os.path.getsize(fd.path))

