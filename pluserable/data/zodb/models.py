"""Base models for apps that use ZODB and pluserable.

This is a work in progress; the ZODB repository has not been developed and
tests would need to change to accomodate both technologies.
"""

from persistent import Persistent
from pluserable.data.models import ActivationBase, GroupBase, UserBase


class Activation(Persistent, ActivationBase):

    pass


class User(Persistent, UserBase):

    pass


class Group(Persistent, GroupBase):

    def __init__(self, name, description=None, users=None):
        """Constructor."""
        assert name and isinstance(name, str)
        self.name = name
        self.description = description
        self.users = users or []
