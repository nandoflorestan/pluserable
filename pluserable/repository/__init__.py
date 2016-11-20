"""This namespace contains at least one Repository implementation.

Repositories are persistence strategies.
"""

from pluserable.const import REPOSITORY
from pluserable.interfaces import IDBSession, IMundi


def instantiate_repository(registry):
    """Return a new instance of the configured repository.

    This must be called only once per request.
    """
    mundi = registry.queryUtility(IMundi)
    session_factory = registry.queryUtility(IDBSession)
    return mundi.get_utility(REPOSITORY)(mundi, session_factory)
