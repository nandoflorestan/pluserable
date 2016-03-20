# -*- coding: utf-8 -*-

'''Tests'''

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pkg_resources import resource_filename


def pytest_sessionstart():
    from py.test import config

    # Only run database setup on master (in case of xdist/multiproc mode)
    if not hasattr(config, 'slaveinput'):
        from pyramid.config import Configurator
        from pluserable.tests.models import Base
        from pluserable.settings import get_default_pluserable_settings
        from paste.deploy.loadwsgi import appconfig
        from sqlalchemy import engine_from_config

        settings = appconfig('config:' + resource_filename(
            __name__, 'pluserable/tests/test.ini'))
        engine = engine_from_config(settings, prefix='sqlalchemy.')
        print('Creating the tables on the test database %s' % engine)
        config = Configurator(settings=settings)
        # config.scan('pluserable.models')  # but above we import Base
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
