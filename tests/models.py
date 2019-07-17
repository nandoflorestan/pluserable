"""Models for tests."""

from sqlalchemy.ext.declarative import declarative_base
from bag.sqlalchemy.tricks import MinimalBase
from pluserable.data.sqlalchemy.models import (
    ActivationMixin, GroupMixin, UsernameMixin, UserGroupMixin)

Base = declarative_base(cls=MinimalBase)  # type: MinimalBase


# Inherit from NoUsernameMixin instead if you do not want a username field.
class User(UsernameMixin, Base):  # noqa
    pass


class Group(GroupMixin, Base):  # noqa
    pass


class UserGroup(UserGroupMixin, Base):  # noqa
    pass


class Activation(ActivationMixin, Base):  # noqa
    pass
