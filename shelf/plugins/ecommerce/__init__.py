# coding: utf-8

from flask import Blueprint
from flask.ext.babel import lazy_gettext as _
from shelf.admin.view import SQLAModelView
from shelf.base import db

def get_model(model_name):
    from shelf.plugins.ecommerce import models

    return getattr(models, model_name)

class ClientModelView(SQLAModelView):
    column_list = ('user', 'first_name', 'last_name', 'created_on')

    column_labels = {
        'user': _(u"E-mail"),
    }

    form_shortcuts = (
        'first_name',
        'last_name',
        'created_on',
    )

    form_export_fields = (
        'first_name',
        'last_name',
        'created_on',
    )

    form_widget_args = {
        'created_on': {
            'readonly': True,
        },
        'user': {
            'readonly': True,
        }
    }

class AddressModelView(SQLAModelView):
    pass

config = {
    "name": "Ecommerce",
    "description": "e-Commerce for Shelf",
}

class Ecommerce(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = Blueprint('ecommerce', __name__)
        app.register_blueprint(self.bp)

        app.shelf.admin.add_view(ClientModelView(get_model('Client'), db.session, name="Clients", category="e-Commerce"))
        app.shelf.admin.add_view(AddressModelView(get_model('Address'), db.session, name="Addresses", category="e-Commerce"))
