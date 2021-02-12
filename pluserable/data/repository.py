"""Repository implementations.

Repositories are persistence strategies.
"""

from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generic, Optional

from kerno.repository.sqlalchemy import BaseSQLAlchemyRepository, Query
from kerno.typing import DictStr

from pluserable.data.typing import TActivation, TGroup, TTUser


class AbstractRepo(
    BaseSQLAlchemyRepository,
    Generic[TActivation, TGroup, TTUser],
    metaclass=ABCMeta,
):
    """An abstract base class (ABC) defining the repository interface."""

    @abstractmethod
    def get_user_by_activation(
        self, activation: TActivation
    ) -> Optional[TTUser]:
        """Return the user with ``activation``, or None."""

    @abstractmethod
    def get_user_by_id(self, id: int) -> Optional[TTUser]:
        """Return the user with ``id``, or None."""

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[TTUser]:
        """Return a user with ``email``, or None."""

    @abstractmethod
    def one_user_by_email(self, email: str) -> TTUser:
        """Return a user with ``email``, or raise."""

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[TTUser]:
        """Return a user with ``username``, or None. Case-insensitive."""

    @abstractmethod
    def q_groups(self) -> Query[TGroup]:
        """Return an iterator on all groups."""

    @abstractmethod
    def q_activations(self) -> Query[TActivation]:
        """Return an iterator on all activations."""

    @abstractmethod
    def get_activation_by_code(self, code: str) -> Optional[TActivation]:
        """Return the Activation with ``code``, or None."""

    @abstractmethod
    def delete_activation(self, user: TTUser, activation: TActivation) -> None:
        """Delete the Activation instance from the database."""

    @abstractmethod
    def delete_expired_activations(
        self, now: Optional[datetime] = None
    ) -> int:
        """Delete all old activations."""

    @abstractmethod
    def get_or_create_user_by_email(
        self, email: str, details: DictStr
    ) -> TTUser:
        """Return User if ``email`` exists, else create it with ``details``."""

    @abstractmethod
    def q_users(self) -> Query[TTUser]:
        """Return a query for all users."""
