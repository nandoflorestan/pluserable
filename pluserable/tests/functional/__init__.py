"""A functional test makes a fake request and verifies the response content."""

from unittest import TestCase
from pyramid import testing
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.response import Response
from sqlalchemy import engine_from_config
from webtest import TestApp
from pluserable.tests import DBSession, settings
from pluserable.tests.models import Activation, Base, User, Group
from pluserable.interfaces import (
    IUserClass, IActivationClass, IGroupClass, IDBSession)


class FunctionalTestBase(TestCase):

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
