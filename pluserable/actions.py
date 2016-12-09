"""The **action** layer is also called "service" layer.

It stands between the model layer and the view layer.
It is the heart of an application and contains its business rules.

This is because MVC/MVT is insufficient for large apps. Views should
be thin.  Business rules must be decoupled from the web framework.
"""

from bag.settings import SettingsReader
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from kerno.action import Action
from pluserable.exceptions import AuthenticationFailure
from pluserable.interfaces import IKerno
from pluserable.strings import get_strings


def register_operations(kerno):
    """At startup register our operations (made of actions) with kerno."""
    kerno.register_operation(name='Log in', actions=[CheckCredentials])
    kerno.register_operation(name='Activate user', actions=[ActivateUser])


def instantiate_action(cls, request, payload: dict, user=None):  # TODO REMOVE
    """Convenience function to be used from pluserable views."""
    return cls(
        repo=request.replusitory,
        kerno=request.registry.getUtility(IKerno),
        registry=request.registry,
        user=user or getattr(request, 'user', None),
        payload=payload,
    )


class PluserableAction(Action):
    """Base class for our actions."""

    @reify
    def _strings(self):
        return get_strings(self.peto.kerno)


def require_activation_setting_value(kerno):
    """Return the value of a certain setting."""
    return kerno.pluserable_settings.bool('require_activation', default=True)


class CheckCredentials(PluserableAction):
    """Business rules decoupled from the web framework and from persistence."""

    @reify
    def _require_activation(self):
        return require_activation_setting_value(self.peto.kerno)

    def q_user(self, handle):
        """Fetch user. ``handle`` can be a username or an email."""
        if '@' in handle:
            return self.peto.repo.q_user_by_email(handle)
        else:
            return self.peto.repo.q_user_by_username(handle)

    def __call__(self):
        """Get user object if credentials are valid, else raise."""
        handle = self.peto.dirty['handle']
        user = self.q_user(handle)  # IO
        self.peto.user = self._check_credentials(
            user, handle, self.peto.dirty['password'])

    def _check_credentials(self, user, handle, password):
        """Pure method (no IO) that checks credentials against ``user``."""
        if not user or not user.check_password(password):
            raise AuthenticationFailure(
                self._strings.wrong_email if '@' in handle
                else self._strings.wrong_username)

        if self._require_activation and not user.is_activated:
            raise AuthenticationFailure(self._strings.inactive_account)
        return user


class ActivateUser(PluserableAction):

    def __call__(self):
        peto = self.peto
        activation = peto.repo.q_activation_by_code(peto.dirty['code'])
        if not activation:
            raise HTTPNotFound()  # TODO Don't import pyramid in actions

        user = peto.repo.q_user_by_id(peto.dirty['user_id'])
        if not user:
            raise HTTPNotFound()

        if user.activation is not activation:
            raise HTTPNotFound()

        peto.repo.delete_activation(user, activation)
        peto.user = user
        peto.activation = activation
