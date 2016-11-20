"""Pluserable is a user registration and login library."""

from mundi.core import Mundi
from .const import REPOSITORY, SAS
from .interfaces import (
    IUIStrings, IMundi, ILoginForm, ILoginSchema,
    IRegisterForm, IRegisterSchema, IForgotPasswordForm, IForgotPasswordSchema,
    IResetPasswordForm, IResetPasswordSchema, IProfileForm, IProfileSchema)
from .schemas import (
    ForgotPasswordSchema, UsernameLoginSchema, UsernameRegisterSchema,
    UsernameResetPasswordSchema, UsernameProfileSchema, EmailLoginSchema,
    EmailRegisterSchema, EmailResetPasswordSchema, EmailProfileSchema)
from .strings import UIStringsBase


def groupfinder(userid, request):
    user = request.user
    groups = None
    if user:
        groups = []
        for group in user.groups:
            groups.append('group:%s' % group.name)
        groups.append('user:%s' % user.id_value)
    return groups


class BaseStrategy(object):
    defaults = [
        (IUIStrings, UIStringsBase),
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
    mundi.set_default_utility(REPOSITORY,
                              'pluserable.repository.sqlalchemy:Repository')

    return mundi


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    config.include('pluserable.web.pyramid')
