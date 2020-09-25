"""Repository implementations.

Repositories are persistence strategies.
"""

from abc import ABCMeta, abstractmethod
from typing import Generic, Optional

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
