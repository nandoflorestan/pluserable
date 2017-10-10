"""Pluserable integration for the Pyramid web framework."""

from bag.settings import SettingsReader
from kerno.web.pyramid import IKerno
from pyramid.security import unauthenticated_userid
from pluserable import initialize_kerno, EmailStrategy, UsernameStrategy
from pluserable.forms import SubmitForm
from pluserable.interfaces import (
    ILoginForm, ILoginSchema,
    IRegisterForm, IRegisterSchema, IForgotPasswordForm, IForgotPasswordSchema,
    IResetPasswordForm, IResetPasswordSchema, IProfileForm, IProfileSchema)
from pluserable.data.repository import instantiate_repository
from .resources import RootFactory


def get_user(request):
    """Return the user making the current request, or None."""
    userid = unauthenticated_userid(request)
    if userid is None:
        return None
    return request.repo.q_user_by_id(userid)


def find_or_create_kerno(registry, ini_path):
    """Return kerno -- either found in the registry, or initialized here."""
    kerno = registry.queryUtility(IKerno, default=None)
    if kerno:
        initialize_kerno(ini_path, kerno)
    else:  # Kerno is not yet registered, so let's create and register it:
        kerno = initialize_kerno(ini_path)
        registry.registerUtility(kerno, IKerno)
    return kerno


def setup_pluserable(config, ini_path):
    """Integrate pluserable into a Pyramid web app.

    ``ini_path`` must be the path to an INI file.
    """
    registry = config.registry

    settings = registry.settings
    config.add_request_method(get_user, 'user', reify=True)  # request.user
    config.set_root_factory(RootFactory)
    settings_reader = SettingsReader(settings)

    config.add_request_method(  # request.repo
        lambda request: instantiate_repository(request.registry),
        'repo', reify=True)

    # User code may create a setting "pluserable_configurator" that points
    # to a callable that we call here:
    configurator = settings_reader.resolve(
        key='pluserable_configurator',
        default='pluserable.settings:get_default_pluserable_settings')
    settings['pluserable'] = configurator(config)

    find_or_create_kerno(registry, ini_path)
    config.include('kerno.web.pyramid')

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


def includeme(config):
    """Pyramid integration. Add a configurator directive to be used next."""
    config.add_directive('setup_pluserable', setup_pluserable)
