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


class InlinePictureForm(InlineFormAdmin):
    def __init__(self, model, form_label=_(u"Pictures"), **kwargs):
        super(InlinePictureForm, self).__init__(model, **kwargs)
        self.form_label = form_label

    form_overrides = {
        "position": PositionField,
        "path": PicturePathField,
    }
    form_excluded_columns = ("width", "height",)
    form_args = {
        "position": {
            "choices": [(x, x) for x in range(50)],
            "coerce": int
        },
    }

    def on_model_change(self, form, model):
        print "saving inline picture:", form.path.raw_data, model.path

class ClientView(SQLAModelView):
    column_list = ('user', 'first_name', 'last_name', 'orders_nb', 'created_on')

    column_labels = {
        'user': _(u"E-mail"),
        'orders_nb': _(u"Orders"),
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

    list_template = 'client.list-actions.html'

    @expose('/detail/<int:id>')
    def detail(self, id):
        return self.render(
            'client.html',
            model=get_model('Client').query.get(id),
            admin_view=self,
            admin_base_template=self.admin.base_template,
        )

class AddressView(SQLAModelView):
    pass

class CarrierView(SQLAModelView):
    pass

class CountryView(SQLAModelView):
    column_list = ('code', 'name')
    form_columns = ('code', 'name')

class DeliveryZoneView(SQLAModelView):
    pass

class ShippingOptionView(SQLAModelView):
    pass

class ShippingInfoView(SQLAModelView):
    pass


class OrderView(SQLAModelView):
    can_delete = False
    can_edit = False
    column_list = ('id', "client", 'date', "step", "total")
    list_template = "order-list.html"

    column_formatters = {
        "total": lambda view, context, model, name: model.get_total_price(),
        "date": lambda view, context, model, name: model.date.strftime("%d/%m/%Y")
    }

    @expose("/detail/<int:id>")
    def detail(self, id):
        return self.render(
            "order.html",
            model=get_model('Order').query.get(id),
            admin_view=self,
            admin_base_template=self.admin.base_template,
        )

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

class ProductView(SQLAModelView, OrderViewMixin, LibraryViewMixin):
    column_list = ('active', 'code', 'name', 'price', 'qty')

    column_labels = {
        'active': _(u"Active"),
    }

    column_formatters = {
        'active': lambda v, c, m, p: not m.deleted,
    }


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
        from shelf.plugins.ecommerce import forms

        self.bp = Blueprint('ecommerce', __name__, url_prefix='/ecommerce', template_folder='templates')
        app.register_blueprint(self.bp)

        ProductView.inline_models = (
            InlinePictureForm(get_model('ProductPicture'), form_label="slides"),
        )

        app.shelf.admin.add_view(ClientView(get_model('Client'), db.session, name="Clients", category="e-Commerce"))
        # app.shelf.admin.add_view(AddressView(get_model('Address'), db.session, name="Addresses", category="e-Commerce"))
        # app.shelf.admin.add_view(CarrierView(get_model('Carrier'), db.session, name="Carriers", category="e-Commerce"))
        # app.shelf.admin.add_view(CountryView(get_model('Country'), db.session, name="Countries", category="e-Commerce"))
        # app.shelf.admin.add_view(DeliveryZoneView(get_model('DeliveryZone'), db.session, name="DeliveryZones", category="e-Commerce"))
        app.shelf.admin.add_view(ShippingOptionView(get_model('ShippingOption'), db.session, name="ShippingOptions", category="e-Commerce"))
        # app.shelf.admin.add_view(ShippingInfoView(get_model('ShippingInfo'), db.session, name="ShippingInfos", category="e-Commerce"))
        app.shelf.admin.add_view(OrderView(get_model('Order'), db.session, name="Orders", endpoint="client_order", category="e-Commerce"))
        # app.shelf.admin.add_view(OrderedItemView(get_model('OrderedItem'), db.session, name="OrderedItems", category="e-Commerce"))
        # app.shelf.admin.add_view(CategoryTypeView(get_model('CategoryType'), db.session, name="CategoryTypes", category="e-Commerce"))
        # app.shelf.admin.add_view(CategoryView(get_model('Category'), db.session, name="Categories", category="e-Commerce"))
        app.shelf.admin.add_view(ProductTypeView(get_model('ProductType'), db.session, name="ProductTypes", category="e-Commerce"))
        # app.shelf.admin.add_view(VariationTypeView(get_model('VariationType'), db.session, name="VariationTypes", category="e-Commerce"))
        # app.shelf.admin.add_view(VariationView(get_model('Variation'), db.session, name="Variations", category="e-Commerce"))
        app.shelf.admin.add_view(ProductView(get_model('Product'), db.session, name="Products", endpoint="products", category="e-Commerce"))
        # app.shelf.admin.add_view(ProductVariationView(get_model('ProductVariation'), db.session, name="ProductVariations", category="e-Commerce"))
        # app.shelf.admin.add_view(ProductPictureView(get_model('ProductPicture'), db.session, name="ProductPictures", category="e-Commerce"))
