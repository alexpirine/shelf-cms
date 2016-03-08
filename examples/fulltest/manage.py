#!/usr/bin/env python
# coding: utf-8

from flask import current_app
from flask.ext.script import Manager
from flask_security.utils import encrypt_password
from shelf import manager as shelf_manager
from shelf.base import db
from shelf.security.models import User, Role

from app import create_app

manager = Manager(create_app)
manager.add_command('shelf', shelf_manager)

@manager.command
def create_admin():
    user_datastore = current_app.extensions['security'].datastore

    admin = User.query.join(User.roles).filter(Role.name == 'superadmin').first()
    if not admin:
        admin_email = 'admin@localhost'
        admin_pwd = 'admin31!'
        admin = User(
            email=admin_email,
            active=True,
        )
        for role_name in ['superadmin', 'reviewer', 'publisher']:
            role = user_datastore.find_role(role_name)
            user_datastore.add_role_to_user(admin, role)
        admin.password = encrypt_password(admin_pwd)
        db.session.add(admin)
        db.session.commit()

        print("Admin user %(email)s (password: %(pwd)s) created successfully." % {
            'email': admin.email,
            'pwd': admin_pwd,
        })
    else:
        print("Admin user %(email)s already exists!" % {
            'email': admin.email,
        })

if __name__ == '__main__':
    manager.run()
