"""Pluserable integration for the Pyramid web framework."""

from bag.settings import SettingsReader

from pluserable import EmailStrategy, UsernameStrategy
from pluserable.forms import SubmitForm
from pluserable.interfaces import (
    ILoginForm,
    ILoginSchema,
    IRegisterForm,
    IRegisterSchema,
    IForgotPasswordForm,
    IForgotPasswordSchema,
    IResetPasswordForm,
    IResetPasswordSchema,
    IProfileForm,
    IProfileSchema,
)
from pluserable.web.pyramid.resources import RootFactory


def get_user(request):
    """Return the user making the current request, or None."""
    userid = request.unauthenticated_userid
    if userid is None:
        return None
    return request.repo.q_user_by_id(userid)


def includeme(config) -> None:
    """Integrate pluserable into a Pyramid web app.

    - Make ``request.user`` available.
    - Set our root factory for Pyramid URL traversal.
    - Call the ``pluserable_configurator`` indicated in
      the settings (or the default one).
    - Include other initializers from kerno and from pluserable.
    """
    registry = config.registry
    settings = registry.settings
    settings_reader = SettingsReader(settings)

    config.add_request_method(get_user, "user", reify=True)  # request.user
    config.set_root_factory(RootFactory)

    # User code may create a setting "pluserable_configurator" that points
    # to a callable that we call here:
    configurator = settings_reader.resolve(
        key="pluserable_configurator",
        default="pluserable.settings:get_default_pluserable_settings",
    )
    settings["pluserable"] = configurator()

    config.include("kerno.web.pyramid")

    # SubmitForm is the default for all our forms
    for form in (
        ILoginForm,
        IRegisterForm,
        IForgotPasswordForm,
        IResetPasswordForm,
        IProfileForm,
    ):
        if not registry.queryUtility(form):
            registry.registerUtility(SubmitForm, form)

    # Default schemas depend on login handle configuration:
    handle_config = settings.get("pluserable.handle", "username")
    if handle_config in ("username", "username+email", "email+username"):
        UsernameStrategy.set_up(config)
    elif handle_config == "email":
        EmailStrategy.set_up(config)
    else:
        raise RuntimeError(
            "Invalid config value for pluserable.handle: {}".format(
                handle_config
            )
        )

    config.include("kerno.web.msg_to_html")
    config.include("pluserable.views")
