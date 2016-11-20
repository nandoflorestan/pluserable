from pyramid import testing
from . import IntegrationTestBase


class TestResources(IntegrationTestBase):

    def test_user_factory(self):
        from pluserable.resources import UserFactory
        from pluserable.tests.models import User
        from pluserable.interfaces import IUserClass
        self.config.registry.registerUtility(User, IUserClass)

        user = User(username='sagan', email='carlsagan@nasa.org')
        user.password = 'foo'
        self.sas.add(user)
        self.sas.commit()

        request = testing.DummyRequest()
        factory = UserFactory(request)

        fact_user = factory[user.id]

        assert factory.request == request
        assert user == fact_user
