"""Pluserable is a user registration and login library."""

from bag.settings import SettingsReader
from pluserable.web.pyramid import get_user
from .schemas import (
    ForgotPasswordSchema, UsernameLoginSchema, UsernameRegisterSchema,
    UsernameResetPasswordSchema, UsernameProfileSchema, EmailLoginSchema,
    EmailRegisterSchema, EmailResetPasswordSchema, EmailProfileSchema)
from .forms import SubmitForm
from .resources import RootFactory
from .interfaces import (
    IUIStrings, IRepositoryClass, ILoginForm, ILoginSchema,
    IRegisterForm, IRegisterSchema, IForgotPasswordForm, IForgotPasswordSchema,
    IResetPasswordForm, IResetPasswordSchema, IProfileForm, IProfileSchema)
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


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    registry = config.registry
    settings = registry.settings
    config.add_request_method(get_user, 'user', reify=True)
    config.set_root_factory(RootFactory)
    settings_reader = SettingsReader(settings)

    # User code may create a setting "pluserable_configurator" that points
    # to a callable that we call here:
    configurator = settings_reader.resolve(
        key='pluserable_configurator',
        default='pluserable.settings:get_default_pluserable_settings')
    settings['pluserable'] = configurator(config)

    # Persistence is done by a Repository class. The default uses SQLAlchemy:
    repo_class = settings_reader.resolve(
        'pluserable_repository', default='pluserable.repository.sqlalchemy:Repository')
    registry.registerUtility(repo_class, IRepositoryClass)

    # SubmitForm is the default for all our forms
    for form in (ILoginForm, IRegisterForm, IForgotPasswordForm,
                 IResetPasswordForm, IProfileForm):
        if not registry.queryUtility(form):
            registry.registerUtility(SubmitForm, form)

    # Default schemas depend on login handle configuration:
    handle_config = settings.get('pluserable.handle', 'username')
    if handle_config in ('username', 'username+email', 'email+username'):
        UsernameStrategy.set_up(config)
    elif handle_config == 'email':
        EmailStrategy.set_up(config)
    else:
        raise RuntimeError(
            'Invalid config value for pluserable.handle: {}'.format(
                handle_config))

    config.include('bag.web.pyramid.flash_msg')
    config.include('pluserable.views')
