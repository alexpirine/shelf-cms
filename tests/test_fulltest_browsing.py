# coding: utf-8

import os
import shutil
import subprocess
import time

from multiprocessing import Process
from scripttest import TestFileEnvironment
from selenium import webdriver
from unittest import TestCase

from examples.fulltest.app import create_app

TESTS_PATH = os.path.dirname(__file__)
TESTS_OUTPUT_PATH = os.path.join(TESTS_PATH, 'tests-output')
BASE_PATH = os.path.dirname(TESTS_PATH)
EXAMPLE_PATH = os.path.join(BASE_PATH, 'examples', 'fulltest')
DB_PATH = os.path.join(EXAMPLE_PATH, 'demo.sqlite')

TEST_HOST = '127.0.0.1'
TEST_PORT = 5000
ADMIN_USER = 'admin@localhost'
ADMIN_PWD = 'admin31!'

app = create_app()

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
        self.server_p = Process(target = app.run, args = (TEST_HOST, TEST_PORT), kwargs = {'use_reloader': False})
        self.server_p.start()
        time.sleep(5)

        # sets up the browser
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)

    def tearDown(self):
        # closes the browser
        self.driver.quit()

        # stops the testing server
        self.server_p.terminate()

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

        self.driver.find_element_by_css_selector('ul.nav>li>a[href="/admin/user/"]').click()
        self.assertEquals(self.driver.current_url, "http://127.0.0.1:5000/admin/user/")
        self.assertEquals(self.driver.title, "User - Admin")

