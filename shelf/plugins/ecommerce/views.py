# coding: utf-8

from flask import current_app

from shelf.plugins.ecommerce import abstract_views as AV

__all__ = []

for class_name in AV.__all__:
    settings_class = current_app.config.get('shelf.ec.views.%s' % class_name, False)

    if settings_class is None:
        continue

    __all__.append(class_name)

    if settings_class is False:
        globals()[class_name] = type(class_name, (getattr(AV, class_name),), {'__module__': __name__})
    elif settings_class is not None:
        globals()[class_name] = settings_class
