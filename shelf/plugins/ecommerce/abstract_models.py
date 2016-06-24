# coding: utf-8

import sqlalchemy as sa
import sqlalchemy_utils as su

from decimal import Decimal
from datetime import datetime
from flask_babel import lazy_gettext as _
from flask_security import UserMixin, RoleMixin
from prices import Price
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship
from sqlalchemy_defaults import Column
from sqlalchemy.ext.orderinglist import ordering_list

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
    'PromoCode',
]

DEFAULT_CURRENCY = 'EUR'

class PrettyPrice(Price):
    def __add__(self, other):
        r = super(PrettyPrice, self).__add__(other)
        r.__class__ = self.__class__
        return r

    def __sub__(self, other):
        r = super(PrettyPrice, self).__sub__(other)
        r.__class__ = self.__class__
        return r

    def __mul__(self, other):
        r = super(PrettyPrice, self).__mul__(other)
        r.__class__ = self.__class__
        return r

    def __truediv__(self, other):
        r = super(PrettyPrice, self).__truediv__(other)
        r.__class__ = self.__class__
        return r

    def quantize(self, *args, **kwargs):
        r = super(PrettyPrice, self).quantize(*args, **kwargs)
        r.__class__ = self.__class__
        return r

    def __unicode__(self):
        return u" ".join(filter(None, (unicode(self.gross), self.currency)))

    def __str__(self):
        return unicode(self).encode('utf-8')

class PriceDecimal(sa.types.TypeDecorator):
    impl = sa.types.Numeric

    def process_bind_param(self, value, dialect):
        if value is None:
            return 0

        if type(value) is int:
            return value

        return value.gross

    def process_result_value(self, value, dialect):
        try:
            return PrettyPrice(value / Decimal(1.2), gross=value, currency=DEFAULT_CURRENCY)
        except TypeError:
            return PrettyPrice(0, currency=DEFAULT_CURRENCY)


class Client(LazyConfigured):
    __tablename__ = 'client'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    created_on = Column(sa.DateTime, nullable=False, auto_now=True, default=datetime.utcnow(), label=_(u"registration date"))
    first_name = Column(sa.Unicode(255), label=_(u"first name"))
    last_name = Column(sa.Unicode(255), label=_(u"last name"))
    tel = Column(sa.Unicode(20), nullable=True, label=_(u"telephone number"))

    @declared_attr
    def user(cls):
        return relationship('User', backref=backref('client', uselist=False), info={'label': _(u"user")})

    @declared_attr
    def user_id(cls):
        return Column(sa.Integer, sa.ForeignKey('user.id'), unique=True, nullable=False)

    def __unicode__(self):
        return u"%s %s" % (self.first_name, self.last_name)

    @property
    def orders_nb(self):
        return len(self.orders)

    @property
    def total_payed(self):
        prices = [order.get_total_price() for order in self.orders]
        if prices:
            return reduce(lambda x,y: x + y, prices)
        else:
            return PrettyPrice(0, currency=DEFAULT_CURRENCY)

class Address(LazyConfigured):
    __tablename__ = 'address'
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
        return relationship('Client', backref='addresses')

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)

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
    def lines(self):
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

        return filter(None, address)

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
    __tablename__ = 'carrier'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(63), unique=True, label=_(u"name"))
    api = Column(sa.String(63), nullable=True, label=_(u"API"))

    def __unicode__(self):
        return self.name

class Country(LazyConfigured):
    __tablename__ = 'country'
    __abstract__ = True

    code = Column(sa.String(2), primary_key=True, label=_(u"code"))
    name = Column(sa.Unicode(63), unique=True, label=_(u"name"))

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)

class DeliveryZone(LazyConfigured):
    __tablename__ = 'delivery_zone'
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('carrier_id', 'name'),
    )
    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(63), label=_(u"name"))

    @declared_attr
    def carrier(cls):
        return relationship('Carrier', backref='delivery_zones', info={'label': _(u"carrier")})

    @declared_attr
    def carrier_id(cls):
        return Column(sa.Integer, sa.ForeignKey('carrier.id'), nullable=False)

    @declared_attr
    def countries(cls):
        return relationship(
            'Country',
            secondary=db.Table(
                'delivery_zone_countries',
                Column('delivery_zone_id', sa.Integer, sa.ForeignKey('delivery_zone.id'), nullable=False),
                Column('country_code', sa.String(2), sa.ForeignKey('country.code'), nullable=False),
                sa.UniqueConstraint('delivery_zone_id', 'country_code'),
                extend_existing=True,
            ),
            backref='delivery_zones',
            info={'label': _(u"countries")},
        )

    def __unicode__(self):
        return self.name

class ShippingOption(LazyConfigured):
    __tablename__ = 'shipping_option'
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
        return relationship('DeliveryZone', backref='shipping_options', info={'label': _(u"delivery_zone")})

    @declared_attr
    def delivery_zone_id(cls):
        return Column(sa.Integer, sa.ForeignKey('delivery_zone.id'), nullable=False)

    def __unicode__(self):
        return self.name


class ShippingInfo(LazyConfigured):
    __tablename__ = 'shipping_info'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    tel = Column(sa.Unicode(20), nullable=True, label=_(u"telephone number"))
    instructions = Column(sa.Unicode(255), nullable=True, label=_(u"delivery instructions"))

    @declared_attr
    def address(cls):
        return relationship('Address', backref='shipping_infos', info={'label': _(u"address")})

    @declared_attr
    def address_id(cls):
        return Column(sa.Integer, sa.ForeignKey('address.id'), nullable=False)

    def __unicode__(self):
        if self.order:
            return u"Shipping info for Order No.%d" % self.order.id
        else:
            return u"Shipping info #%d" % self.id


class Order(LazyConfigured):
    __tablename__ = 'order'
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
    date = Column(sa.DateTime, auto_now=True, default=datetime.utcnow(), label=_(u"date"))
    tracknb = Column(sa.String(30), nullable=True, label=_(u"tracking number"))
    shipping_fee = Column(PriceDecimal(11, 2), label=_(u"shipping fee"))
    discount = Column(PriceDecimal(11, 2), label=_(u"discount"))
    step = Column(su.ChoiceType(STEPS_CHOICES, impl=sa.Integer()), default=STEPS['created'], label=_(u"step"))
    error = Column(su.ChoiceType(ERRORS, impl=sa.String(63)), nullable=True, label=_(u"error"))
    closed = Column(sa.Boolean, default=False, index=True, label=_(u"closed"))

    @declared_attr
    def client(cls):
        return relationship('Client', backref='orders', info={'label': _(u"client")})

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, sa.ForeignKey('client.id'), nullable=False)

    @declared_attr
    def shipping_option(cls):
        return relationship('ShippingOption', backref='orders', info={'label': _(u"shipping option")})

    @declared_attr
    def shipping_option_id(cls):
        return Column(sa.Integer, sa.ForeignKey('shipping_option.id'), nullable=False)

    @declared_attr
    def shipping_info(cls):
        return relationship('ShippingInfo', backref=backref('order', uselist=False), info={'label': _(u"shipping info")})

    @declared_attr
    def shipping_info_id(cls):
        return Column(sa.Integer, sa.ForeignKey('shipping_info.id'), unique=True, nullable=False)

    @declared_attr
    def billing_address(cls):
        return relationship('Address', backref='billed_orders', info={'label': _(u"billing address")})

    @declared_attr
    def billing_address_id(cls):
        return Column(sa.Integer, sa.ForeignKey('address.id'), nullable=False)

    def __unicode__(self):
        return u"Order No.%d for %s" % (self.id, self.client)

    def get_total_price(self, with_shipping=True):
        prices = [item.get_total_price() for item in self.items]
        if with_shipping and self.shipping_option:
            prices.append(self.shipping_option.price)
        if prices:
            return reduce(lambda x, y: x + y, prices)
        else:
            return PrettyPrice(0, currency=DEFAULT_CURRENCY)

    def check_no_errors(self):
        if self.error:
            raise Exception(_(u"This order has an unsolved issue."))

    def check_not_closed(self):
        if self.closed:
            raise Exception(_(u"This order is archived."))

    def can_accept(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step.code >= self.STEPS['accepted']:
            raise Exception(_(u"This order has already been accepted"))

    def accept(self):
        self.can_accept()
        self.step = self.STEPS['accepted']

    def can_process(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step.code < self.STEPS['accepted']:
            raise Exception(_(u"This order has not been accepted yet."))

        if self.step.code >= self.STEPS['processed']:
            raise Exception(_(u"This order has already been processed"))

    def process(self):
        self.can_process()
        self.step = self.STEPS['processed']

    def can_send(self):
        self.check_not_closed()
        self.check_no_errors()

        if self.step.code < self.STEPS['processed']:
            raise Exception(_(u"This order has not been processed yet."))

        if self.step.code >= self.STEPS['sent']:
            raise Exception(_(u"This order has already been sent"))

    def send(self):
        self.can_send()
        self.step = self.STEPS['sent']

    def can_cancel(self):
        self.check_not_closed()

        if self.error == 'cancelled':
            raise Exception(_(u"This order is already cancelled."))

        if self.step.code >= self.STEPS['sent']:
            raise Exception(_(u"This order has already been sent."))

    def cancel(self):
        self.can_cancel()

        self.error = 'cancelled'
        self.closed = True

    def add_item(self, product, quantity):
        self.items.append(get_model('Item')(
            product=product,
            qty=quantity
        ))

    def __call__(self, value):
        if value[:4] != 'can_':
            raise NotImplementedError

        try:
            return getattr(self, value)()
        except Exception:
            return False

class OrderedItem(LazyConfigured):
    __tablename__ = 'ordered_item'
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('order_id', 'product_id'),
    )

    id = Column(sa.Integer, primary_key=True)
    qty = Column(sa.SmallInteger, min=1, nullable=False, label=_(u"quantity"))
    price = Column(PriceDecimal(11, 2), min=0, nullable=False, label=_(u"unit price"))

    @declared_attr
    def order(cls):
        return relationship('Order', backref='items', info={'label': _(u"order")})

    @declared_attr
    def order_id(cls):
        return Column(sa.Integer, sa.ForeignKey('order.id'), nullable=False)

    @declared_attr
    def product(cls):
        return relationship('Product', backref='items', info={'label': _(u"product")})

    @declared_attr
    def product_id(cls):
        return Column(sa.Integer, sa.ForeignKey('product.id'), nullable=False)

    def __unicode__(self):
        return u"Ordered product %s for order No.%d" % (self.product.code, self.order.id)

    def get_total_price(self):
        return self.qty * self.price


class CategoryType(LazyConfigured):
    __tablename__ = 'category_type'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class Category(LazyConfigured):
    __tablename__ = 'category'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), label=_(u"name"))

    @declared_attr
    def category_type(cls):
        return relationship('CategoryType', backref='categories', info={'label': _(u"category type")})

    @declared_attr
    def category_type_id(cls):
        return Column(sa.Integer, sa.ForeignKey('category_type.id'), nullable=False)

    @declared_attr
    def parent_category(cls):
        return relationship('Category', backref='children', remote_side=[cls.id], info={'label': _(u"parent category")})

    @declared_attr
    def parent_category_id(cls):
        return Column(sa.Integer, sa.ForeignKey('category.id'), nullable=True)

    def __unicode__(self):
        return self.name

class ProductType(LazyConfigured):
    __tablename__ = 'product_type'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class VariationType(LazyConfigured):
    __tablename__ = 'variation_type'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), unique=True, label=_(u"name"))

    def __unicode__(self):
        return self.name

class Variation(LazyConfigured):
    __tablename__ = 'variation'
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('variation_type_id', 'value'),
    )

    id = Column(sa.Integer, primary_key=True)
    value = Column(sa.Unicode(255), label=_(u"value"))

    @declared_attr
    def variation_type(cls):
        return relationship('VariationType', backref='variations', info={'label': _(u"variation type")})

    @declared_attr
    def variation_type_id(cls):
        return Column(sa.Integer, sa.ForeignKey('variation_type.id'), nullable=False)

    def __unicode__(self):
        return self.value

class Product(LazyConfigured):
    __tablename__ = 'product'
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
        return relationship('ProductType', backref='products', info={'label': _(u"product type")})

    @declared_attr
    def product_type_id(cls):
        return Column(sa.Integer, sa.ForeignKey('product_type.id'), nullable=False)

    @declared_attr
    def categories(cls):
        return relationship(
            'Category',
            secondary=db.Table(
                'product_categories',
                Column('product_id', sa.Integer, sa.ForeignKey('product.id'), nullable=False),
                Column('category_id', sa.Integer, sa.ForeignKey('category.id'), nullable=False),
                sa.UniqueConstraint('product_id', 'category_id'),
                extend_existing=True,
            ),
            backref='products',
            info={'label': _(u"categories")}
        )

    @declared_attr
    def variations(cls):
        return relationship(
            'Variation',
            secondary=db.Table(
                'product_variations',
                Column('product_id', sa.Integer, sa.ForeignKey('product.id'), nullable=False),
                Column('variation_id', sa.Integer, sa.ForeignKey('variation.id'), nullable=False),
                sa.UniqueConstraint('product_id', 'variation_id'),
                extend_existing=True,
            ),
            backref='products',
            info={'label': _(u"variations")}
        )

    @declared_attr
    def variation_of(cls):
        return relationship('ProductVariation', backref='children', foreign_keys='Product.variation_of_id', info={'label': _(u"variation of…")})

    @declared_attr
    def variation_of_id(cls):
        return Column(sa.Integer, sa.ForeignKey('product_variation.id'), nullable=True)

    def __unicode__(self):
        return self.name

class ProductVariation(LazyConfigured):
    __tablename__ = 'product_variation'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def parent(cls):
        return relationship('Product', backref=backref('variation', uselist=False), foreign_keys='ProductVariation.parent_id', info={'label': _(u"parent product")})

    @declared_attr
    def parent_id(cls):
        return Column(sa.Integer, sa.ForeignKey('product.id'), unique=True, nullable=False)

    @declared_attr
    def variation_types(cls):
        return relationship(
            'VariationType',
            secondary=db.Table(
                'product_variation_types',
                Column('product_variation_id', sa.Integer, sa.ForeignKey('product_variation.id'), nullable=False),
                Column('variation_type_id', sa.Integer, sa.ForeignKey('variation_type.id'), nullable=False),
                sa.UniqueConstraint('product_variation_id', 'variation_type_id'),
                extend_existing=True,
            ),
            backref='product_variation',
            info={'label': _(u"variation types")},
        )

    def __unicode__(self):
        return self.parent

class ProductPicture(LazyConfigured, PictureModelMixin):
    __tablename__ = 'product_picture'
    __abstract__ = True
    __table_args__ = (
        sa.UniqueConstraint('id', 'product_id'),
    )

    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.Unicode(255), label=_(u"title"))
    position = Column(sa.SmallInteger, min=0, default=0, label=_(u"position"))

    @declared_attr
    def product(cls):
        return relationship('Product', backref='pictures', info={'label': _(u"product")})

    @declared_attr
    def product_id(cls):
        return Column(sa.Integer, sa.ForeignKey('product.id'), nullable=False)

    def __unicode__(self):
        return self.parent

    def get_inline_title(self):
            return ""

    def get_inline_thumbnail(self):
        try:
            return self.get_url()
        except:
            return None

class PromoCode(LazyConfigured):
    __tablename__ = 'promo_code'
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)
    code = Column(sa.Unicode(255), unique=True, label=_(u"code"))
    description = Column(sa.Unicode(255), label=_(u"description"))
    min_amount = Column(PriceDecimal(11, 2), default=0, label=_(u"minimum amount"))
    discount_fixed = Column(PriceDecimal(11, 2), default=0, label=_(u"fixed discount"))
    discount_per100 = Column(sa.SmallInteger, min=0, default=0, label=_(u"discount percentage"))
    offer_shipping = Column(sa.Boolean, default=False, label=_(u"offer shipping"))
    unique = Column(sa.Boolean, default=False, label=_(u"for unique usage"))
    deleted = Column(sa.Boolean, default=False, label=_(u"deleted"))

    def __unicode__(self):
        return self.code

    def apply(self, amount, invalidate=False):
        if self.deleted:
            raise Exception(_(u"This promo code is no longer active."))

        if self.min_amount > amount:
            raise Exception(_(u"This promo code can only by used if you purchase for more than %s.") % unicode(self.min_amount))

        if self.unique and invalidate:
            self.deleted = True

        discount = PrettyPrice(0, currency=amount.currency)
        discount += self.discount_fixed
        discount += amount * self.discount_per100 / 100
        discount = min(amount, discount)

        return {
            'discount': discount,
            'offer_shipping': self.offer_shipping,
        }
