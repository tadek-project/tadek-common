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

__all__ = ["searcher", "searcher_back", "searcher__",
           "structure", "structure_back", "structure__"]

class BaseSearcher(object):
    '''
    A base class of searchers. Searcher searches a child widget of
    the given one, which has specified features.
    '''
    #: A search method
    method = None
    #: A default widget class for the searcher class
    defaultwidgetclass = None

    def __init__(self, name=None, description=None, role=None, index=None,
                       count=None, action=None, relation=None, state=None,
                       text=None, nth=0, **attrs):
        '''
        Stores features of searched widget.

        :param name: A name of searched widget, if the name starts with '&'
            character then it means that it is a regular expression
        :type name: string
        :param description: A description of searched widget, if the description
          starts with '&' character then it means that it is a regular expression
        :type description: string
        :param role: A role of the searched widget
        :type role: Role
        :param index: An index of the searched widget in its parent widget
        :type index: integer
        :param count: A number of children of the searched widget
        :type count: integer
        :param action: An action of the searched widget
        :type action: Action
        :param relation: A relation of the searched widget
        :type relation: Relation
        :param state: A state of the searched widget
        :type state: State
        :param text: A text of searched widget, if the text starts with '&'
            character then it means that it is a regular expression
        :type text: string
        :param nth: An index of the searched widget in a list of widgets those
            have all the features specified in the searcher
        :type nth: integer
        :param attrs: Attributes of searched widget
        :type attrs: dictionary
        '''
        if self.method is None:
            raise NotImplementedError
        self._name = name
        self._description = description
        self._role = role
        self._index = index
        self._count = count
        self._action = action
        self._relation = relation
        self._state = state
        self._text = text
        self._attrs = attrs
        self._nth = nth

    def find(self, accessible):
        '''
        Returns a child widget of the specified widget given as accessible
        that has features specified in the searcher.

        :param accessible: The starting point widget as accessible
        :type accessible: tadek.core.accessible.Accessible
        :return: A found child widget as accessible
        :rtype: tadek.core.accessible.Accessible or NoneType
        '''
        device = accessible.device
        path = accessible.path
        return device.searchAccessible(path, self.method, name=self._name,
                                       description=self._description,
                                       role=self._role, index=self._index,
                                       count=self._count, action=self._action,
                                       relation=self._relation, text=self._text,
                                       state=self._state, nth=self._nth,
                                       **self._attrs)


class searcher(BaseSearcher):
    '''
    A class of general searchers. Searcher can find any widget that has
    specified features in children of a given parent widget.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_SIMPLE


class searcher_back(BaseSearcher):
    '''
    A class of general backward searchers. Backward searcher can find any widget
    that has specified features in children of a given parent widget starting
    from the last child widget.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_BACKWARDS


class searcher__(BaseSearcher):
    '''
    A class of general deep searchers. A deep searcher can find any widget that
    has specified features in all descendants of a given parent widget,
    searching level by level.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_DEEP


class structure(BaseSearcher):
    '''
    A class of structure searchers. A structure searcher searches in children
    of a given parent widget a widget of specified features that is a root
    widget of a structure of widgets defined by a given list of searchers.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_SIMPLE

    def __init__(self, name=None, description=None, role=None, index=None,
                       count=None, action=None, relation=None, state=None,
                       text=None, nth=0, searchers=(), **attrs):
        '''
        Stores features of searched widget.

        :param name: A name of searched widget, if the name starts with '&'
            character then it means that it is a regular expression
        :type name: string
        :param description: A description of searched widget, if the description
          starts with '&' character then it means that it is a regular expression
        :type description: string
        :param role: A role of the searched widget
        :type role: Role
        :param index: An index of the searched widget in its parent widget
        :type index: integer
        :param count: A number of children of the searched widget
        :type count: integer
        :param action: An action of the searched widget
        :type action: Action
        :param relation: A relation of the searched widget
        :type relation: Relation
        :param state: A state of the searched widget
        :type state: State
        :param text: A text of searched widget, if the text starts with '&'
            character then it means that it is a regular expression
        :type text: string
        :param nth: An index of the searched widget in a list of widgets those
            have all the features specified in the searcher
        :type nth: integer
        :param searchers: A list of searchers that defines the structure
        :type searchers: tuple
        :param attrs: Attributes of searched widget
        :type attrs: dictionary
        '''
        BaseSearcher.__init__(self, name=name, description=description,
                             role=role, index=index, count=count, action=action,
                             relation=relation, state=state, text=text, **attrs)
        self._istruct = nth
        for s in searchers:
            if not isinstance(s, BaseSearcher):
                raise TypeError
        self._searchers = searchers

    def find(self, accessible):
        '''
        Returns a root widget of the defined structure of widgets that has
        features specified in the searcher.

        :param accessible: The starting widget as accessible
        :type accessible: tadek.core.accessible.Accessible
        :return: A found root widget of the structure as accessible
        :rtype: tadek.core.accessible.Accessible or NoneType
        '''
        i = self._nth = 0
        struct = BaseSearcher.find(self, accessible)
        while struct:
            found = True
            for s in self._searchers:
                if s.find(struct) is None:
                    found = False
                    break
            if found:
                i += 1
                if self._istruct < i:
                    return struct
            self._nth += 1
            struct = BaseSearcher.find(self, accessible)
        return None


class structure_back(structure):
    '''
    A class of backward structure searchers. A backward structure searcher
    searches in children of a given parent widget starting from a last widget
    of specified features that is a root widget of a structure of widgets
    defined by a given list of searchers.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_BACKWARDS


class structure__(structure):
    '''
    A class of deep structure searchers. A deep structure searcher searches
    in all descendants of a given parent widget a widget of specified features
    that is a root widget of a structure of widgets defined by a given list of
    searchers.
    '''
    #: A search method
    method = protocol.MHD_SEARCH_DEEP


def roleSearcher(name, role):
    '''
    Creates new role searcher and deep role searcher (with suffix: `__`)
    classes of the given name and the specified role.

    :param name: A base name of role searchers: `name`, `name__` (for the deep
        one)
    :type name: string
    :param role: A role of searched widgets for those searchers are created
    :type role: Role
    '''
    def makedict(role):
        '''
        Defines a dictionary containing the role and '__init__' method for new
        created role searcher class.
        '''
        def __init__(self, name=None, description=None, index=None, count=None,
                           action=None, relation=None, state=None, text=None,
                           nth=0, **attrs):
            searcher.__init__(self, name=name, description=description,
                                    role=role, index=index, count=count,
                                    action=action, relation=relation,
                                    state=state, text=text, nth=nth, **attrs)
        return locals()
    def makedict__(role):
        '''
        Defines a dictionary containing the role and '__init__' method for new
        created deep role searcher class.
        '''
        def __init__(self, name=None, description=None, index=None, count=None,
                           action=None, relation=None, state=None, text=None,
                           nth=0, **attrs):
            searcher__.__init__(self, name=name, description=description,
                                      role=role, index=index, count=count,
                                      action=action, relation=relation,
                                      state=state, text=text, nth=nth, **attrs)
        return locals()
    globals()[name] = type(name, (searcher,), makedict(role))
    __all__.append(name)
    globals()[name + "__"] = type(name + "__", (searcher__,), makedict__(role))
    __all__.append(name + "__")

roleSearcher("alert", "ALERT")
roleSearcher("application", "APPLICATION")
roleSearcher("button", "BUTTON")
roleSearcher("checkbox", "CHECK_BOX")
roleSearcher("checkmenuitem", "CHECK_MENU_ITEM")
roleSearcher("combobox", "COMBO_BOX")
roleSearcher("dialog", "DIALOG")
roleSearcher("documentframe", "DOCUMENT_FRAME")
roleSearcher("drawingarea", "DRAWING_AREA")
roleSearcher("entry", "ENTRY")
roleSearcher("filler", "FILLER")
roleSearcher("form", "FORM")
roleSearcher("frame", "FRAME")
roleSearcher("heading", "HEADING")
roleSearcher("icon", "ICON")
roleSearcher("image", "IMAGE")
roleSearcher("label", "LABEL")
roleSearcher("link", "LINK")
roleSearcher("list", "LIST")
roleSearcher("listitem", "LIST_ITEM")
roleSearcher("menu", "MENU")
roleSearcher("menubar", "MENU_BAR")
roleSearcher("menuitem", "MENU_ITEM")
roleSearcher("pagetab", "PAGE_TAB")
roleSearcher("pagetablist", "PAGE_TAB_LIST")
roleSearcher("panel", "PANEL")
roleSearcher("paragraph", "PARAGRAPH")
roleSearcher("passwordtext", "PASSWORD_TEXT")
roleSearcher("popupmenu", "POPUP_MENU")
roleSearcher("progressbar", "PROGRESS_BAR")
roleSearcher("radiobutton", "RADIO_BUTTON")
roleSearcher("radiomenuitem", "RADIO_MENU_ITEM")
roleSearcher("scrollbar", "SCROLL_BAR")
roleSearcher("scrollpane", "SCROLL_PANE")
roleSearcher("section", "SECTION")
roleSearcher("separator", "SEPARATOR")
roleSearcher("slider", "SLIDER")
roleSearcher("spinbutton", "SPIN_BUTTON")
roleSearcher("splitpane", "SPLIT_PANE")
roleSearcher("statusbar", "STATUS_BAR")
roleSearcher("table", "TABLE")
roleSearcher("tablecell", "TABLE_CELL")
roleSearcher("tablecolumnheader", "TABLE_COLUMN_HEADER")
roleSearcher("text", "TEXT")
roleSearcher("togglebutton", "TOGGLE_BUTTON")
roleSearcher("toolbar", "TOOL_BAR")
roleSearcher("tree", "TREE")
roleSearcher("treetable", "TREE_TABLE")
roleSearcher("unknown", "UNKNOWN")
roleSearcher("viewport", "VIEWPORT")
roleSearcher("window", "WINDOW")

