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
import time
from datetime import datetime
import xml.etree.cElementTree as etree

import constants
import config

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
DATE_TIME_SEPARATOR = ' '

def encode(data, encoding=None):
    '''
    Encodes the given data using the given encoding.

    :param data: Data to encode
    :type data: string or unicode
    :param encoding: An encoding name
    :type encoding: string
    :return: Encoded data
    :rtype: string
    '''
    encoding = encoding or constants.ENCODING
    if isinstance(data, buffer):
        data = data[:]
    if isinstance(data, unicode):
        return data.encode(encoding, "ignore")
    return str(data)

def decode(data, encoding=None):
    '''
    Decodes the given data using the given encoding.

    :param data: Data to decode
    :type data: string or unicode
    :param encoding: An encoding name
    :type encoding: string
    :return: Decoded data
    :rtype: unicode
    '''
    encoding = encoding or constants.ENCODING
    if isinstance(data, buffer):
        data = data[:]
    if isinstance(data, str):
        return data.decode(encoding, "ignore")
    return unicode(data)

def localTime(stamp=None):
    '''
    Gets a local date in format 'YYYY-MM-DD' and local time in format 'hh:mm:ss'
    according to the given utime. If utime is not given then a current local
    date and time is returned.

    :param stamp: A time stamp or None
    :type stamp: float
    :return: A local date and time
    :rtype: tuple
    '''
    dt = datetime.fromtimestamp(stamp) if stamp else datetime.now()
    return dt.strftime(DATE_FORMAT), dt.strftime(TIME_FORMAT)

def uniqueFile(name):
    '''
    Returns an unique file name basing on the given file name in format:
    name_YYYYMMDD_hhmmss.ext.

    :param name: A base file name
    :type name: string
    :return: An unique file name
    :rtype: string
    '''
    date, time = localTime()
    name, ext = os.path.splitext(name)
    return ''.join([name,
                    '_', date.replace('-', ''),
                    '_', time.replace(':', ''),
                    ext])

def runTimeToString(runTime):
    '''
    Returns string representing run time in human readable format.

    :param runTime: Amount of seconds
    :type runTime: float
    :return: String containing time
    :rtype: string
    '''
    parts = []
    for unit, suffix in zip((3600, 60), ('h', 'm')):
        n = runTime // unit
        if n > 0:
            parts.append("%d%s" % (n, suffix))
            runTime %= unit
    if runTime > 0 or not parts:
        parts.append("%.2fs" % runTime)
    return ' '.join(parts)

def timeToString(dt):
    '''
    Returns string from time or datetime object.
    If object is None, function returns empty string.

    :param dt: Time object to convert
    :type dt: datetime.datetime
    :return: String containing time
    :rtype: string
    '''
    if dt is None:
        return ''
    return dt.strftime(DATE_TIME_SEPARATOR.join((DATE_FORMAT, TIME_FORMAT)))

def timeStampFromString(timeStr):
    '''
    Returns time stamp from string.
    If input is empty, returns None.
    
    :param timeStr: Time string to convert
    :type timeStr: String
    :return: Time stamp or None
    :rtype: float or None
    '''
    if not timeStr:
        return None
    dt = timeFromString(timeStr)
    return time.mktime(dt.timetuple()) + dt.microsecond / 1000000.0

def timeFromString(timeStr):
    '''
    Returns datetime object from string.
    If input is empty, returns None.

    :param timeStr: Time string to convert
    :type timeStr: string
    :return: Time object or None
    :rtype: datetime.datetime or None
    '''
    if not timeStr:
        return None
    return datetime.strptime(timeStr, DATE_TIME_SEPARATOR.join(
                                                (DATE_FORMAT, TIME_FORMAT)))

def sizeToString(size):
    '''
    Returns a human readable representation of a given size in bytes.
    If size is None, function returns empty string.

    :param size: Size in bytes to convert
    :type size: integer or long
    :return: String containing size
    :rtype: string
    '''
    if size is None:
        return ''
    size = float(size)
    val = 0
    for suffix in ('B', "KB", "MB", "GB"):
        val = str(int(size)) if suffix == "B" else "%0.2f" % size
        if size < 1024:
            break
        size /= 1024
    return ''.join((val, suffix))

def saveXml(element, file, encoding=constants.ENCODING,
            xslt=None, dtd=None, pretty=True):
    '''
    Saves to the specified file an XML document given as root element of
    element tree in the human-readable (pretty) format:
    <root>
        <child>
            <text>Text</text>
            ...
        </child>
        ...
    </root>

    :param element: A root element to write
    :type element: Element
    :param file: A target file name or a target file descriptor
    :type file: string or file
    :param pretty: If True, saves the given element tree in the pretty format
    :type pretty: boolean
    :param encoding: An encoding name of the XML document
    :type encoding: string
    '''
    if pretty:
        # Add indentations
        _indent(element)
    close = False
    tree = etree.ElementTree(element)
    if not hasattr(file, "write"):
        file = open(file, "wb")
        close = True
    try:
        file.write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        if xslt:
            file.write("<?xml-stylesheet type='text/xml' href='%s'?>\n" % xslt)
        if dtd:
            file.write("<!DOCTYPE TESTCASES SYSTEM '%s'>\n" % dtd)
        tree.write(file, encoding)
    finally:
        if close:
            file.close()

_TAG_LEVEL = 4*' '

def _indent(element, previous=None, level=0):
    '''
    Adds indentations to the given element according to its level and content.
    '''
    element.tail = '\n'
    if previous is not None:
        previous.tail = "\n%s" % (level * _TAG_LEVEL)
    if len(element):
        if element.text is None:
            element.text = "\n%s" % ((level +1) * _TAG_LEVEL)
        previous = None
        for subelement in element:
            _indent(subelement, previous, level+1)
            previous = subelement
        subelement.tail = "\n%s" % (level * _TAG_LEVEL)

def getDataPath(subdir, filename):
    '''
    Gets an absolute path do the given data file.

    :param subdir: A name of a data subdirectory
    :type subdir: string
    :param filename: A name of a data file
    :type filename: string
    :return: An absolute path to a data file
    :rtype: string
    '''
    return os.path.join(config.DATA_DIR, subdir, filename)

def ensureUserDir(dirname):
    '''
    Ensures the given user directory exists.

    :param dirname: A name of the user directory
    :type dirname: string
    '''
    userdir = os.path.join(config.USER_DIR, dirname)
    if not os.path.exists(userdir):
        try:
            os.makedirs(userdir, mode=0755)
        except IOError:
            return None
    return userdir

# Module support
_modulePattern = re.compile("^([a-z][a-z0-9_]*)(\.(py|pyc|pyo|pyd|o))?$")

def packageModules(package):
    '''
    Gets a list of all available modules in the given package.
    '''
    modules = []
    for dir in package.__path__:
        for file in os.listdir(dir):
            match = _modulePattern.match(file)
            if match is None:
                continue
            module = '.'.join([package.__name__, match.group(1)])
            if module not in modules:
                modules.append(module)
    return modules

def importModule(name):
    '''
    Imports a module of the given name.
    '''
    try:
        __import__(name)
    except ImportError:
        return False
    return True

