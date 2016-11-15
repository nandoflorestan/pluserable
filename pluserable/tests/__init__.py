"""Tests for *pluserable*."""

import os
from pkg_resources import resource_filename
from paste.deploy.loadwsgi import appconfig
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

here = os.path.dirname(__file__)
# settings = appconfig('config:' + os.path.join(here, 'test.ini'))
settings = appconfig('config:' + resource_filename(__name__, 'test.ini'))

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
