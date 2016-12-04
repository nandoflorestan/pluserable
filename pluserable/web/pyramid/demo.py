"""Demonstration."""

from pyramid.config import Configurator


def main(global_config, **settings):
    """Return a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    # secret = 'asdfasdf'
    # config.set_authorization_policy(AuthorizationPolicy())
    # config.set_authentication_policy(AuthTktAuthenticationPolicy(secret))
    # config.set_session_factory(UnencryptedCookieSessionFactoryConfig(secret))

    # config.set_root_factory(RootFactory)
    # config.set_request_factory(RequestFactory)

    config.scan()
    return config.make_wsgi_app()
