"""Pluserable integration for the Pyramid web framework."""

from bag.settings import SettingsReader
from pyramid.security import unauthenticated_userid
from pluserable import initialize_kerno, EmailStrategy, UsernameStrategy
from pluserable.forms import SubmitForm
from pluserable.interfaces import (
    IDBSession, IKerno, ILoginForm, ILoginSchema,
    IRegisterForm, IRegisterSchema, IForgotPasswordForm, IForgotPasswordSchema,
    IResetPasswordForm, IResetPasswordSchema, IProfileForm, IProfileSchema)
from pluserable.data.repository import instantiate_repository
from .resources import RootFactory


def get_user(request):
    """Return the user making the current request, or None."""
    userid = unauthenticated_userid(request)
    if userid is None:
        return None
    return request.replusitory.q_user_by_id(userid)


def find_or_create_kerno(registry):
    """Try to find Kerno in the registry, then initialize it."""
    kerno = registry.queryUtility(IKerno, default=None)
    if kerno:
        return kerno

    # Kerno is not yet registered, so let's create it:
    config_path = registry.settings.get('__file__')
    if not config_path:
        raise RuntimeError('pluserable needs a "__file__" setting containing '
                           'the path to the configuration file.')
    kerno = initialize_kerno(config_path)
    registry.registerUtility(kerno, IKerno)
    return kerno


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    registry = config.registry
    # Ensure, at startup, that a SQLAlchemy session factory was configured:
    assert registry.queryUtility(IDBSession), 'No SQLAlchemy session ' \
        'factory has been configured before including pluserable!'

    settings = registry.settings
    config.add_request_method(get_user, 'user', reify=True)  # request.user
    config.set_root_factory(RootFactory)
    settings_reader = SettingsReader(settings)

    config.add_request_method(  # request.replusitory
        lambda request: instantiate_repository(request.registry),
        'replusitory', reify=True)

    # User code may create a setting "pluserable_configurator" that points
    # to a callable that we call here:
    configurator = settings_reader.resolve(
        key='pluserable_configurator',
        default='pluserable.settings:get_default_pluserable_settings')
    settings['pluserable'] = configurator(config)

    find_or_create_kerno(registry)

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
