# coding: utf-8

from flask_babel import lazy_gettext as _
from flask_security import UserMixin, RoleMixin
from flask_security.utils import encrypt_password
from flask_security.utils import verify_and_update_password
from sqlalchemy_defaults import Column

from ..base import LazyConfigured
from ..base import db

roles_users = db.Table('roles_users',
    Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(LazyConfigured, RoleMixin):
    id = Column(db.Integer(), primary_key=True)
    name = Column(db.Unicode(80), unique=True, label=_(u"name"))
    description = Column(db.Unicode(255), label=_(u"description"))

    def __unicode__(self):
        return self.name

class User(LazyConfigured, UserMixin):
    id = Column(db.Integer, primary_key=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    email = Column(db.String(255), unique=True, label=_(u"e-mail"))
    password = Column(db.String(255), nullable=True, label=_(u"password"))
    active = Column(db.Boolean(), default=False, label=_(u"active"))

    def __unicode__(self):
        return self.email

    def set_password(self, new_password):
        self.password = encrypt_password(new_password)
        return self

    def check_password(self, password):
        return verify_and_update_password(password, self)
