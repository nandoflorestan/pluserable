'''Function that runs when pluserable tests start.'''

from pkg_resources import resource_filename


def pytest_sessionstart():
    from py.test import config

    # Only run database setup on master (in case of xdist/multiproc mode)
    if not hasattr(config, 'slaveinput'):
        from paste.deploy.loadwsgi import appconfig
        from pyramid.config import Configurator
        from sqlalchemy import engine_from_config
        from pluserable.interfaces import IUserClass, IActivationClass
        from pluserable.tests.models import Base, User, Activation

        settings = appconfig('config:' + resource_filename(
            __name__, 'pluserable/tests/test.ini'))
        engine = engine_from_config(settings, prefix='sqlalchemy.')
        print('Creating the tables on the test database %s' % engine)
        config = Configurator(settings=settings)
        # config.scan('pluserable.models')  # but above we import Base
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

        config.registry.registerUtility(User, IUserClass)
        config.registry.registerUtility(Activation, IActivationClass)
