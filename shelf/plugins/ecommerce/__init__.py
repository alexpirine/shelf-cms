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

class CarrierView(SQLAModelView):
    pass

class CountryView(SQLAModelView):
    pass

class DeliveryZoneView(SQLAModelView):
    pass

class ShippingOptionView(SQLAModelView):
    pass

class ShippingInfoView(SQLAModelView):
    pass

class OrderView(SQLAModelView):
    pass

class OrderedItemView(SQLAModelView):
    pass

class CategoryTypeView(SQLAModelView):
    pass

class CategoryView(SQLAModelView):
    pass

class ProductTypeView(SQLAModelView):
    pass

class VariationTypeView(SQLAModelView):
    pass

class VariationView(SQLAModelView):
    pass

class ProductView(SQLAModelView):
    pass

class ProductVariationView(SQLAModelView):
    pass

class ProductPictureView(SQLAModelView):
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
        app.register_blueprint(self.bp, url_prefix='/ecommerce')

        app.shelf.admin.add_view(ClientModelView(get_model('Client'), db.session, name="Clients", category="e-Commerce"))
        app.shelf.admin.add_view(AddressModelView(get_model('Address'), db.session, name="Addresses", category="e-Commerce"))
        app.shelf.admin.add_view(CarrierView(get_model('Carrier'), db.session, name="Carriers", category="e-Commerce"))
        app.shelf.admin.add_view(CountryView(get_model('Country'), db.session, name="Countries", category="e-Commerce"))
        app.shelf.admin.add_view(DeliveryZoneView(get_model('DeliveryZone'), db.session, name="DeliveryZones", category="e-Commerce"))
        app.shelf.admin.add_view(ShippingOptionView(get_model('ShippingOption'), db.session, name="ShippingOptions", category="e-Commerce"))
        app.shelf.admin.add_view(ShippingInfoView(get_model('ShippingInfo'), db.session, name="ShippingInfos", category="e-Commerce"))
        app.shelf.admin.add_view(OrderView(get_model('Order'), db.session, name="Orders", endpoint="orders", category="e-Commerce"))
        app.shelf.admin.add_view(OrderedItemView(get_model('OrderedItem'), db.session, name="OrderedItems", category="e-Commerce"))
        app.shelf.admin.add_view(CategoryTypeView(get_model('CategoryType'), db.session, name="CategoryTypes", category="e-Commerce"))
        app.shelf.admin.add_view(CategoryView(get_model('Category'), db.session, name="Categories", category="e-Commerce"))
        app.shelf.admin.add_view(ProductTypeView(get_model('ProductType'), db.session, name="ProductTypes", category="e-Commerce"))
        app.shelf.admin.add_view(VariationTypeView(get_model('VariationType'), db.session, name="VariationTypes", category="e-Commerce"))
        app.shelf.admin.add_view(VariationView(get_model('Variation'), db.session, name="Variations", category="e-Commerce"))
        app.shelf.admin.add_view(ProductView(get_model('Product'), db.session, name="Products", endpoint="products", category="e-Commerce"))
        app.shelf.admin.add_view(ProductVariationView(get_model('ProductVariation'), db.session, name="ProductVariations", category="e-Commerce"))
        app.shelf.admin.add_view(ProductPictureView(get_model('ProductPicture'), db.session, name="ProductPictures", category="e-Commerce"))
