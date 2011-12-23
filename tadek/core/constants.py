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

# The default encoding
ENCODING = "utf-8"

#: Actions
ACTIONS = (
    "ACTIVATE",
    "CLICK",
    "CONTRACT",
    "EDIT",
    "EXPAND",
    "JUMP",
    "PRESS",
    "RELEASE"
)

#: Relations
RELATIONS = (
    "CHILD_CELL_OF",
    "LABEL_FOR",
    "LABELED_BY"
)

#: Roles
ROLES = (
    "ACCELERATOR_LABEL",
    "ALERT",
    "APPLICATION",
    "BUTTON",
    "CANVAS",
    "CHECK_BOX",
    "CHECK_MENU_ITEM",
    "COMBO_BOX",
    "DIALOG",
    "DOCUMENT_FRAME",
    "DRAWING_AREA",
    "EDITBAR",
    "ENTRY",
    "FILE_CHOOSER",
    "FILLER",
    "FORM",
    "FRAME",
    "HEADER",
    "HEADING",
    "ICON",
    "IMAGE",
    "INTERNAL_FRAME",
    "LABEL",
    "LINK",
    "LIST",
    "LIST_ITEM",
    "MENU",
    "MENU_BAR",
    "MENU_ITEM",
    "PAGE",
    "PAGE_TAB",
    "PAGE_TAB_LIST",
    "PANEL",
    "PARAGRAPH",
    "PASSWORD_TEXT",
    "POPUP_MENU",
    "PROGRESS_BAR",
    "RADIO_BUTTON",
    "RADIO_MENU_ITEM",
    "SCROLL_BAR",
    "SCROLL_PANE",
    "SECTION",
    "SEPARATOR",
    "SLIDER",
    "SPIN_BUTTON",
    "SPLIT_PANE",
    "STATUS_BAR",
    "TABLE",
    "TABLE_CELL",
    "TABLE_COLUMN_HEADER",
    "TABLE_ROW_HEADER",
    "TEXT",
    "TOGGLE_BUTTON",
    "TOOL_BAR",
    "TREE",
    "TREE_TABLE",
    "UNKNOWN",
    "VIEWPORT",
    "WINDOW",
)

#: States
STATES = (
    "ACTIVE",
    "CHECKED",
    "COLLAPSED",
    "EDITABLE",
    "ENABLED",
    "EXPANDABLE",
    "EXPANDED",
    "FOCUSABLE",
    "FOCUSED",
    "MULTILINE",
    "MULTISELECTABLE",
    "SELECTABLE",
    "SELECTED",
    "SENSITIVE",
    "SHOWING",
    "VISIBLE",
    "VISITED"
)

#: Mouse buttons
BUTTONS = (
    "LEFT",
    "MIDDLE",
    "RIGHT"
)

#: Mouse events
EVENTS = (
    "CLICK",
    "DOUBLE_CLICK",
    "PRESS",
    "RELEASE",
    "ABSOLUTE_MOTION",
    "RELATIVE_MOTION"
)

#: Keyboard symbol codes mapping
KEY_SYMS = {
               "F1" : 0xFFBE,
               "F2" : 0xFFBF,
               "F3" : 0xFFC0,
               "F4" : 0xFFC1,
               "F5" : 0xFFC2,
               "F6" : 0xFFC3,
               "F7" : 0xFFC4,
               "F8" : 0xFFC5,
               "F9" : 0xFFC6,
              "F10" : 0xFFC7,
              "F11" : 0xFFC8,
              "F12" : 0xFFC9,
        "BACKSPACE" : 0xFF08,
              "TAB" : 0xFF09,
            "ENTER" : 0xFF0D,
           "ESCAPE" : 0xFF1B,
           "INSERT" : 0xFF63,
           "DELETE" : 0xFFFF,
             "HOME" : 0xFF50,
             "LEFT" : 0xFF51,
               "UP" : 0xFF52,
            "RIGHT" : 0xFF53,
             "DOWN" : 0xFF54,
          "PAGE_UP" : 0xFF55,
        "PAGE_DOWN" : 0xFF56,
              "END" : 0xFF57,
       "LEFT_SHIFT" : 0xFFE1,
      "RIGHT_SHIFT" : 0xFFE2,
     "LEFT_CONTROL" : 0xFFE3,
    "RIGHT_CONTROL" : 0xFFE4,
         "LEFT_ALT" : 0xFFE9,
        "RIGHT_ALT" : 0xFFEA
}

#: Keyboard keys mapping
KEY_CODES = {
              "F1": 0x0043,
              "F2": 0x0044,
              "F3": 0x0045,
              "F4": 0x0046,
              "F5": 0x0047,
              "F6": 0x0048,
              "F7": 0x0049,
              "F8": 0x004a,
              "F9": 0x004b,
             "F10": 0x004c,
             "F11": 0x005f,
             "F12": 0x0060,
       "BACKSPACE": 0x0016,
             "TAB": 0x0017,
           "SPACE": 0x0020,
           "ENTER": 0x0024,
          "ESCAPE": 0x0009,
          "INSERT": 0x0076,
          "DELETE": 0x0077,
            "HOME": 0x006e,
            "LEFT": 0x0071,
              "UP": 0x006f,
           "RIGHT": 0x0072,
            "DOWN": 0x0074,
         "PAGE_UP": 0x0070,
       "PAGE_DOWN": 0x0075,
             "END": 0x0073,
      "LEFT_SHIFT": 0x0032,
     "RIGHT_SHIFT": 0x003e,
    "LEFT_CONTROL": 0x0025,
   "RIGHT_CONTROL": 0x0069,
        "LEFT_ALT": 0x0040,
       "RIGHT_ALT": 0x006c
}
