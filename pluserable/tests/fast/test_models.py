"""Unit tests for pure methods of models."""

from datetime import datetime
from pluserable.tests.models import Activation, Base, Group
from . import FastTestCase
from sqlalchemy import Column
from sqlalchemy.types import DateTime


class SomeModel(Base):

    start_date = Column(DateTime)


class TestBaseModel(FastTestCase):

    def test_tablename(self):
        model = SomeModel()
        assert model.__tablename__ == 'some_model'

    def test_json(self):
        model = SomeModel()
        model.id = 1
        model.start_date = datetime.now()

        data = {'id': 1, 'start_date': model.start_date.isoformat()}
        assert model.__json__() == data


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
