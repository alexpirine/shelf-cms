# coding: utf-8

from flask import current_app

from shelf.plugins.ecommerce import abstract_models as AM

__all__ = AM.__all__

for class_name in __all__:
    settings_class = current_app.config.get('shelf.ec.models.%s' % class_name)
    if not settings_class:
<<<<<<< HEAD
        globals()[class_name] = type(class_name, (getattr(AM, class_name),), {'__module__': __name__})
=======
        globals()[class_name] = type(class_name, (getattr(AM, class_name),), {})
        globals()[class_name].__module__ = __name__
>>>>>>> 7c01d0903a4190a7d79c4f41501673b851b62a7c
    else:
        globals()[class_name] = settings_class
