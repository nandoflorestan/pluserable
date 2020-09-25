"""Repository implementations.

Repositories are persistence strategies.
"""

from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, Sequence

from pluserable.data.typing import TActivation, TGroup, TTUser


class AbstractRepo(Generic[TActivation, TGroup, TTUser], metaclass=ABCMeta):
    """An abstract base class (ABC) defining the repository interface."""

    # TODO Complete this ABC

    User: TTUser
    Activation: TActivation
    Group: TGroup

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
    def q_groups(self) -> Sequence[TGroup]:
        """Return an iterator on all groups."""

    @abstractmethod
    def q_activations(self) -> Sequence[TActivation]:
        """Return an iterator on all activations."""

    @abstractmethod
    def get_activation_by_code(self, code: str) -> Optional[TActivation]:
        """Return the Activation with ``code``, or None."""
