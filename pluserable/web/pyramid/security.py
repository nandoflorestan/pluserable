# noqa
from typing import List, Optional

from kerno.web.pyramid.typing import KRequest
from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import (
    ACLHelper,
    Authenticated,
    Everyone,
)

from pluserable.data.typing import TTUser


class SecurityPolicy:  # noqa
    def __init__(self, config):  # noqa
        settings = config.get_settings()
        self.authtkt = AuthTktCookieHelper(
            secret=settings["app_secret"],
            wild_domain=False,
            parent_domain=False,
            samesite="strict",
            # Set the Secure flag on the cookie only when serving on https.
            secure=settings.get("scheme_domain_port", "").startswith("https"),
        )
        self.acl = ACLHelper()

    def identity(self, request: KRequest) -> Optional[TTUser]:  # noqa
        adict = self.authtkt.identify(request)
        if adict:
            return request.repo.get_user_by_id(  # type: ignore[attr-defined]
                adict["userid"]
            )
        else:
            return None

    def authenticated_userid(self, request: KRequest) -> Optional[int]:  # noqa
        user = self.identity(request)
        return None if user is None else user.id  # type: ignore[attr-defined]

    def remember(self, request: KRequest, userid: int, **kw):  # noqa
        return self.authtkt.remember(request, userid, **kw)

    def forget(self, request: KRequest, **kw):  # noqa
        return self.authtkt.forget(request, **kw)

    def _effective_principals(self, request: KRequest) -> List[str]:
        principals = [Everyone]
        user = self.identity(request)
        if user is not None:
            principals += [Authenticated, f"u:{user.id}"]
            principals += [str(g) for g in user.groups]
        # print(principals, request.path)
        return principals

    def permits(self, request: KRequest, context, permission: str):  # noqa
        principals = self._effective_principals(request)
        return self.acl.permits(context, principals, permission)


def includeme(config):
    """Stuff that runs upon Pyramid initialization."""
    config.set_security_policy(SecurityPolicy(config))
