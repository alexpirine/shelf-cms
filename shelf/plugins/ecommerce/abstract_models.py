# coding: utf-8

import sqlalchemy as sa
import sqlalchemy_utils as su

from decimal import Decimal
from flask.ext.babel import lazy_gettext as _
from flask.ext.security import UserMixin, RoleMixin
from prices import Price
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy_defaults import Column

from shelf import LazyConfigured
from shelf.base import db
from shelf.plugins.library import PictureModelMixin
from shelf.plugins.ecommerce import get_model

__all__ = [
    'Client',
    'Address',
    'Carrier',
    'Country',
    'DeliveryZone',
    'ShippingOption',
    'ShippingInfo',
    'Order',
    'OrderedItem',
    'CategoryType',
    'Category',
    'ProductType',
    'VariationType',
    'Variation',
    'Product',
    'ProductVariation',
    'ProductPicture',
]

class PriceDecimal(sa.types.TypeDecorator):
    impl = sa.types.NUMERIC

    def process_bind_param(self, value, dialect):
        if value is None:
            return 0
        return value.gross

    def process_result_value(self, value, dialect):
        try:
            return Price(value / Decimal(1.2), gross=value, currency="EUR").quantize('0.01')
        except TypeError:
            return Price(0)


class Client(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    created_on = Column(sa.DateTime, auto_now=True, label=_(u"registration date"))
    first_name = Column(sa.Unicode(255), label=_(u"first name"))
    last_name = Column(sa.Unicode(255), label=_(u"last name"))
    tel = Column(sa.Unicode(20), nullable=True, label=_(u"telephone number"))

    @declared_attr
    def user(cls):
        return db.relationship('User', backref=backref('client', uselist=False), info={'label': _(u"user")})

    @declared_attr
    def user_id(cls):
        return Column(sa.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)


class Address(LazyConfigured):
    __abstract__ = True

    """
    Norme AFNOR XPZ 10-011 :
    on utilise 4 lignes en champ libre, suivis d'une ligne pour le code postal,
    le CEDEX et la ville, et une dernière ligne pour le pays de destination.
    Une ligne ne peut dépasser 38 caractères. Les abbréviations ne sont
    autorisées que lorsque la ligne dépasse 32 caractères. La police utilisée
    doit être Lucida Console. Les signes de pontuation ne doivent pas être
    utilisés dans la description de la localité. Les deux dernières lignes
    doivent être écrites en majuscules, sans accents ni ponctuation.
    Le pays sera toujours la dernière ligne de l'adresse, mais le
    positionnement des autres éléments dépendera du pays de destination. Par
    exemple, le code postal sera imprimé après le nom de la localité pour les
    envois au Canada.
    """
    id = Column(sa.Integer, primary_key=True)
    line1 = Column(sa.Unicode(38), label=_(u"line 1"))
    line2 = Column(sa.Unicode(38), nullable=True, label=_(u"line 2"))
    line3 = Column(sa.Unicode(38), nullable=True, label=_(u"line 3"))
    line4 = Column(sa.Unicode(38), nullable=True, label=_(u"line 4"))
    city = Column(sa.Unicode(38), label=_(u"city"))
    zip_code = Column(sa.Unicode(20), label=_(u"zip code"))
    country = Column(sa.Unicode(38), label=_(u"country"))
    deleted = Column(sa.Boolean, default=False, index=True, label=_(u"deleted"))

    @declared_attr
    def client(cls):
        return db.relationship('Client', backref='addresses')

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, db.ForeignKey('client.id'), nullable=False)

    def __unicode__(self):
        # ligne 5 : localité et code postal
        line5 = []
        if self.zip_code:
            line5.append(self.zip_code)
        if self.city:
            line5.append(self.city)
        line5 = u' '.join(line5)

        # ligne 6 : pays destinataire
        line6 = self.country

        # adresse complète
        address = []
        if self.line1:
            address.append(self.line1)
        if self.line2:
            address.append(self.line2)
        if self.line3:
            address.append(self.line3)
        if self.line4:
            address.append(self.line4)
        if line5:
            address.append(line5)
        if line6:
            address.append(line6)

        address1 = u'\n'.join(address[:-3])
        address2 = u'\n'.join(address[-3:]).upper()

        return u'\n'.join(filter(None, [address1, address2]))

    @property
    def short(self):
        return u"%s %s %s" % (self.line1, self.zip_code, self.city)

    def set_lines(self, lines):
        lines = [l.strip() for l in lines.strip().split('\n')]
        self.line1 = lines[0] if len(lines) > 0 else ''
        self.line2 = lines[1] if len(lines) > 1 else ''
        self.line3 = lines[2] if len(lines) > 2 else ''
        self.line4 = lines[3] if len(lines) > 3 else ''

class Carrier(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(63), unique=True, label=_(u"name"))
    api = Column(sa.String(63), nullable=True, label=_(u"API"))

    def __unicode__(self):
        return self.name

class Country(LazyConfigured):
    __abstract__ = True

    code = Column(sa.String(2), primary_key=True, label=_(u"code"))
    name = Column(sa.Unicode(63), unique=True, label=_(u"name"))

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)

class DeliveryZone(LazyConfigured):
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('carrier_id', 'name'),
    )

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(63), label=_(u"name"))

    @declared_attr
    def carrier(cls):
        return db.relationship('Carrier', backref='delivery_zones', info={'label': _(u"carrier")})

    @declared_attr
    def carrier_id(cls):
        return Column(sa.Integer, db.ForeignKey('carrier.id'), nullable=False)

    @declared_attr
    def countries(cls):
        return db.relationship(
            'Country',
            secondary=db.Table(
                'delivery_zone_countries',
                Column('delivery_zone_id', db.Integer, db.ForeignKey('delivery_zone.id'), nullable=False),
                Column('country_code', db.String(2), db.ForeignKey('country.code'), nullable=False),
                sa.UniqueConstraint('delivery_zone_id', 'country_code'),
                extend_existing=True,
            ),
            backref='delivery_zones',
            info={'label': _(u"countries")},
        )

    def __unicode__(self):
        return self.name

class ShippingOption(LazyConfigured):
    __abstract__ = True

    PACKAGING_FORMATS = (
        ('E', _(u"enveloppes")),
        ('B', _(u"boxes")),
        ('A', _(u"all")),
    )

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(63), label=_(u"name"))
    price = Column(PriceDecimal(11, 2), label=_(u"price"))
    delivery_time = Column(sa.SmallInteger, min=0, max=1440, label=_(u"delivery time"))
    packaging_format = Column(su.ChoiceType(PACKAGING_FORMATS, impl=sa.String(1)))
    max_weight = Column(sa.SmallInteger, default=0, min=0, label=_(u"max weight"))
    max_x = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    max_y = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    max_z = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    deleted = Column(sa.Boolean, default=False, index=True, label=_(u"deleted"))

    @declared_attr
    def delivery_zone(cls):
        return db.relationship('DeliveryZone', backref='shipping_options', info={'label': _(u"delivery_zone")})

    @declared_attr
    def delivery_zone_id(cls):
        return Column(sa.Integer, db.ForeignKey('delivery_zone.id'), nullable=False)

    def __unicode__(self):
        return self.name


class ShippingInfo(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    tel = Column(sa.Unicode(20), nullable=True, label=_(u"telephone number"))
    instructions = Column(sa.Unicode(255), nullable=True, label=_(u"delivery instructions"))

    @declared_attr
    def address(cls):
        return db.relationship('Address', backref='shipping_infos', info={'label': _(u"address")})

    @declared_attr
    def address_id(cls):
        return Column(sa.Integer, db.ForeignKey('address.id'), nullable=False)

    def __unicode__(self):
        return u"Shipping info for Order No.%d" % self.order_id


class Order(LazyConfigured):
    __abstract__ = True

    STEPS = {
        'created': 10,
        'accepted': 20,
        'processed': 30,
        'sent': 40,
        'delivered': 50,
    }

    STEPS_CHOICES = [(v, _(k.decode('utf-8'))) for k, v in STEPS.items()]

    ERRORS = (
        ('cancelled', _(u"cancelled")),
        ('no_stock', _(u"no_stock")),
        ('picking', _(u"picking")),
        ('delivery', _(u"delivery")),
    )

    id = Column(sa.Integer, primary_key=True)
    date = Column(sa.DateTime, auto_now=True, label=_(u"date"))
    tracknb = Column(sa.String(30), nullable=True, label=_(u"tracking number"))
    shipping_fee = Column(PriceDecimal(11, 2), label=_(u"shipping fee"))
    discount = Column(PriceDecimal(11, 2), label=_(u"discount"))
    step = Column(su.ChoiceType(STEPS_CHOICES, impl=sa.Integer()), default=STEPS['created'], label=_(u"step"))
    error = Column(su.ChoiceType(ERRORS, impl=sa.String(63)), nullable=True, label=_(u"error"))
    closed = Column(sa.Boolean, default=False, index=True, label=_(u"closed"))

    @declared_attr
    def client(cls):
        return db.relationship('Client', backref='orders', info={'label': _(u"client")})

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, db.ForeignKey('client.id'), nullable=False)

    @declared_attr
    def shipping_option(cls):
        return db.relationship('ShippingOption', backref='orders', info={'label': _(u"shipping option")})

    @declared_attr
    def shipping_option_id(cls):
        return Column(sa.Integer, db.ForeignKey('shipping_option.id'), nullable=False)

    @declared_attr
    def shipping_info(cls):
        return db.relationship('ShippingInfo', backref=backref('order', uselist=False), info={'label': _(u"shipping info")})

    @declared_attr
    def shipping_info_id(cls):
        return Column(sa.Integer, db.ForeignKey('shipping_info.id'), unique=True, nullable=False)

    @declared_attr
    def billing_address(cls):
        return db.relationship('Address', backref='billed_orders', info={'label': _(u"billing address")})

    @declared_attr
    def billing_address_id(cls):
        return Column(sa.Integer, db.ForeignKey('address.id'), nullable=False)

    def __unicode__(self):
        return u"Order No.%d for %s" % (self.id, self.client)

    def get_total_price(self):
        return sum([item.get_total_price() for item in self.items])

    def check_no_errors(self):
        if self.error:
            raise Exception(_(u"This order has an unsolved issue."))

    def check_not_closed(self):
        if self.closed:
            raise Exception(_(u"This order is archived."))

    def can_accept(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step >= self.STEPS['accepted']:
            raise Exception(_(u"This order has already been accepted"))

    def accept(self):
        self.can_accept()
        self.step = self.STEPS['accepted']

    def can_process(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step < self.STEPS['accepted']:
            raise Exception(_(u"This order has not been accepted yet."))

        if self.step >= self.STEPS['processed']:
            raise Exception(_(u"This order has already been processed"))

    def process(self):
        self.can_process()
        self.step = self.STEPS['processed']

    def can_send(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step < self.STEPS['processed']:
            raise Exception(_(u"This order has not been processed yet."))

        if self.step >= self.STEPS['sent']:
            raise Exception(_(u"This order has already been sent"))

    def send(self):
        self.can_send()
        self.step = self.STEPS['sent']

    def can_cancel(self):
        self.check_not_closed()

        if self.error == 'cancelled':
            raise Exception(_(u"This order is already cancelled."))

        if self.step >= STEP['sent']:
            raise Exception(_(u"This order has already been sent."))

    def cancel(self):
        self.can_cancel()

        self.error = 'cancelled'
        self.closed = True

    def add_item(self, product, quantity):
        pass

class OrderedItem(LazyConfigured):
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('order_id', 'product_id'),
    )

    id = Column(sa.Integer, primary_key=True)
    qty = Column(sa.SmallInteger, min=1, nullable=False, label=_(u"quantity"))
    price = Column(PriceDecimal(11, 2), min=0, nullable=False, label=_(u"unit price"))

    @declared_attr
    def order(cls):
        return db.relationship('Order', backref='items', info={'label': _(u"order")})

    @declared_attr
    def order_id(cls):
        return Column(sa.Integer, db.ForeignKey('order.id'), nullable=False)

    @declared_attr
    def product(cls):
        return db.relationship('Product', backref='items', info={'label': _(u"product")})

    @declared_attr
    def product_id(cls):
        return Column(sa.Integer, db.ForeignKey('product.id'), nullable=False)

    def __unicode__(self):
        return u"Order No.%d for %s" % (self.id, self.client)

    def get_total_price(self):
        return self.qty * self.price


class CategoryType(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class Category(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), label=_(u"name"))

    @declared_attr
    def category_type(cls):
        return db.relationship('CategoryType', backref='categories', info={'label': _(u"category type")})

    @declared_attr
    def category_type_id(cls):
        return Column(sa.Integer, db.ForeignKey('category_type.id'), nullable=False)

    @declared_attr
    def parent_category(cls):
        return db.relationship('Category', backref='children', remote_side=[cls.id], info={'label': _(u"parent category")})

    @declared_attr
    def parent_category_id(cls):
        return Column(sa.Integer, db.ForeignKey('category.id'), nullable=True)

    def __unicode__(self):
        return self.name

class ProductType(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class VariationType(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class Variation(LazyConfigured):
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('variation_type_id', 'value'),
    )

    id = Column(sa.Integer, primary_key=True)
    value = Column(sa.Unicode(255), unique=True, label=_(u"value"))

    @declared_attr
    def variation_type(cls):
        return db.relationship('VariationType', backref='variations', info={'label': _(u"variation type")})

    @declared_attr
    def variation_type_id(cls):
        return Column(sa.Integer, db.ForeignKey('variation_type.id'), nullable=False)

    def __unicode__(self):
        return self.name

class Product(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    code = Column(sa.Unicode(63), unique=True, label=_(u"code"))
    ean13 = Column(sa.Numeric(13, 0), nullable=True, label=_(u"EAN-13 code"))
    name = Column(sa.Unicode(255), label=_(u"name"))
    price = Column(PriceDecimal(11, 2), min=0, label=_(u"price"))
    weight = Column(sa.Integer, min=0, default=0, label=_(u"weight"))
    dim_x = Column(sa.Integer, min=0, default=0, label=_(u"dim_x"))
    dim_y = Column(sa.Integer, min=0, default=0, label=_(u"dim_y"))
    dim_z = Column(sa.Integer, min=0, default=0, label=_(u"dim_z"))
    qty = Column(sa.Integer, min=0, default=0, label=_(u"quantity"))
    qty_reserved = Column(sa.Integer, min=0, default=0, label=_(u"reserved quantity"))
    deleted = Column(sa.Boolean, default=False, index=True, label=_(u"deleted"))

    @declared_attr
    def product_type(cls):
        return db.relationship('ProductType', backref='products', info={'label': _(u"product type")})

    @declared_attr
    def product_type_id(cls):
        return Column(sa.Integer, db.ForeignKey('product_type.id'), nullable=False)

    @declared_attr
    def categories(cls):
        return db.relationship(
            'Category',
            secondary=db.Table(
                'product_categories',
                Column('product_id', db.Integer, db.ForeignKey('product.id'), nullable=False),
                Column('category_id', db.Integer, db.ForeignKey('category.id'), nullable=False),
                sa.UniqueConstraint('product_id', 'category_id'),
                extend_existing=True,
            ),
            backref='products',
            info={'label': _(u"categories")}
        )

    @declared_attr
    def variation_of(cls):
        return db.relationship('ProductVariation', backref='children', foreign_keys='Product.variation_of_id', info={'label': _(u"variation of…")})

    @declared_attr
    def variation_of_id(cls):
        return Column(sa.Integer, db.ForeignKey('product_variation.id'), nullable=True)

    def __unicode__(self):
        return self.name

class ProductVariation(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def parent(cls):
        return db.relationship('Product', backref=backref('variation', uselist=False), foreign_keys='ProductVariation.parent_id', info={'label': _(u"parent product")})

    @declared_attr
    def parent_id(cls):
        return Column(sa.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)

    @declared_attr
    def variation_types(cls):
        return db.relationship(
            'VariationType',
            secondary=db.Table(
                'product_variation_types',
                Column('product_variation_id', db.Integer, db.ForeignKey('product_variation.id'), nullable=False),
                Column('variation_type_id', db.Integer, db.ForeignKey('variation_type.id'), nullable=False),
                sa.UniqueConstraint('product_variation_id', 'variation_type_id'),
                extend_existing=True,
            ),
            backref='product_variation',
            info={'label': _(u"variation types")},
        )

    def __unicode__(self):
        return self.parent

class ProductPicture(LazyConfigured, PictureModelMixin):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), label=_(u"name"))
    position = Column(sa.SmallInteger, min=0, default=0, label=_(u"position"))

    @declared_attr
    def product(cls):
        return db.relationship('Product', backref='pictures', info={'label': _(u"product")})

    @declared_attr
    def product_id(cls):
        return Column(sa.Integer, db.ForeignKey('product.id'), unique=True, nullable=False)

    def __unicode__(self):
        return self.parent
