"""Pluserable is a user registration and login library."""

from typing import List

from bag.settings import SettingsReader
from kerno.start import Eko

from pluserable import const
from pluserable.interfaces import (
    ILoginSchema,
    IRegisterSchema,
    IForgotPasswordSchema,
    IResetPasswordSchema,
    IProfileSchema,
)
from pluserable.schemas import (
    ForgotPasswordSchema,
    UsernameLoginSchema,
    UsernameRegisterSchema,
    UsernameResetPasswordSchema,
    UsernameProfileSchema,
    EmailLoginSchema,
    EmailRegisterSchema,
    EmailResetPasswordSchema,
    EmailProfileSchema,
)


def groupfinder(userid, request) -> List[str]:
    """Return the main principals of the current user."""
    user = request.user
    groups = None
    if user:
        groups = []
        for group in user.groups:
            groups.append("group:%s" % group.name)
        groups.append("user:%s" % user.id)
    return groups


class BaseStrategy:

    defaults = [(IForgotPasswordSchema, ForgotPasswordSchema)]

    @classmethod
    def set_up(cls, config):
        for iface, default in cls.defaults:
            if not config.registry.queryUtility(iface):
                config.registry.registerUtility(default, iface)


class UsernameStrategy(BaseStrategy):

    defaults = BaseStrategy.defaults + [
        (ILoginSchema, UsernameLoginSchema),
        (IRegisterSchema, UsernameRegisterSchema),
        (IResetPasswordSchema, UsernameResetPasswordSchema),
        (IProfileSchema, UsernameProfileSchema),
    ]


class EmailStrategy(BaseStrategy):

    defaults = BaseStrategy.defaults + [
        (ILoginSchema, EmailLoginSchema),
        (IRegisterSchema, EmailRegisterSchema),
        (IResetPasswordSchema, EmailResetPasswordSchema),
        (IProfileSchema, EmailProfileSchema),
    ]


def eki(eko: Eko) -> None:
    """Initialize the Pluserable core (isolated from any web framework)."""
    # Persistence is done by a Repository class. The default uses SQLAlchemy:
    eko.include("kerno.repository")  # adds add_repository_mixin() to eko
    eko.utilities.set_default(
        const.REPOSITORY, "pluserable.data.sqlalchemy.repository:Repository"
    )
    eko.add_repository_mixin(  # type: ignore
        mixin=eko.kerno.utilities[const.REPOSITORY]
    )

    # The UI text can be changed; by default we use UIStringsBase itself:
    eko.utilities.set_default(
        const.STRING_CLASS, "pluserable.strings:UIStringsBase"
    )

    # Other settings are read from the [pluserable] configuration section:
    try:
        section = eko.kerno.settings["pluserable"]
    except Exception:
        section = {}
    eko.kerno.pluserable_settings = SettingsReader(section)  # type: ignore


def includeme(config):
    """Integrate pluserable with a Pyramid web app."""
    config.include("pluserable.web.pyramid")
