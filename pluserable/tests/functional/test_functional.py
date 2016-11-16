from mock import Mock, patch
from pyramid import testing
from pyramid.compat import PY3
from pluserable.tests.functional import FunctionalTestBase


class TestViews(FunctionalTestBase):

    def test_index(self):
        """Call the index view, make sure routes are working."""
        res = self.app.get('/')
        assert res.status_int == 200

    def test_get_register(self):
        """Call the register view, make sure routes are working."""
        res = self.app.get('/register')
        assert res.status_int == 200

    def test_get_login(self):
        """Call the login view, make sure routes are working."""
        res = self.app.get('/login')
        self.assertEqual(res.status_int, 200)

    def test_login_redirects_if_logged_in(self):
        request = testing.DummyRequest()
        from pluserable.views import AuthView
        with patch.object(AuthView, 'request', request) as request:
            request.user = Mock()
            res = self.app.get('/login').follow()
            # TODO: Patch index request as well so that it redirects to the
            # dashboard
            assert b'index' in res.body

    def test_empty_login(self):
        """Empty login fails."""
        res = self.app.post(str('/login'), {'submit': True})

        assert b"There was a problem with your submission" in res.body
        assert b"Required" in res.body
        assert res.status_int == 200

    def test_valid_login(self):
        """Call the login view, make sure routes are working."""
        from pluserable.tests.models import User
        admin = User(username='sontek', email='sontek@gmail.com')
        admin.password = 'temp'
        self.session.add(admin)
        self.session.flush()

        res = self.app.get('/login')

        res = self.app.post(
            str('/login'),
            {
                'submit': True,
                'handle': 'sontek',
                'password': 'temp',
            }
        )
        assert res.status_int == 302

    def test_inactive_login(self):
        """Make sure inactive users can't sign in."""
        from pluserable.tests.models import User
        from pluserable.tests.models import Activation
        admin = User(username='sontek', email='sontek@gmail.com')
        admin.activation = Activation()
        admin.password = 'temp'
        self.session.add(admin)
        self.session.flush()

        res = self.app.get('/login')

        res = self.app.post(
            str('/login'),
            {
                'submit': True,
                'handle': 'sontek',
                'password': 'temp',
            }
        )

        assert b'Your account is not active; please check your e-mail.' \
            in res.body
