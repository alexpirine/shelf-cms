#!/usr/bin/env python
# coding: utf-8

import os

from flask import Flask

from shelf import Shelf
from shelf.base import db
from shelf.plugins.library import FileAdmin
from shelf.security.models import User, Role

import admin
import model

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'notasecret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = 'mysalt'#"hash_123678*",
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

app.config['APP_ROOT'] = os.path.dirname(os.path.abspath(__file__))
app.config['APP_STATIC'] = os.path.join(app.config['APP_ROOT'], 'static')
app.config['MEDIA_ROOT'] = os.path.join(app.config['APP_STATIC'], 'media')
app.config['MEDIA_URL'] = '/static/media/'

try:
    os.makedirs(app.config['MEDIA_ROOT'])
except OSError:
    pass

with app.app_context():
    db.init_app(app)
    db.app = app

    shlf = Shelf(app)
    shlf.init_db(db)
    shlf.init_admin()
    shlf.init_security(User, Role)
    shlf.load_plugins((
        "shelf.plugins.wysiwyg",
        "shelf.plugins.workflow",
        "shelf.plugins.library"
    ))
    shlf.admin.add_view(admin.PostModelView(model.Post, db.session))
    shlf.admin.add_view(FileAdmin(name="Media"))
    shlf.setup_plugins()
    app.run('0.0.0.0')
