"""Event classes."""

from kerno.typing import DictStr


class EventLogin:
    """Fired when a user authenticates."""

    def __init__(self, peto, rezulto):  # noqa
        self.peto = peto
        self.rezulto = rezulto


class EventProfileUpdated:
    """Fired when a user changes email or password."""

    def __init__(self, request, user, values: DictStr, old_email: str):  # noqa
        self.request = request
        self.user = user
        self.values = values
        self.old_email = old_email


class BaseEvent:

    def __init__(self, request, user):  # noqa
        self.request = request
        self.user = user


class NewRegistrationEvent(BaseEvent):

    def __init__(self, request, user, activation, values):  # noqa
        super(NewRegistrationEvent, self).__init__(request, user)
        self.activation = activation
        self.values = values


class RegistrationActivatedEvent(BaseEvent):

    def __init__(self, request, user, activation):  # noqa
        super(RegistrationActivatedEvent, self).__init__(request, user)
        self.activation = activation


class PasswordResetEvent(BaseEvent):

    def __init__(self, request, user, password):  # noqa
        super(PasswordResetEvent, self).__init__(request, user)
        self.password = password
