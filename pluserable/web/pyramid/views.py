"""Views for Pyramid applications."""

from abc import ABCMeta
import logging
from typing import cast, Optional

import colander
import deform
from kerno.state import to_dict
from kerno.typing import DictStr
from kerno.web.pyramid import kerno_view, IKerno
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import forget, remember

from pluserable import const
from pluserable.actions import (
    ActivateUser,
    CheckCredentials,
    create_activation,
)
from pluserable.data.typing import TUser
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
from pluserable.events import (
    EventLogin,
    EventRegistration,
    EventActivation,
    EventPasswordReset,
    EventProfileUpdated,
)
from pluserable.exceptions import AuthenticationFailure, FormValidationFailure
from pluserable.httpexceptions import HTTPBadRequest
from pluserable.strings import get_strings
from pluserable.web.pyramid.resources import UserFactory
from pluserable.web.pyramid.typing import PRequest, UserlessPeto

LOG = logging.getLogger(__name__)


def includeme(config) -> None:
    """Set up pluserable routes and views in Pyramid."""
    settings = config.registry.settings["pluserable"]
    routes = settings["routes"]
    for name, kw in routes.items():
        config.add_route(name, **kw)
    for route_name, kw in settings["views"].items():
        if route_name in routes:
            config.add_view(route_name=route_name, **kw)
    if "login" in routes:
        config.add_view(
            route_name="login",
            xhr=True,
            accept="application/json",
            renderer="json",
            view=AuthView,
            attr="login_ajax",
        )


def get_config_route(request: PRequest, config_key: str) -> str:
    """Resolve ``config_key`` to a URL, usually for redirection."""
    settings = request.kerno.pluserable_settings  # type: ignore[attr-defined]
    try:
        return request.route_path(settings[config_key])
    except KeyError:
        return settings[config_key]


def authenticated(request: PRequest, userid: int) -> HTTPFound:
    """Set the auth cookies and redirect.

    ...either to the URL indicated in the "next" request parameter,
    or to the page defined in kerno.pluserable_settings["login_redirect"],
    which defaults to a view named 'index'.
    """
    autologin = request.kerno.pluserable_settings[  # type: ignore[attr-defined]
        "autologin"
    ]
    msg = get_strings(request.registry).login_done
    if not autologin and msg:
        request.add_flash(plain=msg, level="success")
    return HTTPFound(
        headers=remember(request, userid),
        location=request.params.get("next")
        or get_config_route(request, "login_redirect"),
    )


def render_form(request: PRequest, form, appstruct=None, **kw) -> DictStr:
    """Return the deform *form* rendered with *appstruct* data."""
    retail = request.kerno.pluserable_settings[  # type: ignore[attr-defined]
        "deform_retail"
    ]

    if appstruct is not None:
        form.set_appstruct(appstruct)

    if not retail:
        form = form.render()

    result = {"form": form}
    result.update(kw)
    return result


def validate_form(controls, form) -> DictStr:  # noqa
    try:
        captured = form.validate(controls)
    except deform.ValidationFailure as e:
        # NOTE(jkoelker) normally this is superfluous, but if the app is
        #                debug logging, then log that we "ate" the exception
        LOG.debug("Form validation failed", exc_info=True)
        raise FormValidationFailure(form, e)
    return captured


class BaseView(metaclass=ABCMeta):
    """Base class for pluserable views."""

    @property
    def request(self) -> PRequest:
        """Return the current request."""
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request: PRequest):  # noqa
        # TODO REMOVE MOST OF THESE LINES
        self._request = request
        self.Activation = request.kerno.utilities[const.ACTIVATION_CLASS]
        self.User: type = request.kerno.utilities[const.USER_CLASS]
        self.settings = request.registry.settings

    @reify
    def strings(self):
        """Keep the strings class memoized."""
        return get_strings(self.request.kerno)


class AuthView(BaseView):
    """View that does login and logout."""

    def __init__(self, request: PRequest):  # noqa
        super(AuthView, self).__init__(request)

        # TODO These shouldn't be computed every time... But run tests
        self.login_redirect_view = get_config_route(request, "login_redirect")
        self.logout_redirect_view = get_config_route(request, "logout_redirect")

        schema = request.registry.getUtility(ILoginSchema)
        self.schema = schema().bind(request=request, kerno=request.kerno)

        form = request.registry.getUtility(ILoginForm)
        self.form = form(self.schema, buttons=(self.strings.login_button,))

    def login_ajax(self) -> DictStr:  # noqa.  TODO ADD TESTS FOR THIS!
        request = self.request
        try:
            cstruct = request.json_body
        except ValueError as e:
            raise HTTPBadRequest({"invalid": str(e)})

        try:
            captured = self.schema.deserialize(cstruct)
        except colander.Invalid as e:
            raise HTTPBadRequest({"invalid": e.asdict()})

        try:
            upeto = UserlessPeto.from_pyramid(request)
            rezulto = CheckCredentials(upeto=upeto)(
                handle=captured["handle"],
                password=captured["password"],
                ip=request.client_addr,
            )
        except AuthenticationFailure as e:
            raise HTTPBadRequest({"status": "failure", "reason": str(e)})

        request.user = rezulto.user
        request.kerno.events.broadcast(  # trigger a kerno event
            EventLogin(request=request, upeto=upeto, rezulto=rezulto)
        )
        return {"status": "okay", "user": to_dict(rezulto.user)}

    def login(self, handle=None) -> DictStr:
        """Present the login form, or validate data and authenticate user."""
        request = self.request
        if request.method in ("GET", "HEAD"):
            if request.identity:
                return HTTPFound(location=self.login_redirect_view)
            return render_form(
                request,
                self.form,
                appstruct={"handle": handle} if handle else {},
            )
        elif request.method != "POST":
            raise RuntimeError(f"Login request method: {request.method}")

        # If this is a POST:
        controls = request.POST.items()
        try:  # TODO Move form validation into action
            captured = validate_form(controls, self.form)
        except FormValidationFailure as e:
            return e.result(request)

        upeto = UserlessPeto.from_pyramid(request)
        try:
            rezulto = CheckCredentials(upeto=upeto)(
                handle=captured["handle"],
                password=captured["password"],
                ip=request.client_addr,
            )
        except AuthenticationFailure as e:  # TODO View for this exception
            request.add_flash(plain=str(e), level="danger")
            return render_form(request, self.form, captured, errors=[e])

        request.user = rezulto.user
        request.kerno.events.broadcast(  # trigger a kerno event
            EventLogin(request=request, upeto=upeto, rezulto=rezulto)
        )
        return authenticated(request, rezulto.user.id)

    def logout(self, url: Optional[str] = None) -> HTTPFound:
        """Remove the auth cookies and redirect...

        ...to the view defined in the ``logout_redirect`` setting,
        which defaults to a view named 'index'.
        """
        request = self.request
        msg = self.strings.logout_done
        if msg:
            request.add_flash(plain=msg, level="success")
        request.session.invalidate()
        return HTTPFound(
            location=url or self.logout_redirect_view, headers=forget(request)
        )


class ForgotPasswordView(BaseView):  # noqa
    def forgot_password(self) -> HTTPFound:  # TODO Extract action
        """Show or process the "forgot password" form.

        Create a token and send email for user to click link.
        """
        request = self.request
        schema = request.registry.getUtility(IForgotPasswordSchema)
        schema = schema().bind(request=request, kerno=request.kerno)

        form = request.registry.getUtility(IForgotPasswordForm)
        form = form(schema)

        if request.method == "GET":
            if request.identity:
                return HTTPFound(
                    location=get_config_route(request, "forgot_password_redirect")
                )
            else:
                return render_form(request, form)

        # From here on, we know it's a POST. Let's validate the form
        controls = request.POST.items()

        try:
            captured = validate_form(controls, form)
        except FormValidationFailure as e:
            return e.result(request)

        repo = request.repo
        user = repo.one_user_by_email(captured["email"])
        # If user already has activation, reuse it
        if user.activation is None:  # TODO add test for this condition
            user.activation = self.Activation()
            repo.flush()  # initialize activation.code

        # The app can replace the function that sends the email message.
        send_reset_password_email = request.kerno.utilities[
            "pluserable.send_reset_password_email"
        ]
        send_reset_password_email(request, user)

        request.add_flash(plain=self.strings.reset_password_email_sent, level="success")
        return HTTPFound(location=get_config_route(request, "forgot_password_redirect"))

    def reset_password(self) -> DictStr:  # TODO Extract action
        """Show or process the "reset password" form.

        After user clicked link on email message.
        """
        request = self.request

        # Ensure the code in the URL brings us a real activation object
        code = request.matchdict.get("code", None)
        activation = request.repo.get_activation_by_code(code)
        if not activation:
            raise HTTPNotFound(self.strings.activation_code_not_found)

        # Ensure the activation is connected to a user. TODO fix
        user = request.repo.get_user_by_activation(activation)
        if user is None:
            raise RuntimeError(
                "How is it possible that I found the activation "
                f"{activation.code} but not a corresponding user?"
            )

        # If a user is logged in, log her off before doing anything
        if request.identity:  # TODO add test
            return AuthView(request).logout(url=request.path_qs)

        schema = request.registry.getUtility(IResetPasswordSchema)
        schema = schema().bind(request=request, kerno=request.kerno)

        form = request.registry.getUtility(IResetPasswordForm)
        form = form(schema)

        if request.method in ("GET", "HEAD"):
            appstruct = (
                {"username": user.username}
                if hasattr(user, "username")
                else {"email": user.email}
            )
            return render_form(request, form, appstruct)
        elif request.method == "POST":
            controls = request.POST.items()
            try:
                captured = validate_form(controls, form)
            except FormValidationFailure as e:
                return e.result(request)

            password = captured["password"]

            user.password = password
            request.repo.delete_activation(user, activation)

            request.add_flash(plain=self.strings.reset_password_done, level="success")
            request.kerno.events.broadcast(  # trigger a kerno event
                EventPasswordReset(request, user, password)
            )
            return HTTPFound(
                location=get_config_route(request, "reset_password_redirect")
            )
        else:
            raise RuntimeError(f"Reset password method: {request.method}")


class RegisterView(BaseView):  # noqa
    def __init__(self, request: PRequest):  # noqa
        super(RegisterView, self).__init__(request)
        schema = request.registry.getUtility(IRegisterSchema)
        self.schema = schema().bind(request=self.request, kerno=request.kerno)

        form = request.registry.getUtility(IRegisterForm)
        self.form = form(self.schema)

        # TODO reify:
        kerno = request.registry.getUtility(IKerno)
        self.require_activation = kerno.pluserable_settings["require_activation"]

    @property
    def _after_activate_url(self):
        return get_config_route(self.request, "activate_redirect")

    @property
    def _after_register_url(self):
        return get_config_route(self.request, "register_redirect")

    def register(self) -> DictStr:  # noqa.  TODO Extract action
        request = self.request
        if request.method in ("GET", "HEAD"):
            if request.identity:
                return HTTPFound(location=self._after_register_url)

            return render_form(request, self.form)

        elif request.method != "POST":
            raise RuntimeError(f"register() request method: {request.method}")

        # If the request is a POST:
        controls = request.POST.items()

        try:
            captured = validate_form(controls, self.form)
        except FormValidationFailure as e:
            return e.result(request)

        # With the form validated, we know email and username are unique.
        user = self.persist_user(captured)

        autologin = request.kerno.pluserable_settings[  # type: ignore[attr-defined]
            "autologin"
        ]

        if self.require_activation:
            create_activation(request, user)  # send activation email
            request.add_flash(
                plain=self.strings.activation_check_email, level="success"
            )
        elif not autologin:
            request.add_flash(plain=self.strings.registration_done, level="success")

        request.kerno.events.broadcast(  # trigger a kerno event
            EventRegistration(
                request=request,
                user=user,
                values=cast(DictStr, controls),
                activation_is_required=self.require_activation,
            )
        )
        if autologin:
            request.repo.flush()  # in order to get user.id
            return authenticated(request, user.id)
        else:  # not autologin: user must log in just after registering.
            return HTTPFound(location=self._after_register_url)

    def persist_user(self, controls: DictStr) -> TUser:
        """To change how the user is stored, override this method."""
        # This generic method must work with any custom User class and any
        # custom registration form:
        user = self.User(**controls)
        self.request.repo.add(user)
        return user

    @kerno_view
    def activate(self) -> HTTPFound:  # noqa
        # http://localhost:6543/activate/10/89008993e9d5
        request = self.request
        ret = ActivateUser(upeto=UserlessPeto.from_pyramid(request))(
            code=request.matchdict.get("code", None),
            user_id=request.matchdict.get("user_id", None),
        )

        request.add_flash(  # TODO Move into action
            plain=self.strings.activation_email_verified, level="success"
        )
        request.kerno.events.broadcast(  # trigger a kerno event
            EventActivation(request=request, user=ret.user, activation=ret.activation)
        )
        # If an exception is raised in an event subscriber, this never runs:
        return HTTPFound(location=self._after_activate_url)


class ProfileView(BaseView):  # noqa
    def profile(self) -> DictStr:
        """Display a user profile."""
        user_id = self.request.matchdict.get("user_id", None)
        user = self.request.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPNotFound()
        return {"user": user}

    def _get_form(self):
        schema = self.request.registry.getUtility(IProfileSchema)
        self.schema = schema().bind(request=self.request, kerno=self.request.kerno)

        form = self.request.registry.getUtility(IProfileForm)
        return form(self.schema)

    def edit_profile(self) -> DictStr:
        """Let the user change her own email or password."""
        request = self.request
        user = request.identity

        form = self._get_form()

        if request.method in ("GET", "HEAD"):
            appstruct = {"email": user.email or ""}
            if hasattr(user, "username"):
                appstruct["username"] = user.username
            return render_form(request, form, appstruct)
        elif request.method == "POST":
            controls = request.POST.items()

            try:
                captured = validate_form(controls, form)
            except FormValidationFailure as e:
                if hasattr(user, "username"):
                    # We pre-populate username
                    return e.result(
                        request,
                        username=user.username,
                    )
                else:
                    return e.result(request)

            old_email = user.email
            changed = False
            email = captured.get("email", None)
            if email:
                email_user = request.repo.get_user_by_email(email)
                if email_user and email_user.id != user.id:
                    # TODO This should be a validation error, not add_flash
                    request.add_flash(
                        plain=get_strings(
                            request.kerno
                        ).edit_profile_email_present.format(email=email),
                        level="danger",
                    )
                    return HTTPFound(location=request.url)
                # TODO When user changes email, she must activate again
                if email != user.email:
                    user.email = email
                    changed = True

            password = captured.get("password")
            if password:
                user.password = password
                changed = True

            if changed:
                request.kerno.events.broadcast(  # trigger a kerno event
                    EventProfileUpdated(
                        request=request,
                        user=user,
                        values=captured,
                        old_email=old_email,
                    )
                )
                request.add_flash(plain=self.strings.edit_profile_done, level="success")
            return HTTPFound(location=request.url)
        else:
            raise RuntimeError(f"edit_profile method: {request.method}")


def get_pyramid_views_config():
    """Return a dictionary for registering Pyramid views."""
    return {  # route_name: view_kwargs
        "register": {
            "view": RegisterView,
            "attr": "register",
            "renderer": "pluserable:templates/register.mako",
        },
        "activate": {"view": RegisterView, "attr": "activate"},
        "login": {
            "view": AuthView,
            "attr": "login",
            "renderer": "pluserable:templates/login.mako",
        },
        "logout": {"view": AuthView, "attr": "logout"},
        "forgot_password": {
            "view": ForgotPasswordView,
            "attr": "forgot_password",
            "renderer": "pluserable:templates/forgot_password.mako",
        },
        "reset_password": {
            "view": ForgotPasswordView,
            "attr": "reset_password",
            "renderer": "pluserable:templates/reset_password.mako",
        },
        "profile": {
            "view": ProfileView,
            "attr": "profile",
            "renderer": "pluserable:templates/profile.mako",
        },
        "edit_profile": {
            "view": ProfileView,
            "attr": "edit_profile",
            "is_authenticated": True,
            "renderer": "pluserable:templates/edit_profile.mako",
        },
    }


def get_default_pluserable_settings() -> DictStr:
    """Return default pluserable settings.

    In order to customize Pluserable to its purpose, user code calls this
    and manipulates the returned dictionary.  Here we return defaults
    that user code can change.
    """
    return {
        # Pyramid routes
        "routes": {  # route_name: route_kwargs
            "login": {"pattern": "/login"},
            "logout": {"pattern": "/logout"},
            "register": {"pattern": "/register"},
            "activate": {
                "pattern": "/activate/{user_id}/{code}",
                "factory": UserFactory,
            },
            "forgot_password": {"pattern": "/forgot_password"},
            "reset_password": {"pattern": "/reset_password/{code}"},
            "profile": {
                "pattern": "/profile/{user_id}",
                "factory": UserFactory,
                "traverse": "/{user_id}",
            },
            "edit_profile": {"pattern": "/edit_profile"},
        },
        # Pyramid views
        "views": get_pyramid_views_config(),
    }
