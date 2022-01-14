"""Tests for the views."""

from datetime import datetime
from unittest.mock import Mock, patch

from kerno.state import MalbonaRezulto
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.mailer import DummyMailer
from pyramid.httpexceptions import HTTPNotFound

from pluserable.events import (
    EventRegistration,
    EventPasswordReset,
    EventProfileUpdated,
)
from pluserable.interfaces import ILoginForm, ILoginSchema
from pluserable.strings import UIStringsBase
from pluserable.web.pyramid.views import (
    AuthView,
    ForgotPasswordView,
    ProfileView,
    RegisterView,
)

from tests.models import User
from tests.integration import IntegrationTestBase, LoggedIntegrationTest


class TestAuthView(IntegrationTestBase):  # noqa
    def test_auth_view_extensions(self):  # noqa
        request = self.get_request()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()
        self.config.registry.registerUtility(schema, ILoginSchema)
        self.config.registry.registerUtility(form, ILoginForm)
        AuthView(request)

        assert schema.called
        assert form.called

    def test_login_loads(self):  # noqa
        self.config.add_route("index", "/")

        request = self.get_request()
        view = AuthView(request)
        response = view.login()

        assert response.get("form", None)

    def test_login_fails_empty(self):
        """Make sure we can't log in with empty credentials."""
        self.config.add_route("index", "/")

        request = self.get_request(
            post={
                "submit": True,
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()

        view = AuthView(request)
        response = view.login()
        errors = response["errors"]

        assert errors[0].node.name == "handle"
        assert errors[0].msg == "Required"
        assert errors[1].node.name == "password"
        assert errors[1].msg == "Required"

    def test_login_fails_bad_credentials(self):
        """Make sure we can't log in with bad credentials."""
        self.config.add_route("index", "/")

        request = self.get_request(
            post={
                "submit": True,
                "handle": "admin",
                "password": "test123",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()

        view = AuthView(request)
        view.login()
        request.add_flash.assert_called_with(
            plain="Wrong username or password.", level="danger"
        )

    def test_login_succeeds(self):
        """Make sure we can log in."""
        self.config.add_route("index", "/")
        user = self.create_users(count=1, password="science")
        self.sas.flush()

        request = self.get_request(
            post={
                "submit": True,
                "handle": user.username,
                "password": "science",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()

        view = AuthView(request)
        response = view.login()

        assert response.status_int == 302
        assert user.last_login_date > datetime(2018, 1, 1)

    def test_inactive_login_fails(self):
        """Ensure we can't log in with an inactive user."""
        self.config.add_route("index", "/")

        user = self.create_users(count=1, password="science", activation=True)
        self.sas.flush()

        request = self.get_request(
            post={
                "submit": True,
                "handle": user.username,
                "password": "science",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()

        view = AuthView(request)
        view.login()
        request.add_flash.assert_called_with(
            plain="Your account is not active; please check your e-mail.",
            level="danger",
        )


class TestRegisterView(IntegrationTestBase):  # noqa
    def test_register_loads_not_logged_in(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        request = self.get_request()
        view = RegisterView(request)
        response = view.register()

        assert response.get("form", None)

    def test_register_creates_inactive_user(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        request = self.get_request(
            post={
                "username": "admin",
                "password": {
                    "password": "test123",
                    "password-confirm": "test123",
                },
                "email": "carlsagan@nasa.gov",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()
        view = RegisterView(request)
        response = view.register()

        assert response.status_int == 302
        user = request.repo.get_user_by_username("admin")
        assert isinstance(user, User)
        assert not user.is_activated

    def test_register_validation(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        request = self.get_request(request_method="POST")
        view = RegisterView(request)
        response = view.register()

        assert len(response["errors"]) == 3
        assert "There was a problem with your submission" in response["form"]

    def test_register_existing_user(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")
        user = self.create_users(count=1)
        self.sas.flush()

        request = self.get_request(
            post={
                "username": user.username,
                "password": {
                    "password": "science",
                    "password-confirm": "science",
                },
                "email": "carlsagan@nasa.gov",
            },
            request_method="POST",
        )

        view = RegisterView(request)
        adict = view.register()
        assert isinstance(adict, dict)
        assert adict["errors"]

    def test_register_no_activation_suceeds(self):
        """Test register() with setting to not require activation."""
        self.config.add_route("index", "/")

        request = self.get_request(
            post={
                "username": "admin",
                "password": {
                    "password": "test123",
                    "password-confirm": "test123",
                },
                "email": "carlsagan@nasa.gov",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.kerno.pluserable_settings["require_activation"] = False

        request.add_flash = Mock()

        view = RegisterView(request)
        response = view.register()
        request.add_flash.assert_called_with(
            plain=UIStringsBase.registration_done, level="success"
        )
        assert response.status_int == 302
        user = request.repo.get_user_by_username("admin")
        assert user.is_activated is True

    def test_registration_fails_with_mailer(self):  # noqa
        self.config.add_route("index", "/")

        def send(message):
            raise Exception("I broke!")

        mailer = Mock()
        mailer.send = send
        self.config.registry.registerUtility(mailer, IMailer)

        request = self.get_request(
            post={
                "username": "admin",
                "password": {
                    "password": "test123",
                    "password-confirm": "test123",
                },
                "email": "carlsagan@nasa.gov",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        view = RegisterView(request)

        self.assertRaises(Exception, view.register)

    def test_activate(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request()
        request.add_flash = Mock()
        request.matchdict = Mock()

        def get(key, default):
            if key == "code":
                return user.activation.code
            else:
                return user.id

        request.matchdict.get = get

        view = RegisterView(request)
        response = view.activate()
        the_user = request.repo.get_user_by_username(user.username)

        assert the_user is user
        assert the_user.activation is None
        assert the_user.is_activated
        assert response.status_int == 302

    def test_activation_works(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        user1, user2 = self.create_users(count=2, activation=True)
        self.sas.flush()

        def get(key, default):
            if key == "code":
                return user1.activation.code
            else:
                return user1.id

        request = self.get_request()
        request.add_flash = Mock()
        request.matchdict = Mock()
        request.matchdict.get = get
        view = RegisterView(request)
        response = view.activate()

        activations = list(request.repo.q_activations())

        assert len(activations) == 1
        assert user1.is_activated
        assert response.status_int == 302

    def test_activate_invalid_code_raises(self):  # noqa
        self.config.add_route("index", "/")

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request()
        request.add_flash = Mock()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = "invalid"
        request.matchdict.get = get

        view = RegisterView(request)
        with self.assertRaises(MalbonaRezulto):
            view.activate()

        the_user = request.repo.get_user_by_username(user.username)
        assert the_user is user
        assert not the_user.is_activated

    def test_activate_invalid_user_raises(self):
        """One user tries to get activated with another's code."""
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        user1, user2 = self.create_users(count=2, activation=True)
        self.sas.flush()

        request = self.get_request()
        request.matchdict = Mock()

        def get(val, ret):
            if val == "code":
                return user2.activation.code
            elif val == "user_id":
                return user1.id

        request.matchdict.get = get

        view = RegisterView(request)
        with self.assertRaises(MalbonaRezulto):
            view.activate()

        for user in (user1, user2):
            assert not user.is_activated


class TestForgotPasswordView(IntegrationTestBase):  # noqa
    def test_forgot_password_invalid_password(self):  # noqa
        self.config.add_route("index", "/")
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.create_users(count=1)
        self.sas.flush()
        request = self.get_request(
            post={
                "email": "sagan",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        view = ForgotPasswordView(request)

        response = view.forgot_password()
        assert len(response["errors"]) == 1

    def test_forgot_password_loads(self):  # noqa
        self.config.add_route("index", "/")
        request = self.get_request()
        view = ForgotPasswordView(request)

        response = view.forgot_password()
        assert response.get("form", None)

    def test_forgot_password_valid_user_succeeds(self):  # noqa
        self.config.add_route("index", "/")
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.create_users(count=1)
        self.sas.flush()
        request = self.get_request(
            post={
                "email": "carlsagan1@nasa.gov",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()
        view = ForgotPasswordView(request)

        response = view.forgot_password()
        request.add_flash.assert_called_with(
            plain=UIStringsBase.reset_password_email_sent, level="success"
        )
        assert response.status_int == 302

    def test_invalid_reset_gets_404(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = "wrong value"
        request.matchdict.get = get
        view = ForgotPasswordView(request)

        with self.assertRaises(HTTPNotFound):
            view.reset_password()

    def test_reset_password_empty_password(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request(request_method="POST")
        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get
        view = ForgotPasswordView(request)

        response = view.reset_password()
        assert len(response["errors"]) == 1

    def test_reset_password_invalid_password(self):  # noqa
        self.config.add_route("index", "/")
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request(
            post={
                "Password": {
                    "Password": "t",
                    "Password-confirm": "t",
                },
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get
        view = ForgotPasswordView(request)

        response = view.reset_password()
        assert len(response["errors"]) == 1

    def test_reset_password_loads(self):  # noqa
        self.config.add_route("index", "/")
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get
        view = ForgotPasswordView(request)

        response = view.reset_password()
        assert response.get("form", None)
        assert "sagan" in response["form"]

    def test_reset_password_valid_user(self):  # noqa
        self.config.add_route("index", "/")
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = self.create_users(count=1, activation=True)
        self.sas.flush()

        request = self.get_request(
            post={
                "password": {
                    "password": "test123",
                    "password-confirm": "test123",
                },
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get
        view = ForgotPasswordView(request)

        response = view.reset_password()
        assert user.check_password("test123")
        assert response.status_int == 302


class TestLoggedIn(LoggedIntegrationTest):  # noqa
    def test_forgot_password_logged_in_redirects(self):  # noqa
        self.config.add_route("index", "/")
        request = self.get_request()
        view = ForgotPasswordView(request)

        response = view.forgot_password()
        assert response.status_int == 302

    def test_login_redirects_if_logged_in(self):  # noqa
        self.config.add_route("index", "/")
        request = self.get_request()
        view = AuthView(request)

        response = view.login()
        assert response.status_int == 302
        assert response.headers["Location"] == "/"

    def test_logout(self):
        """User logs out successfully."""
        self.config.add_route("index", "/")
        request = self.get_request()

        invalidate = Mock()
        request.add_flash = Mock()
        request.session = Mock()
        request.session.invalidate = invalidate

        view = AuthView(request)
        with patch("pluserable.web.pyramid.views.forget") as forget:
            with patch("pluserable.web.pyramid.views.HTTPFound") as HTTPFound:
                view.logout()
                request.add_flash.assert_called_with(
                    plain=UIStringsBase.logout_done, level="success"
                )

                forget.assert_called_with(request)
                assert invalidate.called
                assert HTTPFound.called

    def test_profile_view_bad_id(self):  # noqa
        self.config.add_route("index", "/")

        request = self.get_request()
        request.matchdict = Mock()

        get = Mock()
        get.return_value = 99  # This user ID does not exist
        request.matchdict.get = get

        view = ProfileView(request)
        with self.assertRaises(HTTPNotFound):
            view.profile()

    def test_profile_view_loads(self):  # noqa
        self.config.add_route("index", "/")
        request = self.get_request()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = request.identity.id
        request.matchdict.get = get

        view = ProfileView(request)

        response = view.profile()

        assert response.get("user", None) == request.identity

    def test_profile_update_email(self):  # noqa
        self.config.add_route("index", "/")

        def handle_profile_updated(event):
            event.request.repo.flush()

        self.kerno.events.subscribe(
            EventProfileUpdated, handle_profile_updated
        )

        request = self.get_request(
            post={
                "email": "new_email@nasa.gov",
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        assert request.identity
        request.add_flash = Mock()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = request.identity.id
        request.matchdict.get = get

        # The code being tested
        ProfileView(request).edit_profile()

        # Assertions
        the_user = request.repo.get_user_by_id(request.identity.id)
        assert the_user is request.identity
        assert the_user.email == "new_email@nasa.gov"
        assert the_user.password == "Please bypass hashing!"

    def test_profile_update_password(self):  # noqa  # Happy
        self.config.add_route("index", "/")
        request = self.get_request(
            post={
                "email": self.user.email,
                "password": {
                    "password": "new password",
                    "password-confirm": "new password",
                },
                "csrf_token": "irrelevant but required",
            },
            request_method="POST",
        )
        request.add_flash = Mock()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = self.user.id
        request.matchdict.get = get

        handle_profile_updated = Mock()
        self.kerno.events.subscribe(
            EventProfileUpdated, handle_profile_updated
        )

        # The code being tested
        ProfileView(request).edit_profile()

        # Assertions
        assert self.user in request.repo.sas.dirty
        assert self.user.email == "carlsagan1@nasa.gov"
        assert self.user.check_password("new password")
        assert handle_profile_updated.called

    def test_register_redirects_if_logged_in(self):  # noqa
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route("index", "/")
        request = self.get_request()
        view = RegisterView(request)

        response = view.register()
        assert response.status_int == 302

    def test_update_profile_invalid(self):  # noqa
        from pluserable.interfaces import IProfileSchema
        from tests.schemas import ProfileSchema

        self.config.registry.registerUtility(ProfileSchema, IProfileSchema)
        self.config.add_route("index", "/")
        request = self.get_request(request_method="POST")

        request.matchdict = Mock()
        get = Mock()
        get.return_value = request.identity.id
        request.matchdict.get = get

        # The code being tested
        response = ProfileView(request).edit_profile()

        assert len(response["errors"]) == 3
