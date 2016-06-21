# coding: utf-8

from flask import Blueprint
from flask_admin.base import expose
from flask_admin.model.form import InlineFormAdmin
from flask_babel import lazy_gettext as _
from shelf.admin.view import SQLAModelView
from shelf.base import db
from shelf.plugins.library import PicturePathField, LibraryViewMixin
from shelf.plugins.order import OrderViewMixin, PositionField

def init():
    from shelf.plugins.ecommerce import models

def get_model(model_name):
    from shelf.plugins.ecommerce import models

    return getattr(models, model_name)

def get_view(view_name):
    from shelf.plugins.ecommerce import views

    return getattr(views, view_name)


config = {
    "name": "Ecommerce",
    "description": "e-Commerce for Shelf",
}

class Ecommerce(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        from shelf.plugins.ecommerce import views

        self.bp = Blueprint('ecommerce', __name__, url_prefix='/ecommerce', template_folder='templates')
        app.register_blueprint(self.bp)

        for view_name in views.__all__:
            View = get_view(view_name)
            app.shelf.admin.add_view(View(View.get_default_model(), db.session, endpoint=view_name, name=View.name, category="e-Commerce"))
