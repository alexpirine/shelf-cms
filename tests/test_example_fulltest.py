# coding: utf-8

import os

from scripttest import TestFileEnvironment
from unittest import TestCase

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
EXAMPLE_PATH = os.path.join(BASE_PATH, 'examples', 'fulltest')

class TestManagement(TestCase):
    def setUp(self):
        self.env = TestFileEnvironment(
            cwd = EXAMPLE_PATH,
        )

    def test_test_cmd(self):
        r = self.env.run('./manage.py test')
        self.assertEquals(r.stdout, "Hello world!\n")
