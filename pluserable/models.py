"""Base models for apps that use SQLAlchemy and pluserable."""

from urllib.parse import urlencode

from pyramid.i18n import TranslationStringFactory
# from pyramid.security import Allow
from datetime import datetime, timedelta, date
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from bag.sqlalchemy.tricks import MinimalBase, ID
from bag.text import pluralize
from bag.text.hash import random_hash

import cryptacular.bcrypt
import hashlib
import sqlalchemy as sa

_ = TranslationStringFactory('pluserable')

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def three_days_from_now():
    return datetime.utcnow() + timedelta(days=3)


class ActivationMixin(MinimalBase, ID):
    """Handles activations/password reset items for users.

    The code should be a random hash that is valid only once.
    After the hash is used to access the site, it'll be removed.

    The "created by" is a system: new user registration, password reset,
    forgot password etc.
    """

    @declared_attr
    def code(self):
        """A random hash that is valid only once."""
        return sa.Column(sa.Unicode(30), nullable=False,
                         unique=True,
                         default=random_hash)

    @declared_attr
    def valid_until(self):
        """How long will the activation key last."""
        return sa.Column(sa.DateTime, nullable=False,
                         default=three_days_from_now)

    @declared_attr
    def created_by(self):
        """The system that generated the activation key."""
        return sa.Column(sa.Unicode(30), nullable=False,
                         default='web')


class NoUsernameMixin(MinimalBase, ID):

    @declared_attr
    def email(self):
        """ E-mail for user """
        return sa.Column(sa.Unicode(100), nullable=False, unique=True)

    @declared_attr
    def status(self):
        """ Status of user """
        return sa.Column(sa.Integer())

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
        """ Password salt for user """
        return sa.Column(sa.Unicode(256), nullable=False)

    @declared_attr
    def _password(self):
        """ Password hash for user object """
        return sa.Column('password', sa.Unicode(256), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._set_password(value)

    @declared_attr
    def activation_id(self):
        return sa.Column(sa.Integer, sa.ForeignKey('{}.id'.format(
            ActivationMixin.__tablename__)))

    @declared_attr
    def activation(self):
        return sa.orm.relationship('Activation', backref='user')

    @property
    def is_activated(self):
        return self.activation_id is None

    def _get_password(self):
        return self._password

    def _set_password(self, raw_password):
        self._password = self._hash_password(raw_password)

    def _hash_password(self, password):
        if not self.salt:
            self.salt = random_hash(24)
        return str(crypt.encode(password + self.salt))

    def gravatar_url(self, default='mm', size=80, cacheable=True):
        """Return a Gravatar image URL for this user."""
        base = "http://www.gravatar.com/avatar/" if cacheable else \
            "https://secure.gravatar.com/avatar/"
        return base + \
            hashlib.md5(self.email.encode('utf8').lower()).hexdigest() + \
            "?" + urlencode({'d': default, 's': str(size)})

    @classmethod
    def generate_random_password(cls, chars=12):
        """Generate random string of fixed length."""
        return random_hash(chars)

    def check_password(self, password):
        """Check the ``password`` and return a boolean."""
        if not password:
            return False
        return crypt.check(self.password, password + self.salt)

    def __repr__(self):
        return '<User: %s>' % self.email

    # @property
    # def __acl__(self):
    #     return [
    #         (Allow, 'user:%s' % self.id, 'access_user')
    #     ]


class UsernameMixin(NoUsernameMixin):
    """Additional username column for sites that need it."""

    @declared_attr
    def username(self):
        return sa.Column(sa.Unicode(30), nullable=False, unique=True)


class GroupMixin(MinimalBase, ID):
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
            'User',
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

    def __repr__(self):
        return '<Group: %s>' % self.name


class UserGroupMixin(MinimalBase, ID):

    @declared_attr
    def group_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey(GroupMixin.__tablename__ + '.id'))

    @declared_attr
    def user_id(self):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE'))

    def __repr__(self):
        return '<UserGroup: %s, %s>' % (self.group_name, self.user_id,)


__all__ = [
    k for k, v in locals().items()
    if isinstance(v, type) and issubclass(v, MinimalBase)
]
