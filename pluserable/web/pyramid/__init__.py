"""Pluserable integration for the Pyramid web framework."""

from bag.settings import SettingsReader
from pyramid.security import unauthenticated_userid
from pluserable import initialize_mundi, EmailStrategy, UsernameStrategy
from pluserable.forms import SubmitForm
from pluserable.interfaces import (
    IUIStrings, IMundi, ILoginForm, ILoginSchema,
    IRegisterForm, IRegisterSchema, IForgotPasswordForm, IForgotPasswordSchema,
    IResetPasswordForm, IResetPasswordSchema, IProfileForm, IProfileSchema)
from pluserable.repository import instantiate_repository
from pluserable.resources import RootFactory


def get_user(request):
    """Return the user making the current request, or None."""
    userid = unauthenticated_userid(request)
    if userid is None:
        return None
    repo = instantiate_repository(request.registry)
    return repo.get_by_id(request, userid)


''' TODO REMOVE
def register_mundi_utility(config, name: str, utility):
    """Configurator directive that registers a utility with mundi.

    Example usage::

        config.register_mundi_utility('sas', my_scoped_session)
    """
    assert isinstance(name, str), 'The "name" argument must be a string.'
    from pluserable.interfaces import IMundi
    mundi = config.registry.queryUtility(IMundi)
    mundi.register_utility(name, utility)

# config.add_directive('register_mundi_utility', register_mundi_utility)
'''


def find_or_create_mundi(registry):
    """Try to find Mundi in the registry, then initialize it."""
    config_path = registry.settings.get('__file__')
    if not config_path:
        raise RuntimeError('pluserable needs a "__file__" setting containing '
                           'the path to the configuration file.')
    mundi = initialize_mundi(
        config_path, mundi=registry.queryUtility(IMundi, default=None))
    registry.registerUtility(mundi, IMundi)
    return mundi


def includeme(config):
    """Integrate pluserable into a Pyramid web app."""
    registry = config.registry
    settings = registry.settings
    config.add_request_method(get_user, 'user', reify=True)  # request.user
    config.set_root_factory(RootFactory)
    settings_reader = SettingsReader(settings)

    # User code may create a setting "pluserable_configurator" that points
    # to a callable that we call here:
    configurator = settings_reader.resolve(
        key='pluserable_configurator',
        default='pluserable.settings:get_default_pluserable_settings')
    settings['pluserable'] = configurator(config)

    find_or_create_mundi(registry)

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
