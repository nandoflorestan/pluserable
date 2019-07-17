"""Repository implementations.

Repositories are persistence strategies.
"""

from kerno.web.pyramid import IKerno


def instantiate_repository(registry):
    """Return a new instance of the configured repository.

    This must be called only once per request.
    """
    return registry.queryUtility(IKerno).new_repo()
