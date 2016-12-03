from pyramid import testing
from mock import Mock
from pluserable.resources import RootFactory
from pyramid.security import Authenticated, Allow, ALL_PERMISSIONS
from pluserable import groupfinder
from pluserable.tests.models import User, Group
from . import IntegrationTestBase


class TestInitCase(IntegrationTestBase):

    '''def test_request_factory(self):  # TODO Why is this commented out?
       from pluserable import SignUpRequestFactory
       from pluserable.tests.models import User

       user1 = self.create_user(count=1)
       self.sas.flush()

       with patch('pluserable.unauthenticated_userid') as unauth:
           unauth.return_value = 1
           request = SignUpRequestFactory({})
           request.registry = Mock()
           getUtility = Mock()
           getUtility.return_value = self.sas
           request.registry.getUtility = getUtility

           user = request.user
           assert user == user1'''

    def test_groupfinder(self):
        user1 = self.create_users(count=1)
        group = Group(name='foo', description='bar')
        group.users.append(user1)
        self.sas.flush()

        request = Mock()
        request.user = user1

        results = groupfinder(1, request)

        assert 'group:foo' in results
        assert 'user:%s' % (user1.id) in results
        assert len(results) == 2

    def test_groupfinder_no_groups(self):
        user1, user2 = self.create_users(count=2)
        group = Group(name='foo', description='bar')
        group.users.append(user1)
        self.sas.flush()

        request = Mock()
        request.user = user2

        results = groupfinder(2, request)

        assert len(results) == 1
        assert 'user:%s' % (user2.id) in results
