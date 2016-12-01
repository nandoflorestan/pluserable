"""Tests for the views."""

from mock import Mock, patch
from pyramid import testing
from pyramid_mailer.interfaces import IMailer
from pyramid_mailer.mailer import DummyMailer
from pluserable.interfaces import IDBSession
from pluserable.views import AuthView, RegisterView
from pluserable.interfaces import (
    IActivationClass, ILoginForm, ILoginSchema, IUIStrings, IUserClass)
from pluserable.strings import UIStringsBase
from pluserable.tests.models import User, Activation
from . import IntegrationTestBase


class TestAuthView(IntegrationTestBase):

    def test_auth_view_extensions(self):
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(UIStringsBase, IUIStrings)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(schema, ILoginSchema)
        self.config.registry.registerUtility(form, ILoginForm)

        AuthView(request)

        assert schema.called
        assert form.called

    def test_login_loads(self):
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = None
        view = AuthView(request)
        response = view.login()

        assert response.get('form', None)

    def test_login_redirects_if_logged_in(self):
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest()
        request.user = Mock()
        view = AuthView(request)

        response = view.login()
        assert response.status_int == 302

    def test_login_fails_empty(self):
        """Make sure we can't log in with empty credentials."""
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest(post={
            'submit': True,
        }, request_method='POST')

        view = AuthView(request)
        response = view.login()
        errors = response['errors']

        assert errors[0].node.name == 'handle'
        assert errors[0].msg == 'Required'
        assert errors[1].node.name == 'password'
        assert errors[1].msg == 'Required'

    def test_login_fails_bad_credentials(self):
        """Make sure we can't log in with bad credentials."""
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = self.get_request(post={
            'submit': True,
            'handle': 'admin',
            'password': 'test123',
        }, request_method='POST')

        view = AuthView(request)
        with patch('pluserable.views.add_flash') as add_flash:
            view.login()
            add_flash.assert_called_with(
                request, plain="Wrong username or password.", kind="error")

    def test_login_succeeds(self):
        """Make sure we can log in."""
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        admin = User(username='sagan', email='carlsagan@nasa.org')
        admin.password = 'min4'

        self.sas.add(admin)
        self.sas.flush()

        from pluserable.views import AuthView
        self.config.add_route('index', '/')

        self.config.include('pluserable')

        request = self.get_request(post={
                'submit': True,
                'handle': 'sagan',
                'password': 'min4',
            }, request_method='POST')

        view = AuthView(request)
        response = view.login()

        assert response.status_int == 302

    def test_inactive_login_fails(self):
        """Make sure we can't log in with an inactive user."""
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()
        self.sas.add(user)
        self.sas.flush()

        from pluserable.views import AuthView
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = self.get_request(post={
            'submit': True,
            'handle': 'sagan',
            'password': 'min4',
            }, request_method='POST')

        view = AuthView(request)
        with patch('pluserable.views.add_flash') as add_flash:
            view.login()
            add_flash.assert_called_with(
                request,
                plain='Your account is not active; please check your e-mail.',
                kind='error')

    def test_logout(self):
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'
        request = testing.DummyRequest()

        invalidate = Mock()
        request.user = Mock()
        request.session = Mock()
        request.session.invalidate = invalidate

        view = AuthView(request)
        with patch('pluserable.views.forget') as forget:
            with patch('pluserable.views.HTTPFound') as HTTPFound:
                with patch('pluserable.views.add_flash') as add_flash:
                    view.logout()
                    add_flash.assert_called_with(
                        request, plain=UIStringsBase.logout, kind="success")

                forget.assert_called_with(request)
                assert invalidate.called
                assert HTTPFound.called


class TestRegisterView(IntegrationTestBase):

    def test_register_view_extensions_with_mail(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.views import RegisterView
        from pluserable.interfaces import (
            IRegisterSchema, IRegisterForm, IUserClass, IUIStrings,
            IActivationClass)
        from pluserable.strings import UIStringsBase
        from pluserable.tests.models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(UIStringsBase, IUIStrings)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.registerUtility(schema, IRegisterSchema)
        self.config.registry.registerUtility(form, IRegisterForm)
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        with patch('pluserable.views.get_mailer') as get_mailer:
            RegisterView(request)
            assert get_mailer.called

        assert schema.called
        assert form.called

    def test_register_view_extensions_without_mail(self):
        from pluserable.views import RegisterView
        from pluserable.interfaces import (
            IRegisterSchema, IRegisterForm, IUserClass, IUIStrings,
            IActivationClass)
        from pluserable.strings import UIStringsBase
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(UIStringsBase, IUIStrings)

        self.config.add_route('index', '/')

        request = testing.DummyRequest()

        getUtility = Mock()
        getUtility.return_value = True

        schema = Mock()
        form = Mock()

        self.config.registry.settings['pluserable.require_activation'] = False
        self.config.registry.registerUtility(schema, IRegisterSchema)
        self.config.registry.registerUtility(form, IRegisterForm)

        with patch('pluserable.views.get_mailer') as get_mailer:
            RegisterView(request)
            assert not get_mailer.called

        schema.assert_called_once_with()
        assert form.called

    def test_register_loads_not_logged_in(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.include('pluserable')

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = None
        view = RegisterView(request)
        response = view.register()

        assert response.get('form', None)

    def test_register_redirects_if_logged_in(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest()
        request.user = Mock()
        view = RegisterView(request)
        response = view.register()

        assert response.status_int == 302

    def test_register_creates_user(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.views import RegisterView
        from pluserable.interfaces import IActivationClass, IUserClass
        from pluserable.tests.models import Activation, User

        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route('index', '/')

        request = self.get_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'carlsagan@nasa.org'
        }, request_method='POST')
        request.user = Mock()
        view = RegisterView(request)
        response = view.register()

        assert response.status_int == 302
        user = User.get_by_username(request, 'admin')
        assert user is not None

    def test_register_validation(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = self.get_request(request_method='POST')

        request.user = Mock()
        view = RegisterView(request)
        response = view.register()

        assert len(response['errors']) == 3
        assert 'There was a problem with your submission' in response['form']

    def test_register_existing_user(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        admin = User(username='sagan', email='carlsagan@nasa.org')
        admin.password = 'test123'
        self.sas.add(admin)
        self.sas.flush()

        request = self.get_request(post={
            'username': 'sagan',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'carlsagan@nasa.org'
        }, request_method='POST')

        view = RegisterView(request)
        adict = view.register()
        assert isinstance(adict, dict)
        assert adict['errors']

    def test_register_no_email_validation(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.events import NewRegistrationEvent
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.require_activation'] = False

        def handle_registration(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_registration, NewRegistrationEvent)

        request = self.get_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'carlsagan@nasa.org'
        }, request_method='POST')

        request.user = Mock()

        view = RegisterView(request)
        with patch('pluserable.views.add_flash') as add_flash:
            response = view.register()
            add_flash.assert_called_with(
                request, plain=view.Str.registration_done, kind="success")
        assert response.status_int == 302
        user = User.get_by_username(request, 'admin')
        assert user.is_activated is True

    def test_registration_craps_out(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.interfaces import IMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        def send(message):
            raise Exception("I broke!")

        mailer = Mock()
        mailer.send = send

        self.config.include('pluserable')
        self.config.registry.registerUtility(mailer, IMailer)

        self.config.add_route('index', '/')

        request = self.get_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'carlsagan@nasa.org'
        }, request_method='POST')

        request.user = Mock()
        view = RegisterView(request)

        self.assertRaises(Exception, view.register)

    def test_activate(self):
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', email='carlsagan2@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user.activation.code
            else:
                return user.id

        request.matchdict.get = get

        view = RegisterView(request)
        response = view.activate()
        the_user = request.replusitory.q_user_by_username('sagan')

        assert the_user.is_activated
        assert response.status_int == 302

    def test_activate_multiple_users(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.activation = Activation()
        user.password = 'min4'
        user1 = User(username='sagan', email='carlsagan2@nasa.org')
        user1.activation = Activation()
        user1.password = 'more'

        self.sas.add(user)
        self.sas.add(user1)
        self.sas.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user1.activation.code
            else:
                return user1.id

        request.matchdict.get = get

        view = RegisterView(request)
        response = view.activate()
        user = User.get_by_username(request, 'sagan')

        activations = Activation.get_all(request)

        assert len(activations.all()) == 1
        assert user.is_activated
        assert response.status_int == 302

    def test_activate_invalid(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'invalid'
        request.matchdict.get = get

        view = RegisterView(request)
        response = view.activate()
        user = User.get_by_username(request, 'sagan')

        assert not user.is_activated
        assert response.status_int == 404

    def test_activate_invalid_user(self):
        from pluserable.views import RegisterView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        bad_act = Activation()

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.activation = Activation()
        user.password = 'min4'

        user2 = User(username='jessie', email='carlsagan2@nasa.org')
        user2.activation = bad_act
        user2.password = 'more'

        self.sas.add(user)
        self.sas.add(user2)
        self.sas.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(val, ret):
            if val == 'code':
                return bad_act.code
            elif val == 'user_id':
                return user.id

        request.matchdict.get = get

        view = RegisterView(request)
        response = view.activate()
        new_user1 = User.get_by_username(request, 'sagan')
        new_user2 = User.get_by_username(request, 'jessie')

        assert not new_user1.is_activated
        assert not new_user2.is_activated
        assert response.status_int == 404


class TestForgotPasswordView(IntegrationTestBase):

    def test_forgot_password_loads(self):
        from pluserable.views import ForgotPasswordView
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = None
        view = ForgotPasswordView(request)
        response = view.forgot_password()

        assert response.get('form', None)

    def test_forgot_password_logged_in_redirects(self):
        from pluserable.views import ForgotPasswordView
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = Mock()
        view = ForgotPasswordView(request)
        response = view.forgot_password()

        assert response.status_int == 302

    def test_forgot_password_valid_user(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(post={
            'email': 'carlsagan@nasa.org'
        }, request_method='POST')

        request.user = None

        view = ForgotPasswordView(request)

        with patch('pluserable.views.add_flash') as add_flash:
            response = view.forgot_password()
            add_flash.assert_called_with(
                request, plain=view.Str.reset_password_email_sent,
                kind="success")
        assert response.status_int == 302

    def test_forgot_password_invalid_password(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User

        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(post={
            'email': 'sagan'
        }, request_method='POST')

        request.user = None

        view = ForgotPasswordView(request)
        response = view.forgot_password()

        assert len(response['errors']) == 1

    def test_reset_password_loads(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation
        from pluserable.interfaces import IActivationClass

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordView(request)
        response = view.reset_password()

        assert response.get('form', None)
        assert 'sagan' in response['form']

    def test_reset_password_valid_user(self):
        from pluserable.views import ForgotPasswordView
        from pluserable.events import PasswordResetEvent
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.models import crypt
        from pluserable.interfaces import IUserClass
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(post={
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
        }, request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        def handle_password_reset(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_password_reset, PasswordResetEvent)

        view = ForgotPasswordView(request)
        response = view.reset_password()

        assert not crypt.check(user.password, 'temp' + user.salt)
        assert response.status_int == 302

    def test_reset_password_invalid_password(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(post={
            'Password': {
                'Password': 't',
                'Password-confirm': 't',
            },
        }, request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordView(request)
        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_reset_password_empty_password(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.interfaces import IActivationClass
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordView(request)

        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_invalid_reset_gets_404(self):
        from pluserable.views import ForgotPasswordView
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sagan', password='temp',
                    email='carlsagan@nasa.org')
        user.password = 'min4'
        user.activation = Activation()

        self.sas.add(user)
        self.sas.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'b'
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordView(request)
        response = view.reset_password()

        assert response.status_int == 404


class TestProfileView(IntegrationTestBase):

    def test_profile_loads(self):
        from pluserable.views import ProfileView
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.sas.add(user)
        self.sas.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        view = ProfileView(request)

        response = view.profile()

        assert response.get('user', None) == user

    def test_profile_bad_id(self):
        from pluserable.views import ProfileView
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'

        self.sas.add(user)
        self.sas.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 99
        request.matchdict.get = get

        view = ProfileView(request)

        response = view.profile()

        assert response.status_int == 404

    def test_profile_update_profile_invalid(self):
        from pluserable.views import ProfileView
        from pluserable.interfaces import (
            IUserClass, IActivationClass, IProfileSchema)
        from pluserable.tests.models import User, Activation
        from pluserable.tests.schemas import ProfileSchema

        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(ProfileSchema, IProfileSchema)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.sas.add(user)
        self.sas.flush()

        request = self.get_request(request_method='POST')
        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        # The code being tested
        response = ProfileView(request).edit_profile()

        assert len(response['errors']) == 3

    def test_profile_update_profile(self):
        from pluserable.views import ProfileView
        from pluserable.events import ProfileUpdatedEvent
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.models import crypt
        from pluserable.tests.models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'
        self.sas.add(user)
        self.sas.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)

        request = self.get_request(post={
            'email': 'carlsagan@nasa.org',
        }, request_method='POST')

        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        # The code being tested
        ProfileView(request).profile()

        # Assertions
        new_user = User.get_by_id(request, user.id)
        assert new_user.email == 'carlsagan@nasa.org'
        assert crypt.check(user.password, 'temp' + user.salt)

    def test_profile_update_password(self):  # Happy
        from pluserable.views import ProfileView
        from pluserable.events import ProfileUpdatedEvent
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.models import crypt
        from pluserable.tests.models import User, Activation

        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'temp'

        self.sas.add(user)
        self.sas.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)

        request = self.get_request(post={
            'email': 'carlsagan@nasa.org',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
        }, request_method='POST')
        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        # The code being tested
        ProfileView(request).edit_profile()

        # Assertions
        new_user = User.get_by_id(request, user.id)
        assert new_user.email == 'carlsagan@nasa.org'
        assert not crypt.check(user.password, 'temp' + user.salt)
