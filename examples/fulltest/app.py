#!/usr/bin/env python
# coding: utf-8

from flask import Flask
from flask.ext.babel import Babel

from shelf import Shelf
from shelf.base import db
from shelf.plugins.dashboard import DashboardView
from shelf.plugins.page import Page as PagePlugin
from shelf.security.models import User, Role

from admin import init_admin, IndexPageModelView, ContactPageModelView
from models import IndexPage, ContactPage
from view import init_views
from filters import init_filters

def create_app():
    app = Flask(__name__)

    app.debug = True
    app.testing = False

    import config
    app.config.from_object(config)

    app.config['SHELF_PAGES'] = {
        "index": (IndexPage, IndexPageModelView),
        "contact": (ContactPage, ContactPageModelView),
    }

    with app.app_context():
        db.init_app(app)
        db.create_all()

        babel = Babel(app)

        shlf = Shelf(app)
        shlf.init_db(db)

        dview = DashboardView()
        shlf.init_admin(index_view=dview)

        shlf.init_security(User, Role)

        shlf.load_plugins((
            "shelf.plugins.dashboard",
            "shelf.plugins.ecommerce",
            "shelf.plugins.i18n",
            "shelf.plugins.library",
            "shelf.plugins.page",
            "shelf.plugins.preview",
            "shelf.plugins.workflow",
            "shelf.plugins.wysiwyg",
        ))
        init_admin(shlf.admin, db.session)
        shlf.setup_plugins()

        page = shlf.get_plugin_by_class(PagePlugin)
        page.register_pages(app, shlf.db)

        init_views(app)
        init_filters(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run('0.0.0.0', port=5000)
