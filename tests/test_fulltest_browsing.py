# coding: utf-8

import os
import random
import shutil
import subprocess
import sys
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
TEST_PORT = 5000 + random.randint(0, 5000)
ADMIN_USER = 'admin@localhost'
ADMIN_PWD = 'admin31!'

app = create_app()

class TestBrowsing(TestCase):
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
        cls.env.clear()

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

        # sets up the browser
        cls.driver = webdriver.PhantomJS()
        cls.driver.set_window_size(1400, 800)
        cls.driver.implicitly_wait(3)

        # logs in
        cls.driver.get('http://%(host)s:%(port)d/admin/' % {'host': TEST_HOST, 'port': TEST_PORT})
        cls.driver.find_element_by_id('email').send_keys(ADMIN_USER)
        cls.driver.find_element_by_id('password').send_keys(ADMIN_PWD)
        cls.driver.find_element_by_id('remember').click()
        cls.driver.find_element_by_id('submit').click()
        assert cls.driver.current_url == 'http://%(host)s:%(port)d/admin/' % {'host': TEST_HOST, 'port': TEST_PORT}

    @classmethod
    def tearDownClass(cls):
        # closes the browser
        cls.driver.quit()

        # stops the testing server
        cls.server_p.terminate()

        # closes /dev/null
        cls.fnull.close()

        # restores current directory
        os.chdir(BASE_PATH)

        # removes the database file
        cls._remvoe_db_file()

    def tearDown(self):
        if not sys.exc_info()[0]:
            return

        try:
            file_name = '%s.%s.png' % (self.__class__.__name__, self._testMethodName)
            file_path = os.path.join(TESTS_OUTPUT_PATH, file_name)
            self.driver.save_screenshot(file_path)
        except:
            pass

    def test_user_list(self):
        # goes to the user list
        self.driver.get('http://%(host)s:%(port)d/admin/user/' % {'host': TEST_HOST, 'port': TEST_PORT})
        self.assertEquals(self.driver.current_url, 'http://%(host)s:%(port)d/admin/user/' % {'host': TEST_HOST, 'port': TEST_PORT})
        self.assertEquals(self.driver.title, "User - Admin")

    def test_library_create_folder(self):
        # goes to the library files list
        self.driver.get('http://%(host)s:%(port)d/admin/fileadmin/' % {'host': TEST_HOST, 'port': TEST_PORT})
        self.assertEquals(self.driver.current_url, 'http://%(host)s:%(port)d/admin/fileadmin/' % {'host': TEST_HOST, 'port': TEST_PORT})

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
        self.driver.get('http://%(host)s:%(port)d/admin/post/' % {'host': TEST_HOST, 'port': TEST_PORT})
        self.assertEquals(self.driver.current_url, 'http://%(host)s:%(port)d/admin/post/' % {'host': TEST_HOST, 'port': TEST_PORT})

        # fills-in a new post entry
        self.driver.find_element_by_css_selector('.navbar-fixed-bottom ul.navbar-right>li.actions>a>i.fa-plus').click()
        self.driver.find_element_by_id('publication_date').click()
        self.driver.find_element_by_css_selector('.daterangepicker .calendar-date td.today').click()
        self.driver.find_element_by_id('title-fr').send_keys("Test title")

        # submits the new post entry
        self.driver.find_element_by_css_selector('.navbar-fixed-bottom ul.navbar-right>li.actions>a.save-model>i.fa-check').click()
        self.assertEquals(self.driver.current_url, 'http://%(host)s:%(port)d/admin/post/' % {'host': TEST_HOST, 'port': TEST_PORT})
        self.assertEquals(len(self.driver.find_elements_by_css_selector('#wrap table.model-list>tbody>tr')), 1)
