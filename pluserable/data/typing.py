"""Typing stubs for us to be able to write the code with type checking."""

from datetime import datetime
from typing import Generic, TypeVar

TActivation = TypeVar("TActivation")
TGroup = TypeVar("TGroup")


class TUser(Generic[TActivation, TGroup]):
    """Typing stub for a concrete User class."""

    email: str
    password: str
    salt: str
    activation: TActivation
    is_activated: bool
    last_login_date: datetime

    def check_password(self, password: str) -> bool:
        """Check the ``password`` and return a boolean."""
        ...
