# coding: utf-8

from unittest import TestCase

class TestHelloWorld(TestCase):
    def test_hello_world(self):
        s = "Hello World!"
        self.assertTrue(s == "Hello World!")
