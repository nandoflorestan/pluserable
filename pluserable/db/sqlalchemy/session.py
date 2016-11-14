"""The app registers the session as a utility, then we retrieve it here."""

from pluserable.interfaces import IDBSession


def get_session(request):
    """Magic to find a workable SQLAlchemy session."""
    if hasattr(request, 'db_session'):
        return request.db_session
    elif hasattr(request, 'sas'):
        return request.sas

    session = request.registry.getUtility(IDBSession)
    if session is None:
        raise RuntimeError(
            'You need to let pluserable know what SQLAlchemy session to use.'
        )

    is_scoped_session = hasattr(session, 'query')

    if callable(session) and not is_scoped_session:
        return session(request)
    else:
        return session
