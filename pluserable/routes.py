# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .resources import UserFactory


routes = {  # route_name: route_kwargs
    'login': {'pattern': '/login'},
    'logout': {'pattern': '/logout'},
    'register': {'pattern': '/register'},
    'activate': {'pattern': '/activate/{user_id}/{code}',
                 'factory': UserFactory},
    'forgot_password': {'pattern': '/forgot_password'},
    'reset_password': {'pattern': '/reset_password/{code}'},

    'profile': {'pattern': '/profile/{user_id}', 'factory': UserFactory,
                'traverse': "/{user_id}"},
    'edit_profile': {'pattern': '/profile/{user_id}/edit',
                     'factory': UserFactory, 'traverse': "/{user_id}"},
}


def includeme(config):
    """Add routes to the config.  The ``routes`` dictionary can be manipulated
        before this is called and this will affect view registration, too.
        But TODO: we need a better way of allowing user code
        to choose which routes it wants; the ``routes`` dict should not be
        a global variable.
        """
    for name, kw in routes.items():
        config.add_route(name, **kw)
