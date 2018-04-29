"""Pluserable is a user registration and login library."""

from bag.settings import SettingsReader
from kerno.start import Eko
from pluserable import const
from pluserable.interfaces import (
    ILoginSchema, IRegisterSchema, IForgotPasswordSchema,
    IResetPasswordSchema, IProfileSchema)
from pluserable.schemas import (
    ForgotPasswordSchema, UsernameLoginSchema, UsernameRegisterSchema,
    UsernameResetPasswordSchema, UsernameProfileSchema, EmailLoginSchema,
    EmailRegisterSchema, EmailResetPasswordSchema, EmailProfileSchema)


def groupfinder(userid, request):
    """Return the main principals of the current user."""
    user = request.user
    groups = None
    if user:
        groups = []
        for group in user.groups:
            groups.append('group:%s' % group.name)
        groups.append('user:%s' % user.id)
    return groups


class BaseStrategy:

    defaults = [
        (IForgotPasswordSchema, ForgotPasswordSchema),
    ]

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
        (IProfileSchema, UsernameProfileSchema)
    ]


class EmailStrategy(BaseStrategy):

    defaults = BaseStrategy.defaults + [
        (ILoginSchema, EmailLoginSchema),
        (IRegisterSchema, EmailRegisterSchema),
        (IResetPasswordSchema, EmailResetPasswordSchema),
        (IProfileSchema, EmailProfileSchema)
    ]


def initialize_kerno(config_path, eko=None):
    """Initialize the core system, isolated from the web framework."""
    eko = eko or Eko.from_ini(config_path)

    # Persistence is done by a Repository class. The default uses SQLAlchemy:
    eko.include('kerno.repository')  # adds add_repository_mixin() to eko
    eko.set_default_utility(
        const.REPOSITORY, 'pluserable.data.sqlalchemy.repository:Repository')
    eko.add_repository_mixin(mixin=eko.kerno.get_utility(const.REPOSITORY))

    # The UI text can be changed; by default we use UIStringsBase itself:
    eko.set_default_utility(const.STRING_CLASS,
                            'pluserable.strings:UIStringsBase')

    # Other settings are read from the [pluserable] section of the ini file:
    try:
        section = eko.kerno.settings['pluserable']
    except Exception:
        section = {}
    eko.kerno.pluserable_settings = SettingsReader(section)
    return eko


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    config.include('pluserable.web.pyramid')
