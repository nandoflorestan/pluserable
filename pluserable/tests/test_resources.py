# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyramid import testing
from pluserable.tests import UnitTestBase


class TestResources(UnitTestBase):
    def test_user_factory(self):
        from pluserable.resources import UserFactory
        from pluserable.tests.models import User
        from pluserable.interfaces import IUserClass
        self.config.registry.registerUtility(User, IUserClass)

        user = User(username='sontek', email='sontek@gmail.com')
        user.password = 'foo'
        self.session.add(user)
        self.session.commit()

        request = testing.DummyRequest()
        factory = UserFactory(request)

        fact_user = factory[user.id]

        assert factory.request == request
        assert user == fact_user
