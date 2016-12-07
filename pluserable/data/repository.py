"""This namespace contains at least one Repository implementation.

Repositories are persistence strategies.
"""

from pluserable.const import REPOSITORY
from pluserable.interfaces import IDBSession, IKerno


def instantiate_repository(registry):
    """Return a new instance of the configured repository.

    This must be called only once per request.
    """
    kerno = registry.queryUtility(IKerno)
    session_factory = registry.queryUtility(IDBSession)
    return kerno.get_utility(REPOSITORY)(kerno, session_factory)
