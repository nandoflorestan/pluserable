"""Event classes."""

from kerno.peto import Peto
from kerno.typing import DictStr

from pluserable.data.typing import TUser, UserRezulto
from pluserable.web.pyramid.typing import PRequest


class BaseEvent:  # noqa
    def __init__(self, request: PRequest, user: TUser):  # noqa
        self.request = request
        self.user = user


class EventRegistration(BaseEvent):  # noqa
    def __init__(
        self,
        request: PRequest,
        user: TUser,
        values: DictStr,
        activation_is_required: bool,
    ):  # noqa
        super().__init__(request=request, user=user)
        self.activation_is_required = activation_is_required
        self.values = values


class EventActivation(BaseEvent):  # noqa
    def __init__(self, request: PRequest, user: TUser, activation):  # noqa
        super().__init__(request=request, user=user)
        self.activation = activation


class EventLogin(BaseEvent):
    """Fired when a user authenticates."""

    def __init__(
        self, request: PRequest, peto: Peto, rezulto: UserRezulto
    ):  # noqa
        super().__init__(request=request, user=rezulto.user)
        self.peto = peto
        self.rezulto = rezulto


class EventProfileUpdated(BaseEvent):
    """Fired when a user changes email or password."""

    def __init__(
        self, request: PRequest, user: TUser, values: DictStr, old_email: str
    ):  # noqa
        super().__init__(request=request, user=user)
        self.values = values
        self.old_email = old_email


class EventPasswordReset(BaseEvent):  # noqa
    def __init__(self, request: PRequest, user: TUser, password: str):  # noqa
        super().__init__(request=request, user=user)
        self.password = password
