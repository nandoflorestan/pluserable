"""This namespace contains at least one Repository implementation.

Repositories are persistence strategies.
"""

from pluserable.const import REPOSITORY
from pluserable.interfaces import IMundi


def instantiate_repository(registry):
    """Return a new instance of the configured repository."""
    mundi = registry.queryUtility(IMundi)
    return mundi.get_utility(REPOSITORY)(mundi)
