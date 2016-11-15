"""Schemas for tests."""

import colander as c
import deform


class ProfileSchema(c.Schema):

    username = c.SchemaNode(
        c.String(),
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        missing=c.null,
    )
    email = c.SchemaNode(c.String(), validator=c.Email())
    first = c.SchemaNode(c.String())
    last = c.SchemaNode(c.String())
    password = c.SchemaNode(
        c.String(),
        validator=c.Length(min=2),
        widget=deform.widget.CheckedPasswordWidget(),
        missing=c.null
    )
