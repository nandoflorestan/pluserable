"""Custom exceptions raised by pluserable."""

from kerno.typing import DictStr

from pluserable.web.pyramid.typing import PRequest


class AuthenticationFailure(Exception):
    """Raised when handle and password do not match, during login."""

    seconds: int  # user must wait until next login attempt


class FormValidationFailure(Exception):  # TODO REMOVE
    def __init__(self, form, exc):  # noqa
        Exception.__init__(self)
        self.form = form
        self.exc = exc

    def result(self, request: PRequest, **cstruct) -> DictStr:  # noqa
        retail = request.kerno.pluserable_settings[  # type: ignore[attr-defined]
            "deform_retail"
        ]
        if retail:
            form = self.form
            errors = self.form.error.children
        else:
            form = self.exc
            errors = self.exc.error.children

        for k, v in cstruct.items():
            form.cstruct[k] = v

        if not retail:
            form = form.render()
        return {"form": form, "errors": errors}
