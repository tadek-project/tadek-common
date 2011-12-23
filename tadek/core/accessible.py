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

from xml.etree import cElementTree as etree

from utils import decode

__all__ = ["Path", "Accessible", "Relation"]

# All classes defined herein are 'new-style' classes
__metaclass__ = type

class Path:
    '''
    A class of accessible paths.
    '''
    def __init__(self, *path):
        '''
        Stores a path to an accessible object.
        '''
        self.tuple = path
        self.unicode = u"/%s" % '/'.join(str(i) for i in path)

    def __eq__(self, path):
        '''
        Checks if two paths are equal.

        :param path: A path to compare with
        :type path: Path
        :return: True if these two paths are equal, False otherwise
        :rtype: boolean
        '''
        if not isinstance(path, Path):
            return False
        return self.tuple == path.tuple

    def __ne__(self, path):
        '''
        Checks if two paths are not equal.

        :param path: A path to compare with
        :type path: Path
        :return: True if these two paths are not equal, False otherwise
        :rtype: boolean
        '''
        if not isinstance(path, Path):
            return True
        return self.tuple != path.tuple

    def __unicode__(self):
        '''
        Returns an unicode representation of the path.

        :return: An unicode representation of the path
        :rtype: unicode
        '''
        return self.unicode

    __repr__ = __unicode__

    def index(self):
        '''
        Returns an index in the parent of the path.

        :return: An index in the parent
        :rtype: integer
        '''
        return self.tuple[-1] if self.tuple else None

    def parent(self):
        '''
        Returns a new path representing a parent of the path.

        :return: A parent path
        :rtype: Path
        '''
        return self.__class__(*self.tuple[:-1]) if self.tuple else None

    def child(self, index):
        '''
        Returns a new path representing a child of the given index.

        :param index: An index of a child
        :type index: integer
        :return: A child path
        :rtype: Path
        '''
        child = self.tuple + (index,)
        return self.__class__(*child)

    def marshal(self, element):
        '''
        Marshals the path to the given element tree.

        :param element: The element tree to marshal to
        :type element: xml.etree.Element
        '''
        element.text = self.unicode

    @classmethod
    def unmarshal(cls, element):
        '''
        Unmarshals a path given as the element tree.

        :param element: The element tree to unmarshal from
        :type element: xml.etree.Element
        :return: The unmarshaled path
        :rtype: Path
        '''
        return cls(*[int(i) for i in element.text.split('/') if i])


class Accessible:
    '''
    A class for describing accessible objects. Provides the following accessible
    properties:
        - path - a path to the accessible in an accessible tree,
        - parent - a parent object of the accessible,
        - index - an index of the accessible in parent object,
        - role - a role of the accessible,
        - name - a name of the accessible,
        - description - description of the accessible,
        - position - a tuple of x and y coordinates of the accessible on
          the screen,
        - size - a size as a tuple of the accessible,
        - text - text contained in the accessible,
        - editable - True if the accessible supports text editing, False
          otherwise,
        - value - a float value of the accessible,
        - count - a number of children of the accessible,
        - attributes - a list of the accessible attributes,
        - actions - a list of available actions of the accessible,
        - relations - a list of relations of the accessible,
        - states - a list of the accessible states,
        - children - an iterator of children of the accessible object.
    '''
    #: The default role of the accessible
    role = None
    #: The default name of the accessible
    name = None
    #: The default description of the accessible
    description = None
    #: The default position of the accessible
    position = None
    #: The default position of the accessible
    size = None
    #: The default text contained in the accessible
    _text = None
    #: The default editable value of the accessible
    editable = False
    #: The default value of the accessible
    _value = None
    #: The default number of children
    count = 0
    #: The default source device of the accessible
    device = None

    def __init__(self, path, children=()):
        '''
        Stores details about the accessible object.

        :param path: A path to the accessible
        :type path: Path
        :param children: A list of the accessible children
        :type children: list or tuple
        '''
        self.path = path
        self.index = self.path.index()
        self.parent = self.path.parent()
        self.attributes = {}
        self.actions = []
        self.relations = []
        self.states = []
        self._children = [child for child in children] if children else []
        self.count = len(self._children)

    def setDevice(self, device):
        '''
        Sets the given device for the accessible and its fetched children.

        :param device: The device to set for the accessible
        :type device: tadek.connection.device.Device
        '''
        self.device = device
        for child in self.children(force=False):
            child.setDevice(device)

    def text(self, text=None):
        '''
        Gets or sets text in the accessible.

        :param text: Text to set in the accessible
        :type text: string
        :return: Text contained in the accessible
        :rtype: string
        '''
        if text is None:
            return self._text
        if not self.device:
            self._text = text
        #    raise ValueError("Target device not specified")
        elif self.editable and self.device.setAccessible(self.path, text=text):
            self._text = text
    text = property(text, text)

    def value(self, value=None):
        '''
        Gets or sets value of the accessible.

        :param value: A value to set in the accessible
        :type value: float
        :return: A value contained in the accessible
        :rtype: float
        '''
        if value is None:
            return self._value
        #if not self.device:
        #    raise ValueError("Target device not specified")
        if not self.device or self.device.setAccessible(self.path, value=value):
            self._value = value
    value = property(value, value)

    def do(self, action):
        '''
        Performs the given action on the accessible.

        :param action: A name of the action to perform
        :type action: string
        :return: True if success, False otherwise
        :rtype: boolean
        '''
        if action not in self.actions:
            return False
        if not self.device:
            raise ValueError("Target device not specified")
        return self.device.doAccessible(self.path, action)

    def children(self, force=True):
        '''
        An iterator that yields one child of the accessible per iteration.

        :param force: True if the iteration of accessible children should be
            forced by fetching children from a device, False otherwise
        :type force: boolean
        :return: A child of the accessible
        :rtype: Accessible
        '''
        if self.count:
            if self._children:
                for child in self._children:
                    yield child
            elif force:
                if not self.device:
                    raise ValueError("Target device not specified")
                for i in xrange(self.count):
                    child = self.device.getAccessible(self.path.child(i))
                    if not child:
                        # The accessible is not up-to-date
                        break
                    yield child

    def marshal(self):
        '''
        Marshals the accessible to an element tree.

        :return: The marshaled accessible
        :rtype: xml.etree.Element
        '''
        element = etree.Element("accessible")
        self.path.marshal(etree.SubElement(element, "path"))
        elem = etree.SubElement(element, "role")
        if self.role:
            elem.text = decode(self.role)
        elem = etree.SubElement(element, "name")
        if self.name is not None:
            elem.text = decode(self.name)
        elem = etree.SubElement(element, "description")
        if self.description is not None:
            elem.text = decode(self.description)
        # Position
        if self.position:
            elem = etree.SubElement(element, "position")
            elem.text = u','.join([decode(i) for i in self.position])
        # Size
        if self.size:
            elem = etree.SubElement(element, "size")
            elem.text = u','.join([decode(i) for i in self.size])
        # Text
        if self.text is not None:
            etree.SubElement(element, "text",
                editable=decode(int(self.editable))).text = decode(self.text)
        # Value
        if self.value is not None:
            etree.SubElement(element, "value").text = decode(self.value)
        # Attributes
        if self.attributes:
            attribs = etree.SubElement(element, "attributes")
            for attr, val in self.attributes.iteritems():
                elem = etree.SubElement(attribs, "attribute")
                etree.SubElement(elem, "name").text = decode(attr)
                etree.SubElement(elem, "value").text = decode(val)
        # Actions
        if self.actions:
            actions = etree.SubElement(element, "actions")
            for action in self.actions:
                etree.SubElement(actions, "action").text = decode(action)
        # Relations
        if self.relations:
            relations = etree.SubElement(element, "relations")
            for relation in self.relations:
                relations.append(relation.marshal())
        # States
        states = etree.SubElement(element, "states")
        for state in self.states:
            etree.SubElement(states, "state").text = decode(state)
        # Children
        children = etree.SubElement(element, "children",
                                    count=decode(self.count))
        for child in self._children:
            children.append(child.marshal())
        return element

    @classmethod
    def unmarshal(cls, element):
        '''
        Unmarshals an accessible from the given element tree.

        :param element: The marshaled accessible
        :type element: xml.etree.Element
        :return: The unmarshaled accessible
        :rtype: Accessible
        '''
        children = []
        for child in element.find("children").getchildren():
            children.append(cls.unmarshal(child))
        accessible = cls(Path.unmarshal(element.find("path")),
                         children=children)
        val = element.findtext("role")
        if val:
            accessible.role = val
        val = element.findtext("name")
        if val is not None:
            accessible.name = val
        val = element.findtext("description")
        if val is not None:
            accessible.description = val
        # Position
        val = element.findtext("position")
        if val:
            accessible.position = tuple([int(i) for i in val.split(',')])
        # Size
        val = element.findtext("size")
        if val:
            accessible.size = tuple([int(i) for i in val.split(',')])
        # Text
        text = element.find("text")
        if text is not None:
            val = int(text.get("editable", '0'))
            if val:
                accessible.editable = True
            accessible.text = text.text if text.text else u''
        # Value
        val = element.findtext("value")
        if val:
            accessible.value = float(val)
        # Attributes
        attribs = element.find("attributes")
        if attribs is not None and len(attribs):
            for attr in attribs.getchildren():
                val = attr.findtext("name")
                if val:
                    accessible.attributes[val] = attr.findtext("value")
        # Actions
        actions = element.find("actions")
        if actions is not None and len(actions):
            for action in actions.getchildren():
                accessible.actions.append(action.text)
        # Relations
        relations = element.find("relations")
        if relations is not None and len(relations):
            for relation in relations.getchildren():
                accessible.relations.append(Relation.unmarshal(relation))
        # States
        for state in element.find("states").getchildren():
            accessible.states.append(state.text)
        val = int(element.find("children").get("count", "0"))
        if val:
            accessible.count = val
        return accessible


class Relation(object):
    '''
    A class to represent accessible relations. A relation consists of type and
    a list of target accessible objects.
    '''
    #: The default source device of the accessible relation
    device = None

    def __init__(self, type, targets=()):
        '''
        Stores a list of paths to target accessibles for the relation type.
        '''
        self.type = type
        self._targets = [path for path in targets] if targets else []

    def __iter__(self):
        '''
        An iterator that yields one path of target accessible object of
        the accessible relation per iteration.

        :return: A path of target accessible
        :rtype: Path
        '''
        return iter(self._targets)

    def targets(self):
        '''
        An iterator that yields one target accessible object of the accessible
        relation per iteration.

        :return: A target accessible
        :rtype: Accessible
        '''
        if not self.device:
            raise ValueError("Target device not specified")
        for path in self:
            target = self.device.getAccessible(path)
            if not target:
                # The accessible relation is not up-to-date
                break
            yield target

    def marshal(self):
        '''
        Marshals the accessible relation to an element tree.

        :return: The marshaled accessible relation
        :rtype: xml.etree.Element
        '''
        element = etree.Element("relation")
        etree.SubElement(element, "type").text = decode(self.type)
        targets = etree.SubElement(element, "targets")
        for target in self._targets:
            target.marshal(etree.SubElement(targets, "target"))
        return element

    @classmethod
    def unmarshal(cls, element):
        '''
        Unmarshals a accessible relation given as the element tree.

        :param element: The marshaled accessible relation
        :type element: xml.etree.Element
        :return: The unmarshaled accessible relation
        :rtype: Relation
        '''
        targets = []
        for target in element.find("targets").getchildren():
            targets.append(Path.unmarshal(target))
        return cls(element.findtext("type"), targets=targets)

