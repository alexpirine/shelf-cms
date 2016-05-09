#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

DEV_TOOLS = [
    'codecov',
    'coverage',
    'imgurpython',
    'nose',
    'scripttest',
    'selenium',
]

if __name__ == '__main__':
    setup(
        name='ShelfCMS',
        version='0.12.18',
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
            'SQLAlchemy-Defaults',
            'SQLAlchemy-Utils',
            'WTForms',
            'WTForms-Alchemy',
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
        tests_require = DEV_TOOLS,
        extras_require = {
            'dev': DEV_TOOLS,
        },
        test_suite = 'nose.collector',
    )
