"""Typing stubs for us to be able to write the code with type checking."""

from datetime import datetime
from typing import Generic, TypeVar

from kerno.state import Rezulto

from pluserable.data.models import ActivationBase

TActivation = TypeVar("TActivation")
TGroup = TypeVar("TGroup")
TTUser = TypeVar("TTUser")


class TUser(Generic[TActivation, TGroup]):
    """Typing stub for a concrete User class."""

    id: int
    email: str
    password: str
    salt: str
    activation: TActivation
    is_activated: bool
    last_login_date: datetime

    def check_password(self, password: str) -> bool:
        """Check the ``password`` and return a boolean."""
        ...


class UserRezulto(Rezulto):
    """Typing stub for a Rezulto object that includes an authenticated user."""

    user: TUser


class ActivationRezulto(UserRezulto):
    """Typing stub for a Rezulto with ``user`` and ``activation``."""

    activation: ActivationBase
