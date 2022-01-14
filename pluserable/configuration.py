"""At startup pluserable validates its configuration settings."""

from bag.email_validator import DomainValidator
import colander as c
from kerno.typing import DictStr

domain_validator = DomainValidator()


class DomainsSchema(c.SchemaNode):
    """Colander schema that validates a list of domain names."""

    schema_type = c.String

    def validator(self, node, val):
        """Colander validator for a domain name."""
        # When reading an INI file a sequence comes as a single string.
        domains = val.split("\n") if isinstance(val, str) else val

        for domain in domains:
            domain, error = domain_validator.validate_domain(domain.strip())
            if error:
                raise c.Invalid(node, error)


class PluserableConfigSchema(c.MappingSchema):
    """Colander validation schema for the entire configuration dictionary.

    When using a INI configuration file, these settings are placed in
    the ``[pluserable]`` section.
    """

    autologin = c.SchemaNode(
        c.Bool(),
        missing=False,
        doc="Whether to log a user in directly after registration",
    )
    email_domains_blacklist = DomainsSchema()
    login_redirect = c.SchemaNode(c.String(), missing="index")
    logout_redirect = c.SchemaNode(c.String(), missing="index")
    require_activation = c.SchemaNode(
        c.Bool(),
        missing=True,
        doc="When true users can only log in after confirming their email address",
    )


def validate_pluserable_config(adict: DictStr):
    """Validate pluserable settings and return a clean dictionary."""
    schema = PluserableConfigSchema()
    clean = schema.deserialize(adict)
    return clean
