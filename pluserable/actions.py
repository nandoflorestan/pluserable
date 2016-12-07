"""The **action** layer is also called "service" layer.

It stands between the model layer and the view layer.
It is the heart of an application and contains its business rules.

This is because MVC/MVT is insufficient for large apps. Views should
be thin.  Business rules must be decoupled from the web framework.
"""

from bag.settings import SettingsReader
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from mundi.action import Action
from pluserable.exceptions import AuthenticationFailure
from pluserable.interfaces import IMundi
from pluserable.strings import get_strings


def instantiate_action(cls, request, payload: dict, user=None):
    """Convenience function to be used from pluserable views."""
    return cls(
        repo=request.replusitory,
        mundi=request.registry.getUtility(IMundi),
        registry=request.registry,
        user=user or getattr(request, 'user', None),
        payload=payload,
    )


class PluserableAction(Action):
    """Base class for our actions."""

    @reify
    def _strings(self):
        return get_strings(self.mundi)

    @reify
    def _settings_reader(self):
        return SettingsReader(self.registry.settings)  # TODO NOT REGISTRY


class CheckCredentials(PluserableAction):
    """Business rules decoupled from the web framework and from persistence."""

    @reify
    def _allow_inactive_login(self):
        return self._settings_reader.bool(
            'pluserable.allow_inactive_login', False)

    @reify
    def _require_activation(self):
        return self._settings_reader.bool(
            'pluserable.require_activation', True)

    def q_user(self, handle):
        """Fetch user. ``handle`` can be a username or an email."""
        if '@' in handle:
            return self.repo.q_user_by_email(handle)
        else:
            return self.repo.q_user_by_username(handle)

    def do(self):
        """Return user object if credentials are valid, else raise."""
        handle = self.payload['handle']
        user = self.q_user(handle)  # IO
        return self._check_credentials(user, handle, self.payload['password'])

    def _check_credentials(self, user, handle, password):
        """Pure method (no IO) that checks credentials against ``user``."""
        if not user or not user.check_password(password):
            raise AuthenticationFailure(
                self._strings.wrong_email if '@' in handle
                else self._strings.wrong_username)

        if not self._allow_inactive_login and self._require_activation \
                and not user.is_activated:
            raise AuthenticationFailure(self._strings.inactive_account)
        return user


class ActivateUser(PluserableAction):

    def do(self):
        activation = self.repo.q_activation_by_code(self.payload['code'])
        if not activation:
            raise HTTPNotFound()

        user = self.repo.q_user_by_id(self.payload['user_id'])
        if not user:
            raise HTTPNotFound()

        if user.activation is not activation:
            raise HTTPNotFound()

        self.repo.delete_activation(user, activation)
        return user, activation
