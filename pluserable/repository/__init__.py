"""This namespace contains at least one Repository implementation.

Repositories are persistence strategies.
"""

from pluserable.interfaces import IRepositoryClass


def instantiate_repository(registry):
    """Return a new instance of the configured repository."""
    return registry.queryUtility(IRepositoryClass)(registry)
