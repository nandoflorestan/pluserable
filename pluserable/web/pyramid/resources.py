"""Pyramid resources for an app that integrates pluserable."""

from pyramid.security import Authenticated, Allow, ALL_PERMISSIONS


class BaseFactory:

    def __init__(self, request):  # noqa
        self.request = request


class RootFactory(BaseFactory):

    @property
    def __acl__(self):
        defaultlist = [
            (Allow, 'group:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
        ]
        return defaultlist


class UserFactory(RootFactory):

    def __getitem__(self, key):
        user = self.request.repo.q_user_by_id(key)

        if user:
            user.__parent__ = self
            user.__name__ = key
        return user
