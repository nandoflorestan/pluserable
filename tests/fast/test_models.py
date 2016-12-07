"""Unit tests for pure methods of models."""

from datetime import datetime
from tests.models import Activation, Group
from . import FastTestCase


class TestActivation(FastTestCase):

    def test_create_activation_with_valid_until(self):
        dt = datetime.utcnow()
        activation1 = Activation()
        activation1.valid_until = dt
        assert activation1.valid_until == dt


class TestGroup(FastTestCase):

    def test_constructor(self):
        group = Group(name='foo', description='bar')
        assert group.name == 'foo'
        assert group.description == 'bar'

    def test_repr(self):
        group = Group(name='foo', description='bar')
        assert repr(group) == '<Group: foo>'


class TestUser(FastTestCase):

    def test_check_password_empty_password_returns_false(self):
        user = self.create_users(count=1)
        assert user.check_password(password='') is False

    def test_repr(self):
        user = self.create_users(count=1)
        assert repr(user) == '<User: carlsagan1@nasa.gov>'
