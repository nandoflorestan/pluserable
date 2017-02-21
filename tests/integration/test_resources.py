from pyramid import testing
from pluserable.data.repository import instantiate_repository
from pluserable.web.pyramid.resources import UserFactory
from . import IntegrationTestBase


class TestResources(IntegrationTestBase):

    def test_user_factory(self):
        user = self.create_users(count=1)
        self.sas.flush()  # so the user has an id
        request = testing.DummyRequest()
        request.repo = instantiate_repository(self.config.registry)
        factory = UserFactory(request)
        fact_user = factory[user.id]

        assert factory.request is request
        assert user is fact_user
