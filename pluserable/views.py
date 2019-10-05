"""Views for Pyramid applications."""

from abc import ABCMeta
import logging
from typing import Optional

import colander
import deform
from kerno.state import to_dict
from kerno.web.pyramid import kerno_view, IKerno
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.security import remember, forget, Authenticated
from pyramid.settings import asbool
from pyramid.url import route_url
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pluserable import const
from pluserable.actions import (
    ActivateUser,
    CheckCredentials,
    require_activation_setting_value,
    get_activation_link,
)
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
    NewRegistrationEvent,
    RegistrationActivatedEvent,
    PasswordResetEvent,
    ProfileUpdatedEvent,
)
from pluserable.exceptions import AuthenticationFailure, FormValidationFailure
from pluserable.httpexceptions import HTTPBadRequest
from pluserable.strings import get_strings

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


def get_config_route(request, config_key: str) -> str:
    """Resolve ``config_key`` to a URL, usually for redirection."""
    settings = request.registry.settings
    try:
        return request.route_url(settings[config_key])
    except KeyError:
        return settings[config_key]


def authenticated(request, userid) -> HTTPFound:
    """Set the auth cookies and redirect.

    ...either to the URL indicated in the "next" request parameter,
    or to the page defined in pluserable.login_redirect,
    which defaults to a view named 'index'.
    """
    autologin = asbool(
        request.registry.settings.get("pluserable.autologin", False)
    )
    msg = get_strings(request.registry).login_done
    if not autologin and msg:
        request.add_flash(plain=msg, level="success")
    return HTTPFound(
        headers=remember(request, userid),
        location=request.params.get("next")
        or get_config_route(request, "pluserable.login_redirect"),
    )


def create_activation(request, user):  # TODO Move to action
    """Associate ``user`` with a new activation or keep the existing one.

    Also send an email message to ``user`` with the link for her to click.
    """
    if user.activation is None:
        kerno = request.registry.getUtility(IKerno)
        Activation = kerno.utilities[const.ACTIVATION_CLASS]
        activation = Activation()

        repo = request.repo
        repo.store_activation(activation)
        user.activation = activation
        repo.flush()

    strings = get_strings(kerno)
    message = Message(
        subject=strings.activation_email_subject,
        recipients=[user.email],
        body=strings.activation_email_plain.replace(
            "ACTIVATION_LINK",
            get_activation_link(
                request, user_id=user.id, code=user.activation.code
            ),
        ),
    )
    mailer = get_mailer(request)
    mailer.send(message)


def render_form(request, form, appstruct=None, **kw):
    settings = request.registry.settings
    retail = asbool(settings.get("pluserable.deform_retail", False))

    if appstruct is not None:
        form.set_appstruct(appstruct)

    if not retail:
        form = form.render()

    result = {"form": form}
    result.update(kw)
    return result


def validate_form(controls, form):
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
    def request(self):
        """Return the current request."""
        # we defined this so that we can override the request in tests easily
        return self._request

    def __init__(self, request):  # TODO REMOVE MOST OF THESE LINES
        self._request = request
        self.Activation = request.kerno.utilities[const.ACTIVATION_CLASS]
        self.User = request.kerno.utilities[const.USER_CLASS]
        self.settings = request.registry.settings

    @reify
    def strings(self):
        """Keep the strings class memoized."""
        return get_strings(self.request.kerno)


class AuthView(BaseView):
    """View that does login and logout."""

    def __init__(self, request):  # noqa
        super(AuthView, self).__init__(request)

        # TODO These shouldn't be computed every time... But run tests
        self.login_redirect_view = get_config_route(
            request, "pluserable.login_redirect"
        )
        self.logout_redirect_view = get_config_route(
            request, "pluserable.logout_redirect"
        )

        schema = request.registry.getUtility(ILoginSchema)
        self.schema = schema().bind(request=request)

        form = request.registry.getUtility(ILoginForm)
        self.form = form(self.schema, buttons=(self.strings.login_button,))

    def login_ajax(self):  # TODO ADD TESTS FOR THIS!
        try:
            cstruct = self.request.json_body
        except ValueError as e:
            raise HTTPBadRequest({"invalid": str(e)})

        try:
            captured = self.schema.deserialize(cstruct)
        except colander.Invalid as e:
            raise HTTPBadRequest({"invalid": e.asdict()})

        try:
            ret = CheckCredentials.from_pyramid(self.request)(
                handle=captured["handle"], password=captured["password"]
            )
        except AuthenticationFailure as e:
            raise HTTPBadRequest({"status": "failure", "reason": e.message})
        return {"status": "okay", "user": to_dict(ret.user)}

    def login(self, handle=None):
        """Present the login form, or validate data and authenticate user."""
        request = self.request
        if request.method == "GET":
            if request.user:
                return HTTPFound(location=self.login_redirect_view)
            return render_form(
                request,
                self.form,
                appstruct={"handle": handle} if handle else {},
            )

        elif request.method == "POST":
            controls = request.POST.items()
            try:  # TODO Move form validation into action
                captured = validate_form(controls, self.form)
            except FormValidationFailure as e:
                return e.result(request)

            try:
                ret = CheckCredentials.from_pyramid(request)(
                    handle=captured["handle"], password=captured["password"]
                )
            except AuthenticationFailure as e:  # TODO View for this exception
                request.add_flash(plain=str(e), level="danger")
                return render_form(request, self.form, captured, errors=[e])
            request.user = ret.user
            return authenticated(request, ret.user.id)

    def logout(self, url: Optional[str] = None) -> HTTPFound:
        """Remove the auth cookies and redirect...

        ...to the view defined in the ``pluserable.logout_redirect`` setting,
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


class ForgotPasswordView(BaseView):
    def __init__(self, request):  # noqa
        super(ForgotPasswordView, self).__init__(request)

        self.forgot_password_redirect_view = route_url(
            self.settings.get("pluserable.forgot_password_redirect", "index"),
            request,
        )
        self.reset_password_redirect_view = route_url(
            self.settings.get("pluserable.reset_password_redirect", "index"),
            request,
        )

    def forgot_password(self) -> HTTPFound:  # TODO Extract action
        """Show or process the "forgot password" form.

        Create a token and send email for user to click link.
        """
        request = self.request
        schema = request.registry.getUtility(IForgotPasswordSchema)
        schema = schema().bind(request=request)

        form = request.registry.getUtility(IForgotPasswordForm)
        form = form(schema)

        if request.method == "GET":
            if request.user:
                return HTTPFound(location=self.forgot_password_redirect_view)
            else:
                return render_form(request, form)

        # From here on, we know it's a POST. Let's validate the form
        controls = request.POST.items()

        try:
            captured = validate_form(controls, form)
        except FormValidationFailure as e:
            return e.result(request)

        repo = request.repo
        user = repo.get_user_by_email(captured["email"])
        if user.activation is None:  # If user already has activation, reuse it
            activation = self.Activation()  # TODO add test for this condition
            user.activation = activation
            repo.flush()  # initialize activation.code

        # TODO: Generate msg in a separate method so subclasses can override
        mailer = get_mailer(request)
        username = (
            getattr(user, "short_name", "")
            or getattr(user, "full_name", "")
            or getattr(user, "username", "")
            or user.email
        )
        body = self.strings.reset_password_email_body.format(
            link=route_url(
                "reset_password", request, code=user.activation.code
            ),
            username=username,
            domain=request.application_url,
        )
        subject = self.strings.reset_password_email_subject
        message = Message(subject=subject, recipients=[user.email], body=body)
        mailer.send(message)

        request.add_flash(
            plain=self.strings.reset_password_email_sent, level="success"
        )
        return HTTPFound(location=self.reset_password_redirect_view)

    def reset_password(self):  # TODO Extract action
        """Show or process the "reset password" form.

        After user clicked link on email message.
        """
        request = self.request

        # Ensure the code in the URL brings us a real activation object
        code = request.matchdict.get("code", None)
        activation = request.repo.q_activation_by_code(code)
        if not activation:
            raise HTTPNotFound(self.strings.activation_code_not_found)

        # Ensure the activation is connected to a user. TODO fix
        user = request.repo.q_user_by_activation(activation)
        if user is None:
            raise RuntimeError(
                "How is it possible that I found the activation "
                f"{activation.code} but not a corresponding user?"
            )

        # If a user is logged in, log her off before doing anything
        if request.user:  # TODO add test
            return AuthView(request).logout(url=request.path_qs)

        schema = request.registry.getUtility(IResetPasswordSchema)
        schema = schema().bind(request=request)

        form = request.registry.getUtility(IResetPasswordForm)
        form = form(schema)

        if request.method == "GET":
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

            request.add_flash(
                plain=self.strings.reset_password_done, level="success"
            )
            request.registry.notify(
                PasswordResetEvent(request, user, password)
            )
            location = self.reset_password_redirect_view
            return HTTPFound(location=location)


class RegisterView(BaseView):
    def __init__(self, request):  # noqa
        super(RegisterView, self).__init__(request)
        schema = request.registry.getUtility(IRegisterSchema)
        self.schema = schema().bind(request=self.request)

        form = request.registry.getUtility(IRegisterForm)
        self.form = form(self.schema)

        self.after_register_url = route_url(
            self.settings.get("pluserable.register_redirect", "index"), request
        )
        self.after_activate_url = route_url(
            self.settings.get("pluserable.activate_redirect", "index"), request
        )

        # TODO reify:
        kerno = request.registry.getUtility(IKerno)
        self.require_activation = require_activation_setting_value(kerno)

    def register(self):
        request = self.request
        if request.method == "GET":
            if request.user:
                return HTTPFound(location=self.after_register_url)

            return render_form(request, self.form)

        elif request.method != "POST":
            return

        # If the request is a POST:
        controls = request.POST.items()

        try:
            captured = validate_form(controls, self.form)
        except FormValidationFailure as e:
            return e.result(request)

        # With the form validated, we know email and username are unique.
        user = self.persist_user(captured)

        autologin = asbool(self.settings.get("pluserable.autologin", False))

        if self.require_activation:
            create_activation(request, user)  # send activation email
            request.add_flash(
                plain=self.strings.activation_check_email, level="success"
            )
        elif not autologin:
            request.add_flash(
                plain=self.strings.registration_done, level="success"
            )

        request.registry.notify(
            NewRegistrationEvent(request, user, None, controls)
        )
        if autologin:
            request.repo.flush()  # in order to get the id
            return authenticated(request, user.id)
        else:  # not autologin: user must log in just after registering.
            return HTTPFound(location=self.after_register_url)

    def persist_user(self, controls):
        """To change how the user is stored, override this method."""
        # This generic method must work with any custom User class and any
        # custom registration form:
        user = self.User(**controls)
        self.request.repo.store_user(user)
        return user

    @kerno_view
    def activate(self):  # http://localhost:6543/activate/10/89008993e9d5
        request = self.request
        ret = ActivateUser.from_pyramid(request)(
            code=request.matchdict.get("code", None),
            user_id=request.matchdict.get("user_id", None),
        )

        request.add_flash(  # TODO Move into action
            plain=self.strings.activation_email_verified, level="success"
        )
        request.registry.notify(  # send a Pyramid event
            RegistrationActivatedEvent(request, ret.user, ret.activation)
        )
        # If an exception is raised in an event subscriber, this never runs:
        return HTTPFound(location=self.after_activate_url)


class ProfileView(BaseView):
    def profile(self):
        """Display a user profile."""
        user_id = self.request.matchdict.get("user_id", None)
        user = self.request.repo.q_user_by_id(user_id)
        if not user:
            raise HTTPNotFound()
        return {"user": user}

    def _get_form(self):
        schema = self.request.registry.getUtility(IProfileSchema)
        self.schema = schema().bind(request=self.request)

        form = self.request.registry.getUtility(IProfileForm)
        return form(self.schema)

    def edit_profile(self):
        """Let the user change her own email or password."""
        request = self.request
        user = request.user
        # if not user:  # substitute with effective_principals=Authenticated
        #     raise HTTPNotFound()

        form = self._get_form()

        if request.method == "GET":
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
                    return e.result(request, username=user.username)
                else:
                    return e.result(request)

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
                request.add_flash(
                    plain=self.strings.edit_profile_done, level="success"
                )
                request.registry.notify(
                    ProfileUpdatedEvent(request, user, captured)
                )
            return HTTPFound(location=request.url)


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
            "effective_principals": Authenticated,
            "renderer": "pluserable:templates/edit_profile.mako",
        },
    }
