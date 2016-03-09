#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

TESTING_TOOLS = [
    'selenium',
    'scripttest',
    'nose',
]

setup(
    name='ShelfCMS',
    version='0.12.3',
    url='https://github.com/iriahi/shelf-cms',
    license='BSD',
    author='Ismael Riahi',
    author_email='ismael@batb.fr',
    description="""Enhancing flask microframework with beautiful admin
                and cms-like features""",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Admin',
        'Flask-Babel',
        'Flask-Principal',
        'Flask-SQLAlchemy',
        'Flask-Script',
        'Flask-Security',
        'Flask-WTF',
        'Jinja2',
        'Pillow',
        'SQLAlchemy',
        'WTForms',
        'Werkzeug',
        'bcrypt',
        'google-api-python-client',
        'humanize',
        'pyOpenSSL',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    tests_require = TESTING_TOOLS,
    extras_require = {
        'dev': TESTING_TOOLS,
    },
    test_suite = 'nose.collector',
)
