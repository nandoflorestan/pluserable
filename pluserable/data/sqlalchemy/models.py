"""Base models for apps that use SQLAlchemy and pluserable."""

from bag.sqlalchemy.tricks import MinimalBase, ID
from bag.text import pluralize
from bag.text.hash import random_hash
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr

from pluserable.data.models import (
    thirty_days_from_now,
    ActivationBase,
    GroupBase,
    UserBase,
)


class ActivationMixin(ActivationBase, MinimalBase, ID):
    """Handles email confirmation codes and password reset codes for users.

    The code should be a random hash that is valid only once.
    After the code is used to access the site, it gets removed.

    The "created by" value refers to a system:
    new user registration, password reset, forgot password etc.
    """

    @declared_attr
    def code(self):
        """A random hash that is valid only once."""
        return sa.Column(
            sa.Unicode(30), nullable=False, unique=True, default=random_hash
        )

    @declared_attr
    def valid_until(self):
        """How long will the activation key last."""
        return sa.Column(
            sa.DateTime, nullable=False, default=thirty_days_from_now
        )

    @declared_attr
    def created_by(self):  # TODO Use according to doc above
        """The system that generated the activation key."""
        return sa.Column(sa.Unicode(30), nullable=False, default="web")


class NoUsernameMixin(UserBase, MinimalBase, ID):
    @declared_attr
    def email(self):
        """User e-mail address."""
        return sa.Column(sa.Unicode(100), nullable=False, unique=True)

    @declared_attr
    def last_login_date(self):
        """Date of user's last login."""
        return sa.Column(
            sa.TIMESTAMP(timezone=False),
            default=sa.func.now(),
            server_default=sa.func.now(),
            nullable=False,
        )

    @declared_attr
    def registered_date(self):
        """Date of user's registration."""
        return sa.Column(
            sa.TIMESTAMP(timezone=False),
            default=sa.sql.func.now(),
            server_default=sa.func.now(),
            nullable=False,
        )

    @declared_attr
    def salt(self):
        """Password salt for user."""
        return sa.Column(sa.Unicode(256), nullable=False)

    @declared_attr
    def activation_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey("{}.id".format(ActivationMixin.__tablename__)),
        )

    @declared_attr
    def activation(self):
        return sa.orm.relationship("Activation", backref="user")

    @declared_attr
    def _password(self):
        """Password hash."""
        return sa.Column("password", sa.Unicode(256), nullable=False)


class UsernameMixin(NoUsernameMixin):
    """Additional username column for sites that need it."""

    @declared_attr
    def username(self):
        return sa.Column(sa.Unicode(30), nullable=False, unique=True)


class GroupMixin(GroupBase, MinimalBase, ID):
    """Mixin class for groups."""

    @declared_attr
    def name(self):
        return sa.Column(sa.Unicode(50), unique=True)

    @declared_attr
    def description(self):
        return sa.Column(sa.UnicodeText())

    @declared_attr
    def users(self):
        """Relationship for users belonging to this group."""
        return sa.orm.relationship(
            "User",
            secondary=UserGroupMixin.__tablename__,
            # order_by='%s.user.username' % UsernameMixin.__tablename__,
            passive_deletes=True,
            passive_updates=True,
            backref=pluralize(GroupMixin.__tablename__),
        )

    # Removing the only mention of GroupPermission in the entire project:
    # @declared_attr
    # def permissions(self):
    #     """ permissions assigned to this group"""
    #     return sa.orm.relationship(
    #         'GroupPermission',
    #         backref='groups',
    #         cascade="all, delete-orphan",
    #         passive_deletes=True,
    #         passive_updates=True,
    #     )


class UserGroupMixin(MinimalBase, ID):
    @declared_attr
    def group_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey(GroupMixin.__tablename__ + ".id"),
            index=True,
        )

    @declared_attr
    def user_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
            index=True,
        )

    def __repr__(self):
        return "<{}: {}, {}>".format(type(self), self.group_id, self.user_id)


__all__ = [
    k
    for k, v in locals().items()
    if isinstance(v, type) and issubclass(v, MinimalBase)
]
