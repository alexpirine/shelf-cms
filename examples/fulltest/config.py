# coding: utf-8

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
MEDIA_ROOT = os.path.join(APP_STATIC, 'media')
MEDIA_URL = '/static/media/'

try:
    os.makedirs(MEDIA_ROOT)
except OSError:
    pass

SECRET_KEY = 'batbelitiscommerce1234'
BABEL_DEFAULT_LOCALE = 'fr'
SHELF_I18N_LANGS = ("fr", "en")
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = "hash_123678*"
SQLALCHEMY_DATABASE_URI = 'sqlite:///demo.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = True