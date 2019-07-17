"""Unit tests should be preferred because they are the quickest to run.

Unit tests go through only one function and they do not hit the database.
"""

from unittest.mock import Mock

from pyramid.registry import Registry
from pluserable import const
from pluserable.strings import UIStringsBase
from .. import UnitTestCase


class FastTestCase(UnitTestCase):
    """Base for unit test cases."""

    def _make_registry(self, **kw):
        r = Registry('testing')
        r.settings = kw
        return r

    def _fake_kerno(self, utilities={}):
        kerno = Mock()
        kerno.utilities = {
            const.STRING_CLASS: UIStringsBase,
            **utilities
        }
