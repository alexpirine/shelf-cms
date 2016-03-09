# coding: utf-8

import os
import shutil

from scripttest import TestFileEnvironment
from unittest import TestCase

TESTS_PATH = os.path.dirname(__file__)
TESTS_OUTPUT_PATH = os.path.join(TESTS_PATH, 'tests-output')
BASE_PATH = os.path.dirname(TESTS_PATH)
EXAMPLE_PATH = os.path.join(BASE_PATH, 'examples', 'fulltest')
DB_PATH = os.path.join(EXAMPLE_PATH, 'demo.sqlite')

ADMIN_USER = 'admin@localhost'
ADMIN_PWD = 'admin31!'

class TestManagement(TestCase):
    @staticmethod
    def _remvoe_db_file():
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

    def setUp(self):
        # removes the database file
        self._remvoe_db_file()

        # sets up ScriptTest testing environement
        self.env = TestFileEnvironment(
            base_path = TESTS_OUTPUT_PATH,
            start_clear = True,
        )
        os.chdir(TESTS_OUTPUT_PATH)

    def tearDown(self):
        # restores current directory
        os.chdir(BASE_PATH)

        # removes files created during the tests
        self.env.clear()

        # remove the test output folder
        shutil.rmtree(TESTS_OUTPUT_PATH)

        # removes the database file
        self._remvoe_db_file()

    def test_test_cmd(self):
        r = self.env.run('%s test' % os.path.join(EXAMPLE_PATH, 'manage.py'))
        self.assertEquals(r.stdout, "Hello world!\n")

    def test_create_admin(self):
        r = self.env.run('%s create_admin' % os.path.join(EXAMPLE_PATH, 'manage.py'))
        self.assertEquals(r.stdout, "Admin user %(user)s (password: %(pwd)s) created successfully.\n" % {
            'user': ADMIN_USER,
            'pwd': ADMIN_PWD,
        })

        r = self.env.run('%s create_admin' % os.path.join(EXAMPLE_PATH, 'manage.py'))
        self.assertEquals(r.stdout, "Admin user %(user)s already exists!\n" % {
            'user': ADMIN_USER,
        })
