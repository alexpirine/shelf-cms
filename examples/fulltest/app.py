#! /usr/bin/python
# -*- coding:utf-8 -*-
import os

from flask import Flask
from flask.ext.babel import Babel
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from shelf import Shelf
from shelf.plugins.dashboard import DashboardView
from shelf.plugins.page import Page as PagePlugin

from models import db, User, Role
from models import IndexPage, ContactPage
from view import init_views
from admin import init_admin, IndexPageModelView, ContactPageModelView

app = Flask(__name__)

app.debug = True
app.testing = False

app.config.from_object('config')

app.config['SHELF_PAGES'] = {
    "index": (IndexPage, IndexPageModelView),
    "contact": (ContactPage, ContactPageModelView)
}


with app.app_context():
    db.init_app(app)
    db.create_all()

    babel = Babel(app)

    shlf = Shelf(app)
    shlf.init_db(db)

    dview = DashboardView()
    shlf.init_admin(index_view=dview)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    shlf.init_security(User, Role)

    shlf.load_plugins((
        "shelf.plugins.wysiwyg",
        "shelf.plugins.workflow",
        "shelf.plugins.i18n",
        "shelf.plugins.library",
        "shelf.plugins.preview",
        "shelf.plugins.page",
        "shelf.plugins.dashboard"
    ))
    init_admin(shlf.admin, db.session)
    shlf.setup_plugins()

    page = shlf.get_plugin_by_class(PagePlugin)
    page.register_pages(app, shlf.db)

    init_views(app)

    @app.before_first_request
    def create_admin():
        admin = User.query.join(User.roles).filter(Role.name == "superadmin").first()
        if not admin:
            admin = User(
                firstname="Admin", lastname="Shelf",
                email="admin@localhost")
            for role_name in ["superadmin", "reviewer", "publisher"]:
                role = user_datastore.find_role(role_name)
                user_datastore.add_role_to_user(admin, role)
            admin.password = encrypt_password("admin31!")
            db.session.add(admin)
            db.session.commit()

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000)
