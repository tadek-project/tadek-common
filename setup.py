#!/usr/bin/env python

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
from glob import glob
from subprocess import check_call
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.command.install import install as _install
from distutils.core import Distribution as _Distribution
from distutils.core import setup
from distutils.dir_util import remove_tree
from distutils import log

from tadek.core.config import CONF_DIR, DATA_DIR, DOC_DIR, VERSION

HTML_DOC_DIR = os.path.join(DOC_DIR, "api", "html")

DATA_FILES = []

PACKAGES = []

BUILD_OUTPUT_DIR = os.path.join('build', 'html')

class Distribution(_Distribution):
    _Distribution.global_options.extend([
        ("skip-doc", None,
         "don't build and install API documentation"),
        ("only-doc", None,
         "build and install only API documentation"),
        ])

    def __init__(self, attrs=None):
        self.skip_doc = 0
        self.only_doc = 0
        _Distribution.__init__(self, attrs)

class build(_build):
    def run(self):
        if not self.distribution.only_doc:
            DATA_FILES.extend([
                (os.path.join(CONF_DIR, "common"),
                    glob(os.path.join("data", "config", "common", "*"))),
                (os.path.join(DATA_DIR, "locale"),
                    glob(os.path.join("data", "locale", "*"))),
            ])
            PACKAGES.extend(["tadek",
                "tadek.connection",
                "tadek.connection.protocol",
                "tadek.core",
                "tadek.engine",
                "tadek.engine.channels",
                "tadek.models",
                "tadek.teststeps",
                "tadek.testcases",
                  "tadek.testsuites"
                ])
        _build.run(self)
        if not self.distribution.skip_doc and not os.path.exists(BUILD_OUTPUT_DIR):
            os.makedirs(BUILD_OUTPUT_DIR)
            EPYDOC = ['epydoc',
                '--html', '--docformat=reStructuredText',
                '--inheritance=grouped',
                '--no-private',
                '--show-imports',
                '--redundant-details',
                '--graph=umlclasstree',
                '--css='+os.path.join('doc', 'tadek.css'),
                '--output='+BUILD_OUTPUT_DIR,
                '--no-sourcecode',
                'tadek']
            check_call(EPYDOC)

class install(_install):
    def run(self):
        if not self.distribution.skip_doc:
            DATA_FILES.append((HTML_DOC_DIR, glob(os.path.join("build", "html", "*"))))
        _install.run(self)

class clean(_clean):
    def run(self):
        if self.all:
            if os.path.exists(BUILD_OUTPUT_DIR):
                remove_tree(BUILD_OUTPUT_DIR, dry_run=self.dry_run)
            else:
                log.warn("'%s' does not exist -- can't clean it",
                    BUILD_OUTPUT_DIR)
        _clean.run(self)

setup(
    distclass=Distribution,
    cmdclass={'build': build, 'install': install, 'clean': clean},
    name="tadek-common",
    version=VERSION,
    packages=PACKAGES,
    data_files=DATA_FILES,
)
