# coding: utf-8

import os
import shutil
import signal
import subprocess
import time

from selenium import webdriver
from scripttest import TestFileEnvironment
from unittest import TestCase

TESTS_PATH = os.path.dirname(__file__)
TESTS_OUTPUT_PATH = os.path.join(TESTS_PATH, 'tests-output')
BASE_PATH = os.path.dirname(TESTS_PATH)
EXAMPLE_PATH = os.path.join(BASE_PATH, 'examples', 'fulltest')
DB_PATH = os.path.join(EXAMPLE_PATH, 'demo.sqlite')

TEST_HOST = '127.0.0.1'
TEST_PORT = 5000
ADMIN_USER = 'admin@localhost'
ADMIN_PWD = 'admin31!'

class TestManagement(TestCase):
    @staticmethod
    def _remvoe_db_file(self):
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

        # sets up working directory
        os.chdir(TESTS_OUTPUT_PATH)

        # sets up /dev/null
        self.fnull = open(os.devnull, 'wb')

        # creates admin user
        p = subprocess.Popen(
            '%s create_admin' % os.path.join(EXAMPLE_PATH, 'manage.py'),
            shell = True, stdout = self.fnull,
        )
        p.wait()

        # runs the testing server
        self.server_p = subprocess.Popen(
            '%(cmd)s runserver -h %(test_host)s -p %(test_port)d' % {
                'cmd': os.path.join(EXAMPLE_PATH, 'manage.py'),
                'test_host': TEST_HOST,
                'test_port': TEST_PORT,
            },
            shell = True, stdout=self.fnull, stderr=self.fnull, preexec_fn=os.setsid,
        )
        time.sleep(3)

        # sets up the browser
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)

    def tearDown(self):
        # closes the browser
        self.driver.quit()

        # stops the testing server
        os.killpg(os.getpgid(self.server_p.pid), signal.SIGTERM)
        self.server_p.wait()

        # closes /dev/null
        self.fnull.close()

        # restores current directory
        os.chdir(BASE_PATH)

        # removes files created during the tests
        self.env.clear()

        # remove the test output folder
        shutil.rmtree(TESTS_OUTPUT_PATH)

        # removes the database file
        self._remvoe_db_file()

    def test_login(self):
        self.driver.get('http://127.0.0.1:5000/admin/')
        self.driver.find_element_by_id('email').send_keys(ADMIN_USER)
        self.driver.find_element_by_id('password').send_keys(ADMIN_PWD)
        self.driver.find_element_by_id('remember').click()
        self.driver.find_element_by_id('submit').click()
        self.assertEquals(self.driver.title, "Home - Admin")

