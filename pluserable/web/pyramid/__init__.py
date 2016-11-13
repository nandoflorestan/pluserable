"""Pluserable integration for the Pyramid web framework."""

from pyramid.security import unauthenticated_userid
from pluserable.interfaces import IUserClass


def get_user(request):
    """Return the current user object, or None."""
    userid = unauthenticated_userid(request)
    user_class = request.registry.queryUtility(IUserClass)
    if userid is not None:
        return user_class.get_by_id(request, userid)
    return None
