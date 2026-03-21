# noqa
from dataclasses import dataclass, field
from typing import Optional, Protocol

from kerno.bases import Kerno
from kerno.event import EventHub
from kerno.protocols import IConfig
from kerno.peto import AbsUserlessPeto, DictStr
from kerno.web.pyramid.typing import KRequest

from pluserable.data.repository import AbstractRepo
from pluserable.data.typing import TUser


class PConfig(IConfig, Protocol):
    """Protocol for an application's configuration object."""

    pluserable: DictStr  # A map of names to importables


@dataclass
class PKerno(Kerno):
    """Core of an application, integrating decoupled resources."""

    # Override config to replace its type with our own:
    config: PConfig  # for validated configuration
    # Add instance variables:
    events: EventHub = field(default_factory=EventHub)
    pluserable_settings: DictStr = field(default_factory=dict)  # validated, resolved


class PRequest(KRequest):
    """Typing stub for a Pyramid/kerno request object.

    It is recommended that you subclass with a more specific
    typing annotation for the ``user`` instance variable.
    """

    kerno: PKerno  # override the type
    repo: AbstractRepo  # override the type
    user: Optional[TUser]


UserlessPeto = AbsUserlessPeto[AbstractRepo, PKerno]
# Peto = AbstractPeto[AbstractRepo, TUser]
