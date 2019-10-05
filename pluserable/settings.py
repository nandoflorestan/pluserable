"""Provides a default pluserable configuration."""

from kerno.typing import DictStr

from pluserable.web.pyramid.resources import UserFactory
from pluserable.views import get_pyramid_views_config


def get_default_pluserable_settings() -> DictStr:
    """Return default pluserable setings.

    In order to customize Pluserable to its purpose, user code calls this
    and manipulates the returned dictionary.  Here we return defaults
    that user code can change.
    """
    return {
        # Pyramid routes
        "routes": {  # route_name: route_kwargs
            "login": {"pattern": "/login"},
            "logout": {"pattern": "/logout"},
            "register": {"pattern": "/register"},
            "activate": {
                "pattern": "/activate/{user_id}/{code}",
                "factory": UserFactory,
            },
            "forgot_password": {"pattern": "/forgot_password"},
            "reset_password": {"pattern": "/reset_password/{code}"},
            "profile": {
                "pattern": "/profile/{user_id}",
                "factory": UserFactory,
                "traverse": "/{user_id}",
            },
            "edit_profile": {"pattern": "/edit_profile"},
        },
        # Pyramid views
        "views": get_pyramid_views_config(),
    }
