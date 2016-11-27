"""Unit tests should be preferred because they are the quickest.

Unit tests go through only one function and they do not hit the database.
"""

from .. import PluserableTestCase
from pluserable.interfaces import IUIStrings
from pluserable.strings import UIStringsBase
from pyramid.registry import Registry


class FastTestCase(PluserableTestCase):
    """Base for unit test cases."""

    def _make_registry(self, **kw):
        r = Registry('testing')
        r.settings = kw
        r.registerUtility(UIStringsBase, IUIStrings)
        return r
