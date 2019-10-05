"""Base model classes for any backend (SQLAlchemy, ZODB etc.)."""

from datetime import datetime, timedelta
from typing import Optional

from bag.text.hash import random_hash
from bag.web import gravatar_image
import cryptacular.bcrypt

crypt = cryptacular.bcrypt.BCRYPTPasswordManager()


def thirty_days_from_now(now: Optional[datetime] = None) -> datetime:
    """Return a datetime pointing to exactly 30 days in the future."""
    now = now or datetime.utcnow()
    return now + timedelta(days=30)


class ActivationBase:
    """Handles activations and password reset items for users.

    ``code`` is a random hash that is valid only once.
    Once the hash is used to access the site, it is removed.

    ``valid_until`` is a datetime until when the activation key will last.

    ``created_by`` is a system: new user registration, password reset,
    forgot password etc.
    """

    def __init__(
        self,
        code: str = "",
        valid_until: Optional[datetime] = None,
        created_by: str = "web",
    ):
        """Usually call with the ``created_by`` system, or no arguments."""
        self.code = code or random_hash()
        self.valid_until = valid_until or thirty_days_from_now()
        assert isinstance(self.valid_until, datetime)
        self.created_by = created_by


class UserBase:
    """Base class for a User model."""

    def __init__(
        self, email: str, password: str, salt: str = "", activation=None, **kw
    ):  # noqa
        # print('User constructor: {} / {} / {} / {}'.format(
        #     email, password, salt, activation))
        self.email = email
        assert self.email and isinstance(self.email, str)
        self.salt = salt or random_hash(24)
        self.password = password
        assert self.password and isinstance(self.password, str)
        self.activation = activation
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.email)

    def gravatar_url(self, default="mm", size=80, cacheable=True):  # no cover
        """Return a Gravatar image URL for this user."""
        return gravatar_image(  # pragma: no cover
            self.email, default=default, size=size, cacheable=cacheable
        )

    @property
    def password(self):
        """Set the password, or retrieve the password hash."""
        return self._password

    @password.setter
    def password(self, value):
        self._password = self._hash_password(value)

    def _hash_password(self, password):
        assert self.salt, (
            "UserBase constructor was not called; "
            "you probably have your User base classes in the wrong order."
        )
        return str(crypt.encode(password + self.salt))

    @classmethod
    def generate_random_password(cls, chars=12):  # pragma: no cover
        """Generate random string of fixed length.

        This method is not used in the pluserable system, but offered anyway.
        """
        return random_hash(chars)

    def check_password(self, password: str) -> bool:
        """Check the ``password`` and return a boolean."""
        if not password:
            return False
        return crypt.check(self.password, password + self.salt)

    @property
    def is_activated(self):
        """Return False if this user needs to confirm her email address."""
        return self.activation is None

    # @property
    # def __acl__(self):
    #     return [
    #         (Allow, 'user:%s' % self.id, 'access_user')
    #     ]


class GroupBase:
    """Base class for a Group model."""

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.name)
