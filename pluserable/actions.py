"""The **action** layer is also called "service" layer.

It stands between the model layer and the view layer.
It is the heart of an application and contains its business rules.

This is because MVC/MVT is insufficient for large apps. Views should
be thin.  Business rules must be decoupled from the web framework.
"""

from datetime import datetime
from typing import Any, Optional

from bag.reify import reify
from kerno.action import Action
from kerno.state import MalbonaRezulto, Rezulto
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from pluserable import const
from pluserable.data.typing import TUser
from pluserable.events import EventLogin
from pluserable.exceptions import AuthenticationFailure
from pluserable.data.repository import AbstractRepo
from pluserable.strings import get_strings, UIStringsBase


def get_activation_link(request, user_id: int, code: str) -> str:
    """Return the link for the user to click on an email message.

    ``route_url()`` uses the protocol and domain detected from the
    current request.  Unfortunately in production, that's usually
    https for the load balancer, but http for a backend Pyramid server.
    So we take advantage of a ``scheme_domain_port`` configuration
    setting if provided.
    """
    scheme_domain_port: str = request.registry.settings.get(
        "scheme_domain_port", ""
    )
    return (
        scheme_domain_port
        + request.route_path("activate", user_id=user_id, code=code)
        if scheme_domain_port
        else request.route_url("activate", user_id=user_id, code=code)
    )


def create_activation(request, user):  # TODO Lose *request* argument
    """Associate the user with a new activation, or keep the existing one.

    Also send an email message with the link for the user to click.
    """
    repo = request.repo
    if user.activation is None:
        Activation = request.kerno.utilities[const.ACTIVATION_CLASS]
        activation = Activation()
        repo.add(activation)
        user.activation = activation
        repo.flush()

    # The application can configure a function that sends the email message.
    send_activation_email = request.kerno.utilities[
        "pluserable.send_activation_email"
    ]
    send_activation_email(request, user)


def send_activation_email(request, user):
    """Send an extremely simple email message with the activation link.

    Although this works fine, most apps will want to build a personalized
    email message and send it via celery or something else asynchronous.
    """
    strings = get_strings(request.kerno)
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


def get_reset_link(request, code: str) -> str:
    """Return the link for the user to click on an email message.

    ``route_url()`` uses the protocol and domain detected from the
    current request.  Unfortunately in production, that's usually
    https for the load balancer, but http for a backend Pyramid server.
    So we take advantage of a ``scheme_domain_port`` configuration
    setting if provided.
    """
    scheme_domain_port: str = request.registry.settings.get(
        "scheme_domain_port", ""
    )
    return (
        scheme_domain_port
        + request.route_path("reset_password", code=code)
        if scheme_domain_port
        else request.route_url("reset_password", code=code)
    )


def send_reset_password_email(request, user):
    """Send an extremely simple email message with a link.

    Although this works fine, most apps will want to build a personalized
    email message and send it via celery or something else asynchronous.
    """
    username = (
        getattr(user, "short_name", "")
        or getattr(user, "full_name", "")
        or getattr(user, "username", "")
        or user.email
    )
    strings = get_strings(request.kerno)
    body = strings.reset_password_email_body.format(
        link=get_reset_link(request, code=user.activation.code),
        username=username,
        domain=request.application_url,
    )
    subject = strings.reset_password_email_subject
    message = Message(subject=subject, recipients=[user.email], body=body)
    mailer = get_mailer(request)
    mailer.send(message)


class PluserableAction(Action):
    """Base class for our actions."""

    repo: AbstractRepo  # let mypy know about our repo interface

    @reify
    def _strings(self) -> UIStringsBase:
        return get_strings(self.kerno)


def require_activation_setting_value(kerno) -> bool:
    """Return the value of a certain setting."""
    return kerno.pluserable_settings.bool("require_activation", default=True)


class CheckCredentials(PluserableAction):
    """Business rules decoupled from the web framework and from persistence."""

    @property
    def _require_activation(self):
        return require_activation_setting_value(self.kerno)

    def q_user(self, handle: str) -> Optional[TUser]:
        """Fetch user. ``handle`` can be a username or an email."""
        if "@" in handle:
            return self.repo.get_user_by_email(handle)
        else:
            return self.repo.get_user_by_username(handle)

    def __call__(self, handle: str, password: str) -> Rezulto:
        """Get user object if credentials are valid, else raise."""
        rezulto: Any = Rezulto()
        rezulto.user = self.q_user(handle)  # IO
        self._check_credentials(rezulto.user, handle, password)  # might raise
        assert rezulto.user
        rezulto.user.last_login_date = datetime.utcnow()
        self.kerno.events.broadcast(
            EventLogin(peto=self.peto, rezulto=rezulto)
        )
        return rezulto

    def _check_credentials(
        self, user: Optional[TUser], handle: str, password: str
    ) -> TUser:
        """Pure method (no IO) that checks credentials against ``user``."""
        if not user or not user.check_password(password):
            raise AuthenticationFailure(
                self._strings.wrong_email
                if "@" in handle
                else self._strings.wrong_username
            )

        if self._require_activation and not user.is_activated:
            raise AuthenticationFailure(self._strings.inactive_account)
        return user


class ActivateUser(PluserableAction):  # noqa
    def __call__(self, code: str, user_id: int) -> Rezulto:
        """Find code, ensure belongs to user, delete activation instance."""
        activation = self.repo.get_activation_by_code(code)
        if not activation:
            raise MalbonaRezulto(
                status_int=404,
                title=self._strings.activation_code_not_found_title,
                plain=self._strings.activation_code_not_found,
            )

        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise MalbonaRezulto(
                status_int=404,
                title=self._strings.user_not_found_title,
                plain=self._strings.user_not_found,
            )

        if user.activation is not activation:
            raise MalbonaRezulto(
                status_int=404,
                title=self._strings.activation_code_not_match_title,
                plain=self._strings.activation_code_not_match,
            )

        self.repo.delete_activation(user, activation)
        ret = Rezulto()  # type: Any
        ret.user = user
        ret.activation = activation

        # TODO My current flash messages do not display titles
        # ret.add_message(
        #     title=self._strings.activation_email_verified_title,
        #     plain=self._strings.activation_email_verified)
        return ret
