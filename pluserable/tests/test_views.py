# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid import testing
from mock import Mock, patch
from . import UnitTestBase


class TestAuthController(UnitTestBase):
    def test_auth_controller_extensions(self):
        from ..views import AuthController
        from ..interfaces import (
            IUserClass, ILoginSchema, ILoginForm, IActivationClass, IUIStrings)
        from ..strings import UIStringsBase
        from .models import User, Activation

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

        AuthController(request)

        assert schema.called
        assert form.called

    def test_login_loads(self):
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = None
        view = AuthController(request)
        response = view.login()

        assert response.get('form', None)

    def test_login_redirects_if_logged_in(self):
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest()
        request.user = Mock()
        view = AuthController(request)

        response = view.login()
        assert response.status_int == 302

    def test_login_fails_empty(self):
        """Make sure we can't log in with empty credentials."""
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest(post={
            'submit': True,
        }, request_method='POST')

        view = AuthController(request)
        response = view.login()
        errors = response['errors']

        assert errors[0].node.name == 'csrf_token'
        assert errors[0].msg == 'Required'
        assert errors[1].node.name == 'handle'
        assert errors[1].msg == 'Required'
        assert errors[2].node.name == 'password'
        assert errors[2].msg == 'Required'

    def test_csrf_invalid_fails(self):
        """ Make sure we can't login with a bad csrf """
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = self.get_csrf_request(post={
                    'submit': True,
                    'login': 'admin',
                    'password': 'test123',
                    'csrf_token': 'abc2'
                }, request_method='POST')

        view = AuthController(request)

        response = view.login()

        errors = response['errors']

        assert errors[0].node.name == 'csrf_token'
        assert errors[0].msg == 'Invalid cross-site scripting token'

    def test_login_fails_bad_credentials(self):
        """ Make sure we can't login with bad credentials"""
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = self.get_csrf_request(post={
                'submit': True,
                'handle': 'admin',
                'password': 'test123',
            }, request_method='POST')

        view = AuthController(request)
        with patch('pluserable.views.FlashMessage') as FlashMessage:
            view.login()
            FlashMessage.assert_called_with(request,
                "Invalid username or password.", kind="error")

    def test_login_succeeds(self):
        """Make sure we can log in."""
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        admin = User(username='sontek', email='sontek@gmail.com')
        admin.password = 'min4'

        self.session.add(admin)
        self.session.flush()

        from pluserable.views import AuthController
        self.config.add_route('index', '/')

        self.config.include('pluserable')

        request = self.get_csrf_request(post={
                'submit': True,
                'handle': 'sontek',
                'password': 'min4',
            }, request_method='POST')

        view = AuthController(request)
        response = view.login()

        assert response.status_int == 302

    def test_inactive_login_fails(self):
        """Make sure we can't log in with an inactive user."""
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()
        self.session.add(user)
        self.session.flush()

        from pluserable.views import AuthController
        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = self.get_csrf_request(post={
            'submit': True,
            'handle': 'sontek',
            'password': 'min4',
            }, request_method='POST')

        view = AuthController(request)
        with patch('pluserable.views.FlashMessage') as FlashMessage:
            view.login()
            FlashMessage.assert_called_with(
                request,
                'Your account is not active, please check your e-mail.',
                kind='error')

    def test_logout(self):
        from ..strings import UIStringsBase as Str
        from ..views import AuthController
        from ..interfaces import IUserClass, IActivationClass
        from .models import User, Activation
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

        view = AuthController(request)
        with patch('pluserable.views.forget') as forget:
            with patch('pluserable.views.HTTPFound') as HTTPFound:
                with patch('pluserable.views.FlashMessage') as FlashMessage:
                    view.logout()
                    FlashMessage.assert_called_with(request,
                        Str.logout, kind="success")

                forget.assert_called_with(request)
                assert invalidate.called
                assert HTTPFound.called


class TestRegisterController(UnitTestBase):
    def test_register_controller_extensions_with_mail(self):
        from pyramid_mailer.mailer      import DummyMailer
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.views                import RegisterController
        from pluserable.interfaces           import IRegisterSchema
        from pluserable.interfaces           import IRegisterForm
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces   import IUIStrings
        from pluserable.strings      import UIStringsBase
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
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
            RegisterController(request)
            assert get_mailer.called

        assert schema.called
        assert form.called

    def test_register_controller_extensions_without_mail(self):
        from pluserable.views        import RegisterController
        from pluserable.interfaces   import IRegisterSchema
        from pluserable.interfaces   import IRegisterForm
        from pluserable.interfaces   import IUserClass
        from pluserable.interfaces   import IUIStrings
        from pluserable.strings      import UIStringsBase
        from pluserable.tests.models import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
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
            RegisterController(request)
            assert not get_mailer.called

        schema.assert_called_once_with()
        assert form.called

    def test_register_loads_not_logged_in(self):
        from pluserable.views                import RegisterController
        from pyramid_mailer.mailer      import DummyMailer
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.include('pluserable')

        self.config.add_route('index', '/')

        request = testing.DummyRequest()
        request.user = None
        controller = RegisterController(request)
        response = controller.register()

        assert response.get('form', None)

    def test_register_redirects_if_logged_in(self):
        from pluserable.views                import RegisterController
        from pyramid_mailer.mailer      import DummyMailer
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')
        self.config.registry.settings['pluserable.login_redirect'] = 'index'
        self.config.registry.settings['pluserable.logout_redirect'] = 'index'

        request = testing.DummyRequest()
        request.user = Mock()
        controller = RegisterController(request)
        response = controller.register()

        assert response.status_int == 302

    def test_register_creates_user(self):
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from pluserable.views import RegisterController
        from pluserable.interfaces import IActivationClass, IUserClass
        from pluserable.tests.models import Activation, User
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)
        self.config.add_route('index', '/')

        request = self.get_csrf_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'sontek@gmail.com'
        }, request_method='POST')
        request.user = Mock()
        controller = RegisterController(request)
        response = controller.register()

        assert response.status_int == 302
        user = User.get_by_username(request, 'admin')
        assert user is not None

    def test_register_validation(self):
        from pluserable.views                import RegisterController
        from pyramid_mailer.mailer      import DummyMailer
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)
        response = controller.register()

        assert len(response['errors']) == 3
        assert 'There was a problem with your submission' in response['form']

    def test_register_existing_user(self):
        from pluserable.views                import RegisterController
        from pyramid_mailer.mailer      import DummyMailer
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        self.config.add_route('index', '/')

        admin = User(username='sontek', email='sontek@gmail.com')
        admin.password = 'test123'
        self.session.add(admin)
        self.session.flush()

        request = self.get_csrf_request(post={
            'username': 'sontek',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'sontek@gmail.com'
        }, request_method='POST')

        view = RegisterController(request)
        adict = view.register()
        assert isinstance(adict, dict)
        assert adict['errors']

    def test_register_no_email_validation(self):
        from pluserable.views import RegisterController
        from pyramid_mailer.mailer import DummyMailer
        from pyramid_mailer.interfaces import IMailer
        from hem.interfaces import IDBSession
        from pluserable.events import NewRegistrationEvent
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
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

        request = self.get_csrf_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = Mock()

        view = RegisterController(request)
        with patch('pluserable.views.FlashMessage') as FlashMessage:
            response = view.register()
            FlashMessage.assert_called_with(request,
                view.Str.registration_done, kind="success")
        assert response.status_int == 302
        user = User.get_by_username(request, 'admin')
        assert user.is_activated == True

    def test_registration_craps_out(self):
        from pluserable.views                import RegisterController
        from pyramid_mailer.interfaces  import IMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        def send(message):
            raise Exception("I broke!")

        mailer = Mock()
        mailer.send = send

        self.config.include('pluserable')
        self.config.registry.registerUtility(mailer, IMailer)

        self.config.add_route('index', '/')

        request = self.get_csrf_request(post={
            'username': 'admin',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
            'email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = Mock()
        controller = RegisterController(request)

        self.assertRaises(Exception, controller.register)

    def test_activate(self):
        from pluserable.views import RegisterController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces import IUserClass
        from pluserable.tests.models import User
        from pluserable.interfaces   import IActivationClass
        from pluserable.tests.models import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', email='sontek2@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user.activation.code
            else:
                return user.id

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        user = User.get_by_username(request, 'sontek')

        assert user.is_activated
        assert response.status_int == 302

    def test_activate_multiple_users(self):
        from pluserable.views import RegisterController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', email='sontek@gmail.com')
        user.activation = Activation()
        user.password = 'min4'
        user1 = User(username='sontek1', email='sontek+2@gmail.com')
        user1.activation = Activation()
        user1.password = 'more'

        self.session.add(user)
        self.session.add(user1)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(key, default):
            if key == 'code':
                return user1.activation.code
            else:
                return user1.id

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        user = User.get_by_username(request, 'sontek1')

        activations = Activation.get_all(request)

        assert len(activations.all()) == 1
        assert user.is_activated
        assert response.status_int == 302

    def test_activate_invalid(self):
        from pluserable.views import RegisterController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'invalid'
        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        user = User.get_by_username(request, 'sontek')

        assert not user.is_activated
        assert response.status_int == 404

    def test_activate_invalid_user(self):
        from pluserable.views import RegisterController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.include('pluserable')
        self.config.add_route('index', '/')

        self.config.registry.registerUtility(DummyMailer(), IMailer)

        bad_act = Activation()

        user = User(username='sontek', email='sontek@gmail.com')
        user.activation = Activation()
        user.password = 'min4'

        user2 = User(username='jessie', email='sontek+2@gmail.com')
        user2.activation = bad_act
        user2.password = 'more'

        self.session.add(user)
        self.session.add(user2)
        self.session.flush()

        request = testing.DummyRequest()
        request.matchdict = Mock()

        def get(val, ret):
            if val == 'code':
                return bad_act.code
            elif val == 'user_id':
                return user.id

        request.matchdict.get = get

        controller = RegisterController(request)
        response = controller.activate()
        new_user1 = User.get_by_username(request, 'sontek')
        new_user2 = User.get_by_username(request, 'jessie')

        assert not new_user1.is_activated
        assert not new_user2.is_activated
        assert response.status_int == 404


class TestForgotPasswordController(UnitTestBase):
    def test_forgot_password_loads(self):
        from pluserable.views import ForgotPasswordController
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = None
        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert response.get('form', None)

    def test_forgot_password_logged_in_redirects(self):
        from pluserable.views import ForgotPasswordController
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User

        self.config.registry.registerUtility(User, IUserClass)
        self.config.add_route('index', '/')
        self.config.include('pluserable')

        request = testing.DummyRequest()
        request.user = Mock()
        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert response.status_int == 302

    def test_forgot_password_valid_user(self):
        from pluserable.views                import ForgotPasswordController
        from pyramid_mailer.interfaces  import IMailer
        from pyramid_mailer.mailer      import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
            'email': 'sontek@gmail.com'
        }, request_method='POST')

        request.user = None

        view = ForgotPasswordController(request)

        with patch('pluserable.views.FlashMessage') as FlashMessage:
            response = view.forgot_password()
            FlashMessage.assert_called_with(request,
                view.Str.reset_password_email_sent, kind="success")
        assert response.status_int == 302

    def test_forgot_password_invalid_password(self):
        from pluserable.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User

        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
            'email': 'sontek'
        }, request_method='POST')

        request.user = None

        view = ForgotPasswordController(request)
        response = view.forgot_password()

        assert len(response['errors']) == 1

    def test_reset_password_loads(self):
        from pluserable.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation
        from pluserable.interfaces           import IActivationClass

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert response.get('form', None)
        assert 'sontek' in response['form']

    def test_reset_password_valid_user(self):
        from pluserable.views import ForgotPasswordController
        from hem.interfaces import IDBSession
        from pluserable.events import PasswordResetEvent
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.models import crypt
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
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

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert not crypt.check(user.password, 'temp' + user.salt)
        assert response.status_int == 302

    def test_reset_password_invalid_password(self):
        from pluserable.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(post={
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

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_reset_password_empty_password(self):
        from pluserable.views import ForgotPasswordController
        from pyramid_mailer.interfaces import IMailer
        from pyramid_mailer.mailer import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(request_method='POST')

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.activation.code
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordController(request)

        response = view.reset_password()

        assert len(response['errors']) == 1

    def test_invalid_reset_gets_404(self):
        from pluserable.views                import ForgotPasswordController
        from pyramid_mailer.interfaces  import IMailer
        from pyramid_mailer.mailer      import DummyMailer
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')
        self.config.registry.registerUtility(DummyMailer(), IMailer)

        user = User(username='sontek', password='temp',
            email='sontek@gmail.com')
        user.password = 'min4'
        user.activation = Activation()

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 'b'
        request.matchdict.get = get

        request.user = None

        view = ForgotPasswordController(request)
        response = view.reset_password()

        assert response.status_int == 404


class TestProfileController(UnitTestBase):
    def test_profile_loads(self):
        from pluserable.views import ProfileController
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'
        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        view = ProfileController(request)

        response = view.profile()

        assert response.get('user', None) == user

    def test_profile_bad_id(self):
        from pluserable.views import ProfileController
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation

        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'

        self.session.add(user)
        self.session.flush()

        request = testing.DummyRequest()
        request.user = Mock()

        request.matchdict = Mock()
        get = Mock()
        get.return_value = 99
        request.matchdict.get = get

        view = ProfileController(request)

        response = view.profile()

        assert response.status_int == 404

    def test_profile_update_profile_invalid(self):
        from pluserable.views import ProfileController
        from pluserable.interfaces           import IUserClass
        from pluserable.interfaces           import IActivationClass
        from pluserable.interfaces           import IProfileSchema
        from pluserable.tests.models         import User
        from pluserable.tests.models         import Activation
        from pluserable.tests.schemas        import ProfileSchema

        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)
        self.config.registry.registerUtility(ProfileSchema,
            IProfileSchema)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'
        self.session.add(user)
        self.session.flush()

        request = self.get_csrf_request(request_method='POST')
        request.context = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        view = ProfileController(request)

        response = view.edit_profile()

        assert len(response['errors']) == 3

    def test_profile_update_profile(self):
        from pluserable.views import ProfileController
        from hem.interfaces import IDBSession
        from pluserable.events import ProfileUpdatedEvent
        from pluserable.models import crypt
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'
        self.session.add(user)
        self.session.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)

        request = self.get_csrf_request(post={
            'email': 'sontek@gmail.com',
        }, request_method='POST')

        request.user = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        view = ProfileController(request)
        view.profile()

        new_user = User.get_by_id(request, user.id)

        assert new_user.email == 'sontek@gmail.com'
        assert crypt.check(user.password, 'temp' + user.salt)

    def test_profile_update_password(self):
        from pluserable.views import ProfileController
        from hem.interfaces import IDBSession
        from pluserable.events import ProfileUpdatedEvent
        from pluserable.models import crypt
        from pluserable.interfaces           import IUserClass
        from pluserable.tests.models         import User
        from pluserable.interfaces           import IActivationClass
        from pluserable.tests.models         import Activation
        self.config.registry.registerUtility(Activation, IActivationClass)

        self.config.registry.registerUtility(User, IUserClass)

        self.config.add_route('index', '/')
        self.config.include('pluserable')

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'temp'

        self.session.add(user)
        self.session.flush()

        def handle_profile_updated(event):
            request = event.request
            session = request.registry.getUtility(IDBSession)
            session.commit()

        self.config.add_subscriber(handle_profile_updated, ProfileUpdatedEvent)

        request = self.get_csrf_request(post={
            'email': 'sontek@gmail.com',
            'password': {
                'password': 'test123',
                'password-confirm': 'test123',
            },
        }, request_method='POST')

        request.context = user

        request.matchdict = Mock()
        get = Mock()
        get.return_value = user.id
        request.matchdict.get = get

        view = ProfileController(request)

        view.edit_profile()
        new_user = User.get_by_id(request, user.id)

        assert new_user.email == 'sontek@gmail.com'
        assert not crypt.check(user.password, 'temp' + user.salt)
