"""A functional test makes a fake request and verifies the response content.

It is the slowest kind of test. Not only does it hit the database,
it also generates the content of a response. It passes through all layers.
"""

from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.response import Response
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from webtest import TestApp
from pluserable.tests import PluserableTestCase
from pluserable.tests.models import Base
from pluserable.interfaces import IDBSession


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class FunctionalTestBase(PluserableTestCase):

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
        session_factory = session_factory_from_settings(settings)
        config.set_session_factory(session_factory)

        if settings.get('su.require_activation', True):
            config.include('pyramid_mailer')

        config.include('pyramid_mako')
        config.include('pluserable')

        app = config.make_wsgi_app()
        return app

    def setUp(self):
        """Called before each functional test."""
        settings = self._read_pyramid_settings()
        config = self._initialize_config(settings, DBSession)

        self.engine = engine_from_config(config.registry.settings,
                                         prefix='sqlalchemy.')
        app = self.main(config)

        self.app = TestApp(app)

        # TODO Move up the subtransaction trick
        self.connection = connection = self.engine.connect()

        self.session = app.registry.getUtility(IDBSession)
        self.session.configure(bind=connection)
        # begin a non-ORM transaction
        self.trans = connection.begin()

        Base.metadata.bind = connection

    def tearDown(self):
        """Roll back the Session (including calls to commit())."""
        testing.tearDown()  # Remove Pyramid settings, registry and request
        self.trans.rollback()
        self.session.close()
