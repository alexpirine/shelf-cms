from flask import Blueprint
from shelf.admin.view import SQLAModelView
from shelf.base import db
from shelf.plugins.ecommerce import models

class ClientModelView(SQLAModelView):
    column_list = ('first_name', 'last_name', 'created_on')

    form_columns = (
        'first_name',
        "last_name",
        'created_on',
    )

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

        app.shelf.admin.add_view(ClientModelView(models.Client, db.session, name="Clients", category="e-Commerce"))
        app.shelf.admin.add_view(AddressModelView(models.Address, db.session, name="Addresses", category="e-Commerce"))
