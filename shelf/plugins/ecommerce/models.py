# coding: utf-8

from flask import current_app

from shelf.plugins.ecommerce import abstract_models as AM

__all__ = [
    'Client',
    'Address',
    'Carrier',
    'Country',
    'DeliveryZone',
    'ShippingOption',
]

if not current_app.config.get('shelf.ec.models.Client'):
    class Client(AM.Client):
        pass
else:
    Client = current_app.config.get('shelf.ec.models.Client')

if not current_app.config.get('shelf.ec.models.Address'):
    class Address(AM.Address):
        pass
else:
    Address = current_app.config.get('shelf.ec.models.Address')

if not current_app.config.get('shelf.ec.models.Carrier'):
    class Carrier(AM.Carrier):
        pass
else:
    Carrier = current_app.config.get('shelf.ec.models.Carrier')

if not current_app.config.get('shelf.ec.models.Country'):
    class Country(AM.Country):
        pass
else:
    Country = current_app.config.get('shelf.ec.models.Country')

if not current_app.config.get('shelf.ec.models.DeliveryZone'):
    class DeliveryZone(AM.DeliveryZone):
        pass
else:
    DeliveryZone = current_app.config.get('shelf.ec.models.DeliveryZone')

if not current_app.config.get('shelf.ec.models.ShippingOption'):
    class ShippingOption(AM.ShippingOption):
        pass
else:
    ShippingOption = current_app.config.get('shelf.ec.models.ShippingOption')

if not current_app.config.get('shelf.ec.models.Order'):
    class Order(AM.Order):
        pass
else:
    Order = current_app.config.get('shelf.ec.models.Order')

if not current_app.config.get('shelf.ec.models.Item'):
    class Item(AM.Item):
        pass
else:
    Item = current_app.config.get('shelf.ec.models.Item')

if not current_app.config.get('shelf.ec.models.ShippingInfo'):
    class ShippingInfo(AM.ShippingInfo):
        pass
else:
    ShippingInfo = current_app.config.get('shelf.ec.models.ShippingInfo')
