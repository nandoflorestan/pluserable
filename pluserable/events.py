"""Event classes."""

from kerno.peto import Peto
from kerno.typing import DictStr

from pluserable.data.typing import TUser, UserRezulto
from pluserable.web.pyramid.typing import PRequest


class EventLogin:
    """Fired when a user authenticates."""

    def __init__(self, peto: Peto, rezulto: UserRezulto):  # noqa
        self.peto = peto
        self.rezulto = rezulto


class EventProfileUpdated:
    """Fired when a user changes email or password."""

    def __init__(
        self, request: PRequest, user: TUser, values: DictStr, old_email: str
    ):  # noqa
        self.request = request
        self.user = user
        self.values = values
        self.old_email = old_email


class BaseEvent:  # noqa
    def __init__(self, request: PRequest, user: TUser):  # noqa
        self.request = request
        self.user = user


class NewRegistrationEvent(BaseEvent):  # noqa
    def __init__(
        self, request: PRequest, user: TUser, activation, values
    ):  # noqa
        super(NewRegistrationEvent, self).__init__(request, user)
        self.activation = activation
        self.values = values


class RegistrationActivatedEvent(BaseEvent):  # noqa
    def __init__(self, request: PRequest, user: TUser, activation):  # noqa
        super(RegistrationActivatedEvent, self).__init__(request, user)
        self.activation = activation


class PasswordResetEvent(BaseEvent):  # noqa
    def __init__(self, request: PRequest, user: TUser, password: str):  # noqa
        super(PasswordResetEvent, self).__init__(request, user)
        self.password = password
