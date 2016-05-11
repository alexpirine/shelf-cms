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
    class Client(AM.AbstractClient):
        pass
else:
    Client = current_app.config.get('shelf.ec.models.Client')

if not current_app.config.get('shelf.ec.models.Address'):
    class Address(AM.AbstractAddress):
        pass
else:
    Address = current_app.config.get('shelf.ec.models.Address')

if not current_app.config.get('shelf.ec.models.Carrier'):
    class Carrier(AM.AbstractCarrier):
        pass
else:
    Carrier = current_app.config.get('shelf.ec.models.Carrier')

if not current_app.config.get('shelf.ec.models.Country'):
    class Country(AM.AbstractCountry):
        pass
else:
    Country = current_app.config.get('shelf.ec.models.Country')

if not current_app.config.get('shelf.ec.models.DeliveryZone'):
    class DeliveryZone(AM.AbstractDeliveryZone):
        pass
else:
    DeliveryZone = current_app.config.get('shelf.ec.models.DeliveryZone')

if not current_app.config.get('shelf.ec.models.ShippingOption'):
    class ShippingOption(AM.AbstractShippingOption):
        pass
else:
    ShippingOption = current_app.config.get('shelf.ec.models.ShippingOption')
