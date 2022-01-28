"""Pyramid resources for an app that integrates pluserable."""

from typing import Any, List, Tuple

from pyramid.authorization import Authenticated, Allow, ALL_PERMISSIONS

from pluserable.data.typing import TUser
from pluserable.web.pyramid.typing import PRequest


class BaseFactory:  # noqa
    def __init__(self, request: PRequest):  # noqa
        self.request = request


class RootFactory(BaseFactory):  # noqa
    @property
    def __acl__(self) -> List[Tuple[Any, Any, Any]]:
        defaultlist = [
            (Allow, "group:admin", ALL_PERMISSIONS),
            (Allow, Authenticated, "view"),
        ]
        return defaultlist


class UserFactory(RootFactory):  # noqa
    def __getitem__(self, key: int) -> TUser:
        user = self.request.repo.get_user_by_id(key)

        if user:
            user.__parent__ = self
            user.__name__ = key
        return user
