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

import re

from tadek.core import accessible
from tadek.core import childiters
from tadek.core.locale import escape
from tadek.core.utils import decode

import delay
import path
import searchers

__all__ = ["Widget", "App", "Dialog", "Button", "Menu", "PopupMenu", "MenuItem",
           "Entry", "Valuator", "Link", "Container"]

class Widget(path.Object):
    '''
    A base class for representing any UI elements (widgets) in TADEK, especially
    those widgets that do not have any special features.
    '''

    class _Func(object):
        '''
        A class to perform a specified function for a given widget with
        specified arguments.
        '''
        def __init__(self, func, *args):
            self.func = func
            self.args = args

        def __call__(self):
            '''
            Performs the given function for the widget with specified arguments.
            '''
            return self.func(*self.args)

    class _WidgetState(_Func):
        '''
        A class to check if a given widget is in a specified state.
        '''
        def __init__(self, accessible, state):
            Widget._Func.__init__(self, self.check, accessible, state)

        def check(self, accessible, state):
            accessible = accessible.device.getAccessible(accessible.path,
                                                         states=True)
            return accessible and state in accessible.states

    class _WidgetAction(_Func):
        '''
        A class to perform a specified action on a given widget.
        '''
        def __init__(self, accessible, action):
            Widget._Func.__init__(self, accessible.do, action)

    class _WidgetText(_Func):
        '''
        A class to check if a given widget contains a specified text.
        '''
        def __init__(self, accessible, text):
            Widget._Func.__init__(self, self.check, accessible, text)

        def check(self, accessible, text):
            accessible = accessible.device.getAccessible(accessible.path,
                                                         text=True)
            if accessible is None or accessible.text is None:
                return False
            if isinstance(text, basestring) and text and text[0] == '&':
                match = re.compile(text[1:], re.DOTALL).match(accessible.text)
                return bool(match) and match.span() == (0, len(text))
            return accessible.text == text

    def addPath(self, *path):
        '''
        Returns a new instance of Widget class representing a child widget of
        the base widget, pointed by the given relative path of searchers.

        :param path: A relative path to the child widget given as a list
            of searchers
        :type path: tuple
        :return: A new widget
        :rtype: Widget
        '''
        return Widget(self, *path)

    def getWidget(self, device, delay=None, expectedFailure=False):
        '''
        Gets a widget represented by the current Widget instance.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param delay: A delay instance used in getting the widget
        :type delay: delay.Delay
        :param expectedFailure: If True, the widget is not expected to be found
        :type expectedFailure: boolean
        :return: The represented widget
        :rtype: widget class or NoneType
        '''
        return self.getPath()(device, delay, expectedFailure)

    def getImmediate(self, device):
        '''
        Gets immediate (without waiting) the represented widget or returns None.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: The represented widget
        :rtype: widget class or NoneType
        '''
        return self.getPath()(device, delay.immediate, True)

    def getIndex(self, device):
        '''
        Gets an index in parent of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Index of the represented widget
        :rtype: integer
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.index

    def getName(self, device):
        '''
        Gets a name of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A name of the widget
        :rtype: string
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.name

    def getDescription(self, device):
        '''
        Gets a description of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A description of the widget
        :rtype: string
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.description

    def getRoleName(self, device):
        '''
        Gets a role name of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A role name of the widget
        :rtype: string
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.role

    def getPosition(self, device):
        '''
        Gets a position of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A position of the widget as (x, y)
        :rtype: tuple
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.position

    def getSize(self, device):
        '''
        Gets a size of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A size of the widget as (width, height)
        :rtype: tuple
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.size

    def getAttribute(self, device, attribute=None):
        '''
        Gets a value of the given attribute of the represented widget. If no
        attribute is given then a dictionary containing names and values of
        all attributes is returned.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param attribute: An attribute to return value
        :type attribute: string
        :return: A value of the specified attribute
        :rtype: string or dictionary
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        if attribute is None:
            return widget.attributes or None
        return widget.attributes.get(attribute, None)

    def getText(self, device):
        '''
        Gets text contained in the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: The contained text
        :rtype: string
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        return widget.text

    def hasText(self, device, text, expectedFailure=False):
        '''
        Checks if the represented widget contains the specified text.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param text: Text to find in the widget
        :type text: string
        :param expectedFailure: It specifies if the widget is not expected to
            contain the text
        :type expectedFailure: boolean
        :return: True if the widget contains the text, False otherwise
        :rtype: boolean
        '''
        widget = self.getWidget(device)
        if widget is None:
            return False
        # Finalize translation and decode string
        text = decode(escape(text, device))
        return delay.text(self._WidgetText(widget, text), expectedFailure)

    def isExisting(self, device, expectedFailure=False):
        '''
        Checks if the represented widget exists.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: If True, the widget is not expected to be found
        :type expectedFailure: boolean
        :return: True if the widget exists, False otherwise
        :rtype: boolean
        '''
        return self.getWidget(device,
                              expectedFailure=expectedFailure) is not None

    def inState(self, device, state, expectedFailure):
        '''
        Checks if the represented widget is in the specified state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param state: The widget state
        :type state: string
        :param expectedFailure: It specifies if the widget is not expected to be
            in the state
        :type expectedFailure: boolean
        :return: True if the widget is in the state, False otherwise
        :rtype: boolean
        '''
        widget = self.getWidget(device)
        if widget is None:
            return False
        return delay.state(self._WidgetState(widget, state), expectedFailure)

    def isActive(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'active' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'active' state
        :type expectedFailure: boolean
        :return: True if the widget is active, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "ACTIVE", expectedFailure)

    def isChecked(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'checked' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'checked' state
        :type expectedFailure: boolean
        :return: True if the widget is checked, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "CHECKED", expectedFailure)

    def isCollapsed(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'collapsed' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'collapsed' state
        :type expectedFailure: boolean
        :return: True if the widget is collapsed, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "COLLAPSED", expectedFailure)

    def isEditable(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'editable' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'editable' state
        :type expectedFailure: boolean
        :return: True if the widget is editable, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "EDITABLE", expectedFailure)

    def isEnabled(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'enabled' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'enabled' state
        :type expectedFailure: boolean
        :return: True if the widget is enabled, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "ENABLED", expectedFailure)

    def isExpandable(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'expandable' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'expandable' state
        :type expectedFailure: boolean
        :return: True if the widget is expandable, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "EXPANDABLE", expectedFailure)

    def isExpanded(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'expanded' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'expanded' state
        :type expectedFailure: boolean
        :return: True if the widget is expanded, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "EXPANDED", expectedFailure)

    def isFocusable(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'focusable' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'focusable' state
        :type expectedFailure: boolean
        :return: True if the widget is focusable, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "FOCUSABLE", expectedFailure)

    def isFocused(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'focused' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'focused' state
        :type expectedFailure: boolean
        :return: True if the widget is focused, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "FOCUSED", expectedFailure)

    def isMultiselectable(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'multiselectable' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'multiselectable' state
        :type expectedFailure: boolean
        :return: True if the widget is multiselectable, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "MULTISELECTABLE", expectedFailure)

    def isMultiline(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'multiline' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'multiline' state
        :type expectedFailure: boolean
        :return: True if the widget is multiline, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "MULTILINE", expectedFailure)

    def isSelectable(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'selectable' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'selectable' state
        :type expectedFailure: boolean
        :return: True if the widget is selectable, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "SELECTABLE", expectedFailure)

    def isSelected(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'selected' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'selected' state
        :type expectedFailure: boolean
        :return: True if the widget is selected, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "SELECTED", expectedFailure)

    def isSensitive(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'sensitive' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'sensitive' state
        :type expectedFailure: boolean
        :return: True if the widget is sensitive, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "SENSITIVE", expectedFailure)

    def isShowing(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'showing' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'showing' state
        :type expectedFailure: boolean
        :return: True if the widget is showing, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "SHOWING", expectedFailure)

    def isVisible(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'visible' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'visible' state
        :type expectedFailure: boolean
        :return: True if the widget is visible, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "VISIBLE", expectedFailure)

    def isVisited(self, device, expectedFailure=False):
        '''
        Checks if the represented widget is in 'visited' state.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param expectedFailure: It specifies if the widget is not expected to be
            in the 'visited' state
        :type expectedFailure: boolean
        :return: True if the widget is visited, False otherwise
        :rtype: boolean
        '''
        return self.inState(device, "VISITED", expectedFailure)

    def doAction(self, device, action):
        '''
        Performs the given action on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param action: The action to perform
        :type action: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        widget = self.getWidget(device)
        if widget is None:
            return False
        res = delay.action(self._WidgetAction(widget, action))
        if res:
            delay.action.wait()
        return res

    def grabFocus(self, device):
        '''
        Grabs focus for the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "FOCUS")

    def getCenterPoint(self, device):
        '''
        Gets a center point of the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A center point of the widget as (x, y)
        :rtype: tuple
        '''
        widget = self.getWidget(device)
        if widget is None:
            return None
        position = widget.position
        if position is None:
            return None
        size = widget.size
        if size is None:
            return None
        return (position[0]+size[0]//2, position[1]+size[1]//2)

    def mouseClick(self, device, button="LEFT", offset=(0, 0)):
        '''
        Generates a mouse click event on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param button: A mouse button generating the event
        :type button: string
        :param offset: An offset of the widget center point
        :type offset: tuple
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        cp = self.getCenterPoint(device)
        if cp is None:
            return False
        x, y = cp[0] + offset[0], cp[1] + offset[1]
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, event="CLICK")

    def mouseDoubleClick(self, device, button="LEFT", offset=(0, 0)):
        '''
        Generates a mouse double-click event on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param button: A mouse button generating the event
        :type button: string
        :param offset: An offset of the widget center point
        :type offset: tuple
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        cp = self.getCenterPoint(device)
        if cp is None:
            return False
        x, y = cp[0] + offset[0], cp[1] + offset[1]
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, event="DOUBLE_CLICK")

    def mousePress(self, device, button="LEFT", offset=(0, 0)):
        '''
        Generates a mouse press event on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param button: A mouse button generating the event
        :type button: string
        :param offset: An offset of the widget center point
        :type offset: tuple
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        cp = self.getCenterPoint(device)
        if cp is None:
            return False
        x, y = cp[0] + offset[0], cp[1] + offset[1]
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, event="PRESS")

    def mouseRelease(self, device, button="LEFT", offset=(0, 0)):
        '''
        Generates a mouse release event on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param button: A mouse button generating the event
        :type button: string
        :param offset: An offset of the widget center point
        :type offset: tuple
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        cp = self.getCenterPoint(device)
        if cp is None:
            return False
        x, y = cp[0] + offset[0], cp[1] + offset[1]
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, event="RELEASE")

    def mouseDrag(self, device, dest, button="LEFT", offset=(0, 0)):
        '''
        Generates a mouse drag and drop event on the represented widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param dest: A destination point of the event, could be a Widget
            instance or coordinates (x, y)
        :type dest: Widget, tuple, list
        :param button: A mouse button generating the event
        :type button: string
        :param offset: An offset of the widget center point
        :type offset: tuple
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        cp = self.getCenterPoint(device)
        if cp is None:
            return False
        if isinstance(dest, Widget):
            dest = dest.getCenterPoint()
        elif not isinstance(dest, (list, tuple)):
            dest = None
        if dest is None:
            return False
        x, y = cp[0] + offset[0], cp[1] + offset[1]
        if (not device.mouseEvent(accessible.Path(0), x, y,
                                  button, event="PRESS")):
            return False
        x, y = dest[0] + offset[0], dest[1] + offset[1]
        if (not device.mouseEvent(accessible.Path(0), x, y,
                                  button, event="ABSOLUTE_MOTION")):
            return False
        return device.mouseEvent(accessible.Path(0), x, y,
                                 button, event="RELEASE")


class App(Widget):
    '''
    A class to represent widgets that are applications.
    '''
    def __init__(self, execname, *path):
        '''
        Stores an execution name of the represented application.

        :param execname: An execution name of the application
        :type execname: string
        :param path: A path to the represented widget given as a list
            of searchers
        :type path: tuple
        '''
        Widget.__init__(self, *path)
        self.execname = execname

    def launch(self, device):
        '''
        Launches the represented application.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if successful, False otherwise
        :rtype: boolean
        '''
        return device.systemExec(self.execname, wait=False)[0]

    def kill(self, device):
        '''
        Kills the represented application.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if successful, False otherwise
        :rtype: boolean
        '''
        if self.getWidget(device, delay.slow, True) is not None:
            psOut = device.systemExec("ps ax | grep '%s'" % self.execname)[1]
            matches = re.findall("[0-9]{2,7}", psOut)
            if len(matches):
                pid = matches[0]
                killErr = device.systemExec("kill -9 %s" % pid)[2]
                if not len(killErr):
                    return True
        return False

    def isOpen(self, device):
        '''
        Checks if the represented application is open.
        Opening an application is potentially time consuming so a long delay
        is used here.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if the application is open, False otherwise
        :rtype: boolean
        '''
        res = (self.getWidget(device, 4*delay.default) is not None)
        if res:
            # Wait for initialization of the application
            (2*delay.initial).wait()
        return res

    def isClosed(self, device):
        '''
        Checks if the represented application is closed.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if the application is closed, False otherwise
        :rtype: boolean
        '''
        res = (self.getWidget(device, expectedFailure=True) is None)
        if res:
            # To be sure that next operation can be performed
            delay.initial.wait()
        return res


class Dialog(Widget):
    '''
    A class to represent widgets which are dialogs or alerts.
    '''
    def isOpen(self, device):
        '''
        Checks if the represented dialog is open.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if the dialog is open, False otherwise
        :rtype: boolean
        '''
        res = (self.getWidget(device) is not None)
        if res:
            # Wait for initialization of the dialog
            delay.initial.wait()
        return res

    def isClosed(self, device):
        '''
        Checks if the represented dialog is closed.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if the dialog is closed, False otherwise
        :rtype: boolean
        '''
        res = (self.getWidget(device, expectedFailure=True) is None)
        if res:
            # To be sure that next operation can be performed
            delay.initial.wait()
        return res


class Button(Widget):
    '''
    A class to represent widgets that are buttons.
    '''
    def click(self, device):
        '''
        Performs a 'click' action on the represented button.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "CLICK")

    def press(self, device):
        '''
        Performs a 'press' action on the represented button.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "PRESS")

    def release(self, device):
        '''
        Performs a 'release' action on the represented button.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "RELEASE")


class Menu(Widget):
    '''
    A class to represent widgets that are menus.
    '''
    def click(self, device):
        '''
        Performs a 'click' action on the represented menu.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "CLICK")


class PopupMenu(Widget):
    '''
    A class to represent widgets that are popup menus.
    '''
    def popup(self, device, widget):
        '''
        Pops up the represented menu for the given widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param widget: A widget to pop up the menu for
        :type widget: Widget
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        if not isinstance(widget, Widget):
            raise TypeError
        widget.mousePress(device)
        res = self.isShowing(device)
        if res:
            # Wait for displaying
            delay.action.wait()
        widget.mouseRelease(device)
        return res


class MenuItem(Widget):
    '''
    A class to represent widgets that are menu items.
    '''
    def click(self, device):
        '''
        Performs a 'click' action on the represented menu item.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "CLICK")


class Entry(Widget):
    '''
    A class to represent widgets that contain editable text.
    '''
    def type(self, device, text):
        '''
        Types new text into the represented editable widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param text: Text to type into the widget
        :type text: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        widget = self.getWidget(device)
        if widget is None:
            return False
        widget.text = text
        if widget.text == text:
            # Wait for updating the widget
            delay.action.wait()
            return True
        return False


class Valuator(Widget):
    '''
    A class to represent widgets that contain changeable values.
    '''
    def getValue(self, device):
        '''
        Gets current value of the represented valuator widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: Current value of the represented widget
        :rtype: float
        '''
        widget = self.getWidget(device)
        if widget is not None:
            return widget.value
        return None

    def setValue(self, device, value):
        '''
        Sets new value of the represented valuator widget.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param value: New value for the represented widget
        :type value: float
        '''
        widget = self.getWidget(device)
        if widget is None:
            return
        widget.value = value


class Link(Widget):
    '''
    A class to represent widgets that are links.
    '''
    def jump(self, device):
        '''
        Performs a 'jump' action on the represented link.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        return self.doAction(device, "JUMP")


class Container(Widget):
    '''
    A base class for widgets that are containers - they can contain other
    widgets.
    '''
    #: A pattern of names of children (all children with non-empty name)
    pattern_of_children = ".+"

    #: A Widget class of container children
    class_of_children = Widget

    #: A searcher class of container children
    searcher_of_children = searchers.searcher__

    #: A state of a 'current' child (e.g. selected)
    state_of_current = "SELECTED"

    def childIter(self, device):
        '''
        An iterator that yields one Widget instance representing a child widget
        of the represented container widget with not empty name per iteration.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :return: A child Widget instance
        :rtype: Widget
        '''
        widget = self.getWidget(device)
        if widget is not None:
            name = (None if self.pattern_of_children is None
                         else ('&' + self.pattern_of_children))
            i = 0
            iterator = childiters.getByMethod(self.searcher_of_children.method)
            for child in iterator(widget):
                child = self.class_of_children(self,
                                    self.searcher_of_children(name=name, nth=i))
                if child.getImmediate(device) is not None:
                    i += 1
                    yield child

    def getChild(self, child):
        '''
        Gets a Widget instance representing the container's child widget
        according to the given child argument.

        :param child: An index in the container or a name or a searcher of
            the child widget
        :type child: integer or string or searchers.BaseSearcher
        :return: A Widget instance of the child widget or None if an invalid
            argument was passed
        :rtype: Widget or NoneType
        '''
        if isinstance(child, basestring):
            return self.class_of_children(self,
                                          self.searcher_of_children(name=child))
        elif isinstance(child, (int, long)):
            return self.class_of_children(self,
                                          self.searcher_of_children(nth=child))
        elif isinstance(child, searchers.BaseSearcher):
            return self.class_of_children(self, child)
        raise TypeError("Type integer or string or searcher")

    __getitem__ = getChild

    def hasChild(self, device, child):
        '''
        Checks if the represented container widget contains a child widget
        of the given index or name or searcher.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param child: An index in the container or a name or a searcher of
            the child widget
        :type child: integer or string or searchers.BaseSearcher
        :return: True if the container contains the child, False otherwise
        :rtype: boolean
        '''
        child = self.getChild(child)
        return child.getWidget(device) is not None

    def notin(self, device, child):
        '''
        Checks if the represented container widget does not contain a child
        widget of the given index or name or searcher.

        :param device: A device to perform the operation on
        :type device: tadek.connection.device.Device
        :param child: An index in the container or a name or a searcher of
            the child widget
        :type child: integer or string or searchers.BaseSearcher
        :return: True if the container does not contain the child, False
            otherwise
        :rtype: boolean
        '''
        child = self.getChild(child)
        return child.getWidget(device, expectedFailure=True) is None

    def getCurrent(self):
        '''
        Gets a Widget instance representing 'current' child widget (e.g. the
        selected one) of the represented container widget.

        :return: The 'current' child widget
        :rtype: Widget
        '''
        name = (None if self.pattern_of_children is None
                     else ('&' + self.pattern_of_children))
        return self.class_of_children(self, self.searcher_of_children(name=name,
                                                   state=self.state_of_current))

