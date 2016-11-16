"""Pluserable integration for the Pyramid web framework."""

from pyramid.security import unauthenticated_userid
from pluserable.repository import instantiate_repository


def get_user(request):
    """Return the user making the current request, or None."""
    userid = unauthenticated_userid(request)
    if userid is None:
        return None
    repo = instantiate_repository(request.registry)
    return repo.get_by_id(request, userid)
