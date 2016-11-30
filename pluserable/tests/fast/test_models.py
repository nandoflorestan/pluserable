"""Unit tests for pure methods of models."""

from pluserable.tests.models import Group
from . import FastTestCase


class TestGroup(FastTestCase):

    def test_constructor(self):
        group = Group(name='foo', description='bar')
        assert group.name == 'foo'
        assert group.description == 'bar'
