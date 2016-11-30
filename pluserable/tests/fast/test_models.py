"""Unit tests for pure methods of models."""

from datetime import datetime
from pluserable.models import BaseModel
from pluserable.tests.models import Activation, Group
from . import FastTestCase


class TestModel(BaseModel):
    pass


class TestBaseModel(FastTestCase):

    def test_tablename(self):
        model = TestModel()
        assert model.__tablename__ == 'test_model'


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
