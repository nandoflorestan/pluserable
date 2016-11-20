from unittest import TestCase
from pluserable.interfaces import ILoginSchema, ILoginForm


class TestInterfaces(TestCase):

    def test_suloginschema(self):
        """Shouldn't be able to instantiate the interface."""
        def make_session():
            ILoginSchema('1')

        self.assertRaises(TypeError, make_session)

    def test_suloginform(self):
        """Shouldn't be able to instantiate the interface."""
        def make_session():
            ILoginForm('1')

        self.assertRaises(TypeError, make_session)
