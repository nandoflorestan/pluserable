"""Use the SQLAlchemy session to retrieve and store models."""

from datetime import datetime
from typing import Any, Dict, Optional

from bag.reify import reify
from bag.text import random_string
from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository
from sqlalchemy import func

from pluserable import const


class Repository(BaseSQLAlchemyRepository):
    """A repository that uses SQLAlchemy for storage.

    In the future other strategies can be developed (e. g. ZODB).
    """

    @reify
    def User(self):
        return self.kerno.get_utility(const.USER_CLASS)

    @reify
    def Activation(self):
        return self.kerno.get_utility(const.ACTIVATION_CLASS)

    @reify
    def Group(self):
        return self.kerno.get_utility(const.GROUP_CLASS)

    def q_user_by_activation(self, activation):
        """Return the user with ``activation``, or None."""
        return self.sas.query(self.User).filter(
            self.User.activation == activation).first()

    def q_user_by_id(self, id):
        """Return a user with ``id``, or None."""
        # print("\nFetching {} #{}\n".format(self.User, id))
        return self.sas.query(self.User).get(id)

    def q_user_by_email(self, email: str):
        """Return a query for a user with ``email``."""
        return self.sas.query(self.User).filter(
            func.lower(self.User.email) == email.lower())

    def get_user_by_email(self, email: str):
        """Return a user with ``email``, or None."""
        return self.q_user_by_email(email).first()

    def one_user_by_email(self, email: str):
        """Return a user with ``email``, or raise."""
        return self.q_user_by_email(email).one()

    def q_user_by_username(self, username: str):
        """Return a user with ``username``, or None. Case-insensitive."""
        return self.sas.query(self.User).filter(
            # self.User.username == username
            func.lower(self.User.username) == username.lower()).first()

    def q_users(self):
        """Return an iterator on all users."""
        return self.sas.query(self.User)

    def store_user(self, user):
        """Save the ``user`` instance."""
        self.sas.add(user)

    def q_groups(self):
        """Return an iterator on all groups."""
        return self.sas.query(self.Group)

    def q_group_by_id(self, id):
        """Return a group with ``id``, or None."""
        return self.sas.query(self.Group).get(id)

    def q_activations(self):
        """Return an iterator on all activations."""
        return self.sas.query(self.Activation)

    def store_activation(self, activation):
        """Save the ``activation`` instance."""
        self.sas.add(activation)

    def q_activation_by_code(self, code):
        """Return the Activation with ``code``, or None."""
        return self.sas.query(self.Activation).filter_by(code=code).first()

    def delete_activation(self, user, activation):
        """Delete the Activation instance from the database."""
        assert isinstance(activation, self.Activation)
        user.activation = None
        self.sas.delete(activation)

    def delete_expired_activations(self, now=None):
        """Delete all old activations."""
        now = now or datetime.utcnow()
        oldies = self.sas.query(self.Activation).filter(
            self.Activation.valid_until < now)
        count = oldies.count()
        for old in oldies:
            self.sas.delete(old)
        return count

    def get_or_create_user_by_email(self, email: str, details: Dict[str, Any]):
        """Return User if ``email`` exists, else create User with ``details``.

        The returned User instance has a transient ``is_new`` flag.
        If the user is new, they need to go through password recovery.
        # TODO No access to tmp_password, create activation, send email
        """
        user = self.q_user_by_email(email)
        if user is None:
            tmp_password = random_string(length=8)
            user = self.User(email=email, password=tmp_password, **details)
            self.add(user)
            self.flush()
            user.is_new = tmp_password
        else:
            user.is_new = False
        return user
