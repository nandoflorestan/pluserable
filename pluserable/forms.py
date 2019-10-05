"""Deform forms."""

import deform


class SubmitForm(deform.Form):
    """By default include a "submit" button on a form."""

    def __init__(self, *args, **kwargs):  # noqa
        if not kwargs.get("buttons"):
            kwargs["buttons"] = ("submit",)
        super(SubmitForm, self).__init__(*args, **kwargs)


class BootstrapForm(SubmitForm):
    """Renders out forms using twitter bootstrap templates."""

    def __init__(self, *args, **kwargs):  # noqa
        super(BootstrapForm, self).__init__(*args, **kwargs)

        for child in self.children:
            if isinstance(
                child.widget, deform.widget.TextInputWidget
            ) or isinstance(child.widget, deform.widget.TextAreaWidget):

                if not child.widget.css_class:
                    child.widget.css_class = ""

                if "xlarge" not in child.widget.css_class:
                    child.widget.css_class += " xlarge"


class PluserableForm(BootstrapForm):
    """The standard form we should use throughout our code.

    If we decide to swap our rendering later, we only have to do it in 1 place.
    """
