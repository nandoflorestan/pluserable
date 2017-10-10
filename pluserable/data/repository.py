"""Repository implementations.

Repositories are persistence strategies.
"""

from pluserable import const
from pluserable.interfaces import IKerno


def instantiate_repository(registry):
    """Return a new instance of the configured repository.

    This must be called only once per request.
    """
    kerno = registry.queryUtility(IKerno)
    session_factory = kerno.get_utility(const.SAS)
    return kerno.Repository(kerno, session_factory)
