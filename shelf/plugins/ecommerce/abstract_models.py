# coding: utf-8

import sqlalchemy as sa
import sqlalchemy_utils as su

from flask.ext.babel import lazy_gettext as _
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy_defaults import Column

from shelf import LazyConfigured
from shelf.base import db

class Client(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def user(cls):
        return db.relationship('User', backref=backref('client', uselist=False), info={'label': _(u"user")})

    @declared_attr
    def user_id(cls):
        return Column(sa.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    created_on = Column(sa.DateTime, auto_now=True, label=_(u"registration date"))
    first_name = Column(sa.Unicode(255), label=_(u"first name"))
    last_name = Column(sa.Unicode(255), label=_(u"last name"))
    tel = Column(sa.Unicode(20), nullable=True, label=_(u"telephone number"))

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

    @declared_attr
    def client(cls):
        return db.relationship('Client', backref='addresses')

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, db.ForeignKey('client.id'))

    line1 = Column(sa.Unicode(38), label=_(u"line 1"))
    line2 = Column(sa.Unicode(38), nullable=True, label=_(u"line 2"))
    line3 = Column(sa.Unicode(38), nullable=True, label=_(u"line 3"))
    line4 = Column(sa.Unicode(38), nullable=True, label=_(u"line 4"))
    city = Column(sa.Unicode(38), label=_(u"city"))
    zip_code = Column(sa.Unicode(20), label=_(u"zip code"))
    country = Column(sa.Unicode(38), label=_(u"country"))

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

    def set_lines(self, lines):
        lines = [l.strip() for l in lines.strip().split('\n')]
        self.line1 = lines[0] if len(lines) > 0 else ''
        self.line2 = lines[1] if len(lines) > 1 else ''
        self.line3 = lines[2] if len(lines) > 2 else ''
        self.line4 = lines[3] if len(lines) > 3 else ''

    @property
    def short(self):
        return u"%s %s %s" % (self.line1, self.zip_code, self.city)

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
    name = Column(sa.Unicode(63), label=_(u"name"))

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code)

class DeliveryZone(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def carrier(cls):
        return db.relationship('Carrier', backref='delivery_zones', info={'label': _(u"carrier")})

    @declared_attr
    def carrier_id(cls):
        return Column(sa.Integer, db.ForeignKey('carrier.id'))

    @declared_attr
    def countries(cls):
        return db.relationship(
            'Country',
            secondary=db.Table(
                'delivery_zone_countries',
                Column('delivery_zone_id', db.Integer, db.ForeignKey('delivery_zone.id')),
                Column('country_code', db.String(2), db.ForeignKey('country.code')),
                extend_existing=True,
            ),
            backref='delivery_zones',
            info={'label': _(u"countries")},
        )

    name = Column(sa.Unicode(63), label=_(u"name"))

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

    @declared_attr
    def delivery_zone(cls):
        return db.relationship('DeliveryZone', backref='shipping_options', info={'label': _(u"delivery_zone")})

    @declared_attr
    def delivery_zone_id(cls):
        return Column(sa.Integer, db.ForeignKey('delivery_zone.id'))

    name = Column(sa.Unicode(63), label=_(u"name"))
    price = Column(sa.Numeric(11, 2), label=_(u"price"))
    delivery_time = Column(sa.SmallInteger, min=0, max=1440, label=_(u"delivery time"))
    packaging_format = Column(su.ChoiceType(PACKAGING_FORMATS, impl=sa.String(1)))
    max_weight = Column(sa.SmallInteger, default=0, min=0, label=_(u"max weight"))
    max_x = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    max_y = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    max_z = Column(sa.SmallInteger, default=0, min=0, label=_(u"max X dim."))
    deleted = Column(sa.Boolean, default=False, label=_(u"deleted"))

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
        return Column(sa.Integer, db.ForeignKey('address.id'))

    @declared_attr
    def order(cls):
        return db.relationship('Order', backref=backref('shipping_info', uselist=False), info={'label': _(u"order")})

    @declared_attr
    def order_id(cls):
        return Column(sa.Integer, db.ForeignKey('order.id'))

    def __unicode__(self):
        return u"Shipping info for Order No.%d" % self.order_id


class Order(LazyConfigured):
    __abstract__ = True

    STEPS = (
        (10, _(u"created")),
        (20, _(u"accepted")),
        (30, _(u"processed")),
        (40, _(u"sent")),
        (50, _(u"delivered")),
    )

    ERRORS = (
        (1, _(u"cancelled")),
        (100, _(u"no_stock")),
        (200, _(u"picking")),
        (299, _(u"delivery")),
    )

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def client(cls):
        return db.relationship('Client', backref='orders', info={'label': _(u"client")})

    @declared_attr
    def client_id(cls):
        return Column(sa.Integer, db.ForeignKey('client.id'))

    @declared_attr
    def shipping_option(cls):
        return db.relationship('ShippingOption', backref='orders', info={'label': _(u"shipping option")})

    @declared_attr
    def shipping_option_id(cls):
        return Column(sa.Integer, db.ForeignKey('shipping_option.id'))

    @declared_attr
    def billing_address(cls):
        return db.relationship('Address', backref='billed_orders', info={'label': _(u"billing address")})

    @declared_attr
    def billing_address_id(cls):
        return Column(sa.Integer, db.ForeignKey('address.id'))

    date = Column(sa.DateTime, auto_now=True, label=_(u"date"))
    tracknb = Column(sa.String(30), nullable=True, label=_(u"tracking number"))
    shipping_fee = Column(sa.Numeric(11,2), label=_(u"shipping fee"))
    discount = Column(sa.Numeric(11,2), label=_(u"discount"))
    step = Column(su.ChoiceType(STEPS, impl=sa.Integer()), label=_(u"step"))
    error = Column(su.ChoiceType(ERRORS, impl=sa.Integer()), nullable=True, label=_(u"error"))
    closed = Column(sa.Boolean, default=False, label=_(u"closed"))

    def __unicode__(self):
        return u"Order No.%d for %s" % (self.id, self.client)

class Item(LazyConfigured):
    __abstract__ = True

    id = Column(sa.Integer, primary_key=True)

    @declared_attr
    def order(cls):
        return db.relationship('Order', backref='items', info={'label': _(u"order")})

    @declared_attr
    def order_id(cls):
        return Column(sa.Integer, db.ForeignKey('order.id'))

    qty = Column(sa.SmallInteger, min=1, label=_(u"quantity"))
    price = Column(sa.Numeric(11,2), label=_(u"unit price"))

    def __unicode__(self):
        return u"Order No.%d for %s" % (self.id, self.client)

