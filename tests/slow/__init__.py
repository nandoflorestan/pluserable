"""A functional test makes a fake request and verifies the response content.

It is the slowest kind of test. Not only does it hit the database,
it also generates the content of a response. It passes through all layers.
"""

from bag.sqlalchemy.tricks import SubtransactionTrick
from kerno.web.pyramid import IKerno
from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.response import Response
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy.orm import scoped_session, sessionmaker
from webtest import TestApp

from tests import AppTestCase, _make_eko


class FunctionalTestBase(AppTestCase):
    """Base class for tests that make a request and check the response."""

    def main(self, config):
        def index(request):
            return Response('index!')

        config.add_route('index', '/')
        config.add_view(index, route_name='index')

        authz_policy = ACLAuthorizationPolicy()
        config.set_authorization_policy(authz_policy)

        authn_policy = AuthTktAuthenticationPolicy('secret')
        config.set_authentication_policy(authn_policy)

        settings = config.registry.settings

        # Pyramid sessions
        session_factory = SignedCookieSessionFactory('sum_see_krert')
        config.set_session_factory(session_factory)

        if settings.get('su.require_activation', True):
            config.include('pyramid_mailer')  # TODO Avoid test emails

        config.include('pyramid_mako')
        config.include('pluserable')

        app = config.make_wsgi_app()
        return app

    def setUp(self):
        """Stuff called before each functional test."""
        self.subtransaction = SubtransactionTrick(
            engine=self.engine,
            sessionmaker=scoped_session(sessionmaker())
        )
        self.sas = self.subtransaction.sas  # TODO REMOVE

        self.kerno = _make_eko(sas_factory=self.sas).kerno
        self.repo = self.kerno.new_repo()

        config = testing.setUp(settings=self.settings)
        config.registry.registerUtility(self.kerno, IKerno)

        app = self.main(config)
        self.app = TestApp(app)

    def tearDown(self):
        """Roll back the Session (including calls to commit())."""
        testing.tearDown()  # Remove Pyramid settings, registry and request
        self.subtransaction.close()  # roll back the session
