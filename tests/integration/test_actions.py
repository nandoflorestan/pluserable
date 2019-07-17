"""Integration tests for actions."""

from pluserable.actions import get_activation_link

from tests.integration import IntegrationTestBase


class TestGetActivationLink(IntegrationTestBase):  # noqa

    def test_with_route_url(self):  # noqa
        link = get_activation_link(
            self.get_request(), user_id=42, code='alfafa')
        assert link == 'http://example.com/activate/42/alfafa'

    def test_with_route_path(self):  # noqa
        request = self.get_request()
        request.registry.settings['scheme_domain_port'] = \
            'https://test.fairsplit.com'
        link = get_activation_link(request, user_id=42, code='alfafa')
        assert link == 'https://test.fairsplit.com/activate/42/alfafa'
