# noqa
from unittest import TestCase

from pyramid import testing
from pyramid.authorization import Authenticated, Allow, ALL_PERMISSIONS

from pluserable.web.pyramid.resources import RootFactory


class TestInitCase(TestCase):  # noqa
    def test_root_factory(self):  # noqa
        root_factory = RootFactory(testing.DummyRequest())
        assert len(root_factory.__acl__) == 2

        for ace in root_factory.__acl__:
            assert ace[0] == Allow
            if ace[1] == "group:admin":
                assert ace[2] == ALL_PERMISSIONS
            elif ace[1] == Authenticated:
                assert ace[2] == "view"
