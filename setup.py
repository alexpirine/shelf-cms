from setuptools import setup, find_packages

setup(
    name='ShelfCMS',
    version='0.9.1',
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
        'flask==0.10.1',
        'flask_login==0.2.11',
        'flask-admin==1.0.8',
        'flask-wtf==0.9.5',
        'flask-security==1.7.3',
        'flask-sqlalchemy',
        'wtforms==1.0.5',
        'py-bcrypt'
    ]
)
