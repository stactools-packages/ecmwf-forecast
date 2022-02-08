import unittest

import stactools.ecmwf_forecast


class TestModule(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(stactools.ecmwf_forecast.__version__)
