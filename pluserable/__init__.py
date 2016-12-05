"""Pluserable is a user registration and login library."""

from mundi.core import Mundi
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


class BaseStrategy(object):

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


def initialize_mundi(config_path, mundi=None):
    """Initialize the core system, below the web framework."""
    mundi = mundi or Mundi.from_ini(config_path)

    # Persistence is done by a Repository class. The default uses SQLAlchemy:
    mundi.set_default_utility(
        const.REPOSITORY, 'pluserable.data.sqlalchemy.repository:Repository')

    # The UI text can be changed; by default we use UIStringsBase itself:
    mundi.set_default_utility(const.STRING_CLASS,
                              'pluserable.strings:UIStringsBase')
    return mundi


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    config.include('pluserable.web.pyramid')
