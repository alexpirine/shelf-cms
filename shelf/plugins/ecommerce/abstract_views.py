# coding: utf-8

from wtforms import fields
from flask_admin.base import expose
from flask_admin.model.form import InlineFormAdmin
from flask_babel import lazy_gettext as _
from shelf.admin.view import SQLAModelView
from shelf.base import db
from shelf.plugins.library import PicturePathField, LibraryViewMixin
from shelf.plugins.order import OrderViewMixin, PositionField
from shelf.plugins.ecommerce import get_model

__all__ = [
    'ClientView',
    'AddressView',
    'CarrierView',
    'CountryView',
    'DeliveryZoneView',
    'ShippingOptionView',
    'ShippingInfoView',
    'OrderView',
    'OrderedItemView',
    'CategoryTypeView',
    'CategoryView',
    'ProductTypeView',
    'VariationTypeView',
    'VariationView',
    'ProductView',
    'ProductVariationView',
    'ProductPictureView',
    'PromoCodeView',
]

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

class ClientView(SQLAModelView):
    name = _(u"Clients")

    @classmethod
    def get_default_model(cls):
        return get_model('Client')

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
    name = _(u"Addresses")

    @classmethod
    def get_default_model(cls):
        return get_model('Address')

class CarrierView(SQLAModelView):
    name = _(u"Carriers")

    @classmethod
    def get_default_model(cls):
        return get_model('Carrier')

class CountryView(SQLAModelView):
    name = _(u"Countries")

    @classmethod
    def get_default_model(cls):
        return get_model('Country')

    column_list = ('code', 'name')
    form_columns = ('code', 'name')

class DeliveryZoneView(SQLAModelView):
    name = _(u"Delivery zones")

    @classmethod
    def get_default_model(cls):
        return get_model('DeliveryZone')

class ShippingOptionView(SQLAModelView):
    name = _(u"Shipping options")

    @classmethod
    def get_default_model(cls):
        return get_model('ShippingOption')

    column_list = ('name', 'price', 'delivery_time', "deleted")

class ShippingInfoView(SQLAModelView):
    name = _(u"Shipping infos")

    @classmethod
    def get_default_model(cls):
        return get_model('ShippingInfo')


class OrderView(SQLAModelView):
    name = _(u"Orders")

    @classmethod
    def get_default_model(cls):
        return get_model('Order')

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
    name = _(u"Ordered items")

    @classmethod
    def get_default_model(cls):
        return get_model('OrderedItem')

class CategoryTypeView(SQLAModelView):
    name = _(u"Category types")

    @classmethod
    def get_default_model(cls):
        return get_model('CategoryType')

class CategoryView(SQLAModelView):
    name = _(u"Categories")

    @classmethod
    def get_default_model(cls):
        return get_model('Category')

class ProductTypeView(SQLAModelView):
    name = _(u"Product types")

    @classmethod
    def get_default_model(cls):
        return get_model('ProductType')

class VariationTypeView(SQLAModelView):
    name = _(u"Variation types")

    @classmethod
    def get_default_model(cls):
        return get_model('VariationType')

class VariationView(SQLAModelView):
    name = _(u"Variations")

    @classmethod
    def get_default_model(cls):
        return get_model('Variation')

class ProductView(SQLAModelView, OrderViewMixin, LibraryViewMixin):
    name = _(u"Products")

    @classmethod
    def get_default_model(cls):
        return get_model('Product')

    def __init__(self, *args, **kwargs):
        self.inline_models = (
            InlinePictureForm(get_model('ProductPicture'), form_label=_("Pictures")),
        )
        super(ProductView, self).__init__(*args, **kwargs)

    column_list = ('active', 'code', 'name', 'price', 'qty')

    column_labels = {
        'active': _(u"Active"),
    }

    column_formatters = {
        'active': lambda v, c, m, p: not m.deleted,
    }

    column_searchable_list = ("name", "code")


class ProductVariationView(SQLAModelView):
    name = _(u"Product variations")

    @classmethod
    def get_default_model(cls):
        return get_model('ProductVariation')

class ProductPictureView(SQLAModelView):
    name = _(u"Product pictures")

    @classmethod
    def get_default_model(cls):
        return get_model('ProductPicture')

class PromoCodeView(SQLAModelView):
    name = _(u"Promo codes")

    @classmethod
    def get_default_model(cls):
        return get_model('PromoCode')

    column_list = ('code', 'min_amount', 'discount_fixed', 'discount_per100', 'offer_shipping', 'unique')
