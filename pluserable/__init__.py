"""Pluserable is a user registration and login library."""

from kerno.start import Eko
from pluserable import const
from pluserable.configuration import validate_pluserable_config
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
    eko.add_repository_mixin(  # type: ignore[attr-defined]
        mixin=eko.kerno.utilities[const.REPOSITORY]
    )

    # The UI text can be changed; by default we use UIStringsBase itself:
    eko.utilities.set_default(const.STRING_CLASS, "pluserable.strings:UIStringsBase")

    # pluserable provides functions that send very simple email messages.
    # These functions can be replaced by the application.
    eko.utilities.set_default(
        "pluserable.send_activation_email",
        "pluserable.actions:send_activation_email",
    )
    eko.utilities.set_default(
        "pluserable.send_reset_password_email",
        "pluserable.actions:send_reset_password_email",
    )

    # Other settings are read from the [pluserable] configuration section:
    try:
        section = eko.kerno.settings["pluserable"]
    except Exception:
        section = {}
    eko.kerno.pluserable_settings = (  # type: ignore[attr-defined]
        validate_pluserable_config(section)
    )

    # If redis_url configured, use redis by default
    if eko.kerno.pluserable_settings.get("redis_url"):  # type: ignore[attr-defined]
        bfc = "pluserable.no_bruteforce:BruteForceAidRedis"
    else:
        bfc = "pluserable.no_bruteforce:BruteForceAidDummy"
    eko.utilities.set_default("brute force class", bfc)


def includeme(config):
    """Integrate pluserable with a Pyramid web app."""
    config.include("pluserable.web.pyramid")
