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

    @classmethod
    def setUpClass(cls):
        # removes the database file
        cls._remvoe_db_file()

        # sets up ScriptTest testing environement
        cls.env = TestFileEnvironment(
            base_path = TESTS_OUTPUT_PATH,
            start_clear = True,
        )

        # sets up working directory
        os.chdir(TESTS_OUTPUT_PATH)

        # sets up /dev/null
        cls.fnull = open(os.devnull, 'wb')

        # creates admin user
        p = subprocess.Popen(
            '%s create_admin' % os.path.join(EXAMPLE_PATH, 'manage.py'),
            shell = True, stdout = cls.fnull,
        )
        p.wait()

        # runs the testing server
        cls.server_p = Process(target = app.run, args = (TEST_HOST, TEST_PORT), kwargs = {'use_reloader': False})
        cls.server_p.start()
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        # stops the testing server
        cls.server_p.terminate()

        # closes /dev/null
        cls.fnull.close()

        # restores current directory
        os.chdir(BASE_PATH)

        # removes files created during the tests
        cls.env.clear()

        # remove the test output folder
        shutil.rmtree(TESTS_OUTPUT_PATH)

        # removes the database file
        cls._remvoe_db_file()

    def setUp(self):
        # sets up the browser
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1024, 768)
        self.driver.implicitly_wait(3)

        # logs in
        self.driver.get('http://127.0.0.1:5000/admin/')
        self.driver.find_element_by_id('email').send_keys(ADMIN_USER)
        self.driver.find_element_by_id('password').send_keys(ADMIN_PWD)
        self.driver.find_element_by_id('remember').click()
        self.driver.find_element_by_id('submit').click()
        self.assertEquals(self.driver.title, "Home - Admin")

    def tearDown(self):
        # closes the browser
        self.driver.quit()

    def test_user_list(self):
        # goes to the user list
        self.driver.get('http://127.0.0.1:5000/admin/user/')
        self.assertEquals(self.driver.current_url, 'http://127.0.0.1:5000/admin/user/')
        self.assertEquals(self.driver.title, "User - Admin")

    def test_library_create_folder(self):
        # goes to the library files list
        self.driver.get('http://127.0.0.1:5000/admin/fileadmin/')

        # creates a new folder
        folder_name = 'test_library'
        folder_path = os.path.join(app.config['MEDIA_ROOT'], folder_name)
        self.driver.find_element_by_css_selector('.navbar-fixed-bottom li.actions.new>a').click()
        time.sleep(1)
        self.driver.find_element_by_id('name').send_keys(folder_name)
        self.driver.find_element_by_css_selector('#dir-modal ul.nav>li.actions.validate>a').click()
        self.assertTrue("Successfully created directory: test_library" in self.driver.find_element_by_css_selector('#wrap .alert.alert-info').text)
        self.assertTrue(os.path.exists(folder_path))
        os.rmdir(folder_path)

    def test_new_blog_entry(self):
        # goes to the posts list
        self.driver.get('http://127.0.0.1:5000/admin/post/')

        # fills-in a new post entry
        self.driver.find_element_by_css_selector('.navbar-fixed-bottom ul.navbar-right>li.actions>a>i.fa-plus').click()
        self.assertEquals(self.driver.current_url, 'http://127.0.0.1:5000/admin/post/new/?url=%2Fadmin%2Fpost%2F')
        self.driver.find_element_by_id('publication_date').click()
        self.driver.find_element_by_css_selector('.daterangepicker .calendar-date td.today').click()
        self.driver.find_element_by_id('title-fr').send_keys("Test title")

        # submits the new post entry
        self.driver.find_element_by_css_selector('.navbar-fixed-bottom ul.navbar-right>li.actions>a.save-model>i.fa-check').click()
        self.assertEquals(self.driver.current_url, 'http://127.0.0.1:5000/admin/post/')
        self.assertEquals(len(self.driver.find_elements_by_css_selector('#wrap table.model-list>tbody>tr')), 1)
