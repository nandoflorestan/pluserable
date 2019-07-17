# noqa

from pluserable.web.pyramid.resources import UserFactory

from tests.integration import IntegrationTestBase


class TestResources(IntegrationTestBase):  # noqa

    def test_user_factory(self):  # noqa
        user = self.create_users(count=1)
        self.sas.flush()  # so the user has an id
        request = self.get_request()
        factory = UserFactory(request)
        fact_user = factory[user.id]

        assert factory.request is request
        assert user is fact_user
