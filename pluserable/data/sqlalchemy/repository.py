"""Use the SQLAlchemy session to retrieve and store models."""

from datetime import datetime
from typing import Any, Dict, Generic, Optional

from bag.reify import reify
from bag.text import random_string
from kerno.repository.sqlalchemy import Query
from sqlalchemy import func

from pluserable import const
from pluserable.data.repository import AbstractRepo
from pluserable.data.typing import TActivation, TGroup, TUser


class Repository(AbstractRepo, Generic[TActivation, TGroup]):
    """A repository that uses SQLAlchemy for storage."""

    @reify
    def User(self) -> TUser:  # noqa
        return self.kerno.utilities[const.USER_CLASS]

    @reify
    def Activation(self) -> TActivation:  # noqa
        return self.kerno.utilities[const.ACTIVATION_CLASS]

    @reify
    def Group(self) -> TGroup:  # noqa
        return self.kerno.utilities[const.GROUP_CLASS]

    def get_user_by_activation(self, activation: TActivation) -> Optional[TUser]:
        """Return the user with ``activation``, or None."""
        return (
            self.sas.query(self.User).filter(self.User.activation == activation).first()
        )

    def get_user_by_id(self, id: int) -> Optional[TUser]:
        """Return the user with ``id``, or None."""
        # print("\nFetching {} #{}\n".format(self.User, id))
        return self.sas.query(self.User).get(id)

    def _q_user_by_email(self, email: str) -> Query[TUser]:
        """Return a query for a user with ``email``."""
        return self.sas.query(self.User).filter(
            func.lower(self.User.email) == email.lower()
        )

    def get_user_by_email(self, email: str) -> Optional[TUser]:
        """Return a user with ``email``, or None."""
        return self._q_user_by_email(email).first()

    def one_user_by_email(self, email: str) -> TUser:
        """Return a user with ``email``, or raise."""
        return self._q_user_by_email(email).one()

    def get_user_by_username(self, username: str) -> Optional[TUser]:
        """Return a user with ``username``, or None. Case-insensitive."""
        return (
            self.sas.query(self.User)
            .filter(
                # self.User.username == username
                func.lower(self.User.username)
                == username.lower()
            )
            .first()
        )

    def q_groups(self) -> Query[TGroup]:
        """Return an iterator on all groups."""
        return self.sas.query(self.Group)

    def q_activations(self) -> Query[TActivation]:
        """Return an iterator on all activations."""
        return self.sas.query(self.Activation)

    def get_activation_by_code(self, code: str) -> Optional[TActivation]:
        """Return the Activation with ``code``, or None."""
        return self.sas.query(self.Activation).filter_by(code=code).first()

    def delete_activation(self, user: TUser, activation: TActivation) -> None:
        """Delete the Activation instance from the database."""
        assert isinstance(activation, self.Activation)
        user.activation = None
        self.delete(activation)

    def delete_expired_activations(self, now: Optional[datetime] = None) -> int:
        """Delete all old activations."""
        now = now or datetime.utcnow()
        oldies = self.sas.query(self.Activation).filter(
            self.Activation.valid_until < now
        )
        count = oldies.count()
        for old in oldies:
            self.delete(old)
        return count

    def get_or_create_user_by_email(self, email: str, details: Dict[str, Any]) -> TUser:
        """Return User if ``email`` exists, else create User with ``details``.

        The returned User instance has a transient ``is_new`` flag.
        If the user is new, they need to go through password recovery.
        # TODO No access to tmp_password, create activation, send email
        """
        opt_user = self.get_user_by_email(email)
        if opt_user is None:
            tmp_password = random_string(length=8)
            user = self.User(email=email, password=tmp_password, **details)
            self.add(user)
            self.flush()
            user.is_new = tmp_password
        else:  # is_new is a transient variable.
            user = opt_user
            user.is_new = False
        return user

    def q_users(self) -> Query[TUser]:
        """Return a query for all users."""
        return self.sas.query(self.User)
