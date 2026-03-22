# noqa
from dataclasses import dataclass, field
from typing import Optional, Protocol

from kerno.bases import Kerno, DictStr, UserlessPeto as UPeto, Peto as KPeto
from kerno.event import EventHub
from kerno.protocols import IConfig
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

    It is recommended that you subclass with more specific typing annotations
    for each instance variable.
    """

    kerno: PKerno  # override the type
    repo: AbstractRepo  # override the type
    user: Optional[TUser]


@dataclass
class PUserlessPeto(UPeto):
    """Convenience type for actions NOT done by a logged user.

    An application should subclass this to replace variable types.
    """

    kerno: PKerno  # override type of the global application object
    repo: AbstractRepo  # override type of the data access layer


@dataclass
class PPeto(PUserlessPeto, KPeto):
    """Convenience type for actions done by a logged user."""

    user: TUser  # the current user requesting an operation. Not None!
