# noqa

from kerno.peto import AbsUserlessPeto
from kerno.web.pyramid.typing import KRequest

from pluserable.data.repository import AbstractRepo
from pluserable.data.typing import TUser


class PRequest(KRequest):
    """Typing stub for a Pyramid/kerno request object.

    It is recommended that you subclass with a more specific
    typing annotation for the ``user`` instance variable.
    """

    repo: AbstractRepo
    user: TUser


UserlessPeto = AbsUserlessPeto[AbstractRepo]
# Peto = AbstractPeto[AbstractRepo, TUser]
