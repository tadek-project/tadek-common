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
import gettext as gt

from tadek.core import config
from tadek.core import constants
from tadek.core import utils

__all__ = ["gettext", "gettext__", "ngettext", "ngettext__", "escape"]

def add(path):
    '''
    Adds the given path locale.
    '''
    if os.path.isdir(path) and path not in _cache:
        _cache[path] = {}

def remove(path):
    '''
    Removes the given path locale.
    '''
    if path in _cache:
        del _cache[path]

def reset():
    '''
    Resets all cached translations.
    '''
    paths = _cache.keys()
    _cache.clear()
    for path in paths:
        add(path)
    _default.clear()


# TODO: Add support for any domain (*.mo)

# A default locale path
_DEFAULT_PATH = os.path.join(config.DATA_DIR, "locale")

# A translations caches
_cache = {}
_default = {}

def _language(path, mofile):
    '''
    Gets a language symbol from the .mo file path.
    '''
    lang = None
    while mofile != path or not mofile:
        mofile, lang = os.path.split(mofile)
    return lang

def _translation(path, lang, cache=None):
    '''
    Gets a translation for the given language from the locale path.
    '''
    if cache is None:
        cache = _cache[path]
    trans = cache.get(lang)
    if trans:
        return trans
    mofiles = gt.find(config.NAME, path, [lang], True)
    for mofile in mofiles:
        lg = _language(path, mofile)
        tn = cache.get(lg)
        if tn is None:
            tn = cache.setdefault(lg, gt.GNUTranslations(open(mofile, 'rb')))
            tn.set_output_charset(constants.ENCODING)
        if trans:
            trans.add_fallback(tn)
        else:
            trans = tn
    if trans is None:
        trans = gt.NullTranslations()
    return cache.setdefault(lang, trans)

def _translations(device):
    '''
    An iterator that yields one translation for the given device per iteration.
    '''
    lang = device.locale
    if lang and lang.upper() != 'C':
        for path in _cache:
            yield _translation(path, lang)
        if os.path.isdir(_DEFAULT_PATH):
            yield _translation(_DEFAULT_PATH, lang, _default)

def _nmessage(singular, plural, n):
    '''
    Returns the given singular or plural message depending on the n value.
    '''
    return singular if n == 1 else plural


def gettext(message, device):
    '''
    Gets a translation for the given message using locale of the device.
    '''
    if isinstance(message, MessageProxy):
        return message(device)
    for trans in _translations(device):
        tmsg = trans.ugettext(message)
        if tmsg != message:
            return tmsg
    return message

def gettext__(message):
    '''
    Gets a lazy translation for the given message.
    '''
    return LazyTranslation(message)

def ngettext(singular, plural, n, device):
    '''
    Gets a translation for the given singular message if n is equals to 1,
    otherwise for the specified plural message using locale of the device.
    '''
    for trans in _translations(device):
        tmsg = trans.ungettext(singular, plural, n)
        if tmsg not in (singular, plural):
            return tmsg
    return _nmessage(singular, plural, n)

def ngettext__(singular, plural, n):
    '''
    Gets a lazy translation for the given singular message if n is equals to 1,
    otherwise for the specified plural message.
    '''
    return LazyNTranslation(singular, plural, n)

def escape(message, device):
    '''
    Escapes the given lazy translated message if needed.
    '''
    return message(device) if isinstance(message, MessageProxy) else message


class MessageProxy(object):
    '''
    A simple base class for proxy messages.
    '''
    def __init__(self, message):
        self.message = message

    def __str__(self):
        '''
        Returns the string representation of a proxied message.
        '''
        return self.message

    def __repr__(self):
        '''
        Returns the canonical string representation of a proxied message.
        '''
        return repr(self.message)

    def __call__(self, device):
        '''
        Returns a proxied message.
        '''
        return utils.decode(self.message)

    def __add__(self, message):
        '''
        Returns a sum of these two messages.
        '''
        if isinstance(message, basestring):
            message = MessageProxy(message)
        return MessageSum(self, message)

    def __radd__(self, message):
        '''
        Returns a sum of these two messages.
        '''
        if isinstance(message, basestring):
            message = MessageProxy(message)
        return MessageSum(message, self)


class LazyTranslation(MessageProxy):
    '''
    A simple proxy class for making lazy message translations.
    '''
    def __call__(self, device):
        '''
        Translates a corresponding message using the given device.
        '''
        return gettext(self.message, device)


class LazyNTranslation(MessageProxy):
    '''
    A simple proxy class for making lazy message translations.
    '''
    def __init__(self, singular, plural, n):
        MessageProxy.__init__(self, _nmessage(singular, plural, n))
        self.singular = singular
        self.plural = plural
        self.n = n

    def __call__(self, device):
        '''
        Translates a corresponding message using the given device.
        '''
        return ngettext(self.singular, self.plural, self.n, device)


class MessageSum(MessageProxy):
    '''
    A simple class for proxying sum of two messages.
    '''
    def __init__(self, msg1, msg2):
        MessageProxy.__init__(self, (msg1, msg2))

    def __str__(self):
        '''
        Returns the string representation of a proxied message sum.
        '''
        return ''.join([str(msg) for msg in self.message])

    def __repr__(self):
        '''
        Returns the canonical string representation of a proxied message sum.
        '''
        return repr(''.join([str(msg) for msg in self.message]))

    def __call__(self, device):
        '''
        Returns a sum of contained message pair.
        '''
        return ''.join([msg(device) for msg in self.message])

