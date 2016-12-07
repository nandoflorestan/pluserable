"""Unit tests should be preferred because they are the quickest.

Unit tests go through only one function and they do not hit the database.
"""

from pyramid.registry import Registry
from pluserable import const
from pluserable.strings import UIStringsBase
from .. import PluserableTestCase


class FakeKerno:
    """Mock object for tests."""

    def get_utility(self, name):
        """Return the default utility."""
        if name == const.STRING_CLASS:
            return UIStringsBase
        else:
            raise RuntimeError('Unknown utility: {}'.format(name))


class FastTestCase(PluserableTestCase):
    """Base for unit test cases."""

    def _make_registry(self, **kw):
        r = Registry('testing')
        r.settings = kw
        return r
