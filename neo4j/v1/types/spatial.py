#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Copyright (c) 2002-2018 "Neo Technology,"
# Network Engine for Objects in Lund AB [http://neotechnology.com]
#
# This file is part of Neo4j.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
This module defines spatial data types.
"""


__all__ = [
    "Point",
]

# This list contains definitions for the set of Point subclasses to be
# dynamically created within the module scope. Each definition consists
# of the CRS code, type name and type attribute names respectively.
# New Point subclasses should be added to this list.
__point_types = [
    (7203, "CartesianPoint", ["x", "y"]),
    (9157, "CartesianPoint3D", ["x", "y", "z"]),
    (4326, "WGS84Point", ["longitude", "latitude"]),
    (4979, "WGS84Point3D", ["longitude", "latitude", "height"]),
]


class Point(tuple):
    """ A point within a geometric space. This type is generally used
    via its subclasses and should not be instantiated directly unless
    there is no subclass defined for the required CRS.
    """

    @classmethod
    def __get_subclass(cls, crs):
        """ Find the the correct Point subclass for a given CRS.
        If no subclass can be found, None is returned.
        """
        if cls.crs == crs:
            return cls
        for subclass in cls.__subclasses__():
            got = subclass.__get_subclass(crs)
            if got:
                return got
        return None

    @classmethod
    def hydrate(cls, crs, *coordinates):
        """ Create a new instance of a Point subclass from a raw
        set of fields. The subclass chosen is determined by the
        given CRS code; a ValueError will be raised if no such
        subclass can be found.
        """
        point_class = cls.__get_subclass(crs)
        if point_class is None:
            raise ValueError("CRS %d not supported" % crs)
        if 2 <= len(coordinates) <= 3:
            inst = point_class(coordinates)
            inst.crs = crs
            return inst
        else:
            raise ValueError("%d-dimensional Point values are not supported" % len(coordinates))

    crs = None

    def __new__(cls, iterable):
        return tuple.__new__(cls, iterable)

    def __repr__(self):
        return "POINT(%s)" % " ".join(map(str, self))

    def __eq__(self, other):
        try:
            return self.crs == other.crs and tuple(self) == tuple(other)
        except (AttributeError, TypeError):
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.crs) ^ hash(tuple(self))


def __create_point_types():
    """ Dynamically add the defined set of Point subclasses to the
    module scope.
    """
    from sys import modules
    this_module = modules[__name__]
    for crs, name, fields in __point_types:
        attributes = {"crs": crs}
        for i, field in enumerate(fields):
            attributes[field] = property(lambda self, index=i: self[index])
        setattr(this_module, name, type(name, (Point,), attributes))
        __all__.append(name)


# This top-level call ensures that the dynamic Point subclasses are loaded
# into module scope on import.
__create_point_types()