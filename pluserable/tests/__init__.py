import unittest
from webtest import TestApp
from sqlalchemy import engine_from_config
from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.response import Response
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension
from mock import Mock
from pluserable.tests.models import Activation, Base, User
from pluserable.interfaces import IUserClass, IActivationClass
from pkg_resources import resource_filename
from pluserable.interfaces import IDBSession
import os

here = os.path.dirname(__file__)
# settings = appconfig('config:' + os.path.join(here, 'test.ini'))
settings = appconfig('config:' + resource_filename(__name__, 'test.ini'))

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sessionmaker()

    def setUp(self):
        self.config = testing.setUp()

        self.connection = connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = connection.begin()

        # bind an individual Session to the connection
        self.session = self.Session(bind=connection)

        self.config.registry.registerUtility(self.session, IDBSession)
        self.config.registry.registerUtility(Activation, IActivationClass)
        self.config.registry.registerUtility(User, IUserClass)

        Base.metadata.bind = connection

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
        self.connection.close()


class UnitTestBase(BaseTestCase):
    def get_request(self, post=None, request_method='GET'):
        if not post:
            post = {}
        request = testing.DummyRequest(post)
        request.session = Mock()
        request.method = request_method
        return request


class IntegrationTestBase(unittest.TestCase):
    def main(self, global_config, **settings):
        settings['su.using_tm'] = True

        config = global_config
        config.add_settings(settings)

        config.registry.registerUtility(Activation, IActivationClass)
        config.registry.registerUtility(User, IUserClass)

        def index(request):
            return Response('index!')

        config.add_route('index', '/')
        config.add_view(index, route_name='index')

        authz_policy = ACLAuthorizationPolicy()
        config.set_authorization_policy(authz_policy)

        authn_policy = AuthTktAuthenticationPolicy('secret')
        config.set_authentication_policy(authn_policy)

        session_factory = session_factory_from_settings(settings)

        config.set_session_factory(session_factory)

        config.registry.registerUtility(DBSession, IDBSession)

        if settings.get('su.require_activation', True):
            config.include('pyramid_mailer')

        config.include('pyramid_mako')
        config.include('pluserable')

        app = config.make_wsgi_app()
        return app

    def setUp(self):
        self.engine = engine_from_config(settings, prefix='sqlalchemy.')
        config = testing.setUp()
        app = self.main(config, **settings)
        self.app = TestApp(app)
        self.connection = connection = self.engine.connect()

        self.session = app.registry.getUtility(IDBSession)
        self.session.configure(bind=connection)
        # begin a non-ORM transaction
        self.trans = connection.begin()

        Base.metadata.bind = connection

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()
