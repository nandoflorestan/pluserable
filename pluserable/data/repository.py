"""Repository implementations.

Repositories are persistence strategies.
"""

from pluserable import const
from kerno.web.pyramid import IKerno


def instantiate_repository(registry):
    """Return a new instance of the configured repository.

    This must be called only once per request.
    """
    kerno = registry.queryUtility(IKerno)
    session_factory = kerno.get_utility(const.SAS)
    assert session_factory, "No session factory has been configured!"
    return kerno.Repository(kerno, session_factory)
