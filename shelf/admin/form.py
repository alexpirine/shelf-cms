from flask.ext.admin.contrib.sqla import form
from shelf.plugins.order import OrderingInlineFieldList

class ShortcutValidator(object):
    field_flags = ('shortcut',)

    def __init__(self, *args, **kwargs):
        pass

class ModelConverter(form.AdminModelConverter):
    def convert(self, model, mapper, prop, field_args, hidden_pk):
        kwargs = {
            'validators': [],
        }

        if field_args:
            kwargs.update(field_args)

        form_shortcuts = getattr(self.view, 'form_shortcuts', None)

        if form_shortcuts and prop.key in form_shortcuts:
            if kwargs['validators']:
                # flask-admin creates a copy of this list since we will be modifying it;
                # so we do the same, without even knowing the exact reason
                kwargs['validators'] = list(kwargs['validators'])

            kwargs['validators'].append(ShortcutValidator)

        res = super(ModelConverter, self).convert(model, mapper, prop, kwargs, hidden_pk)

        return res

class InlineModelConverter(form.InlineModelConverter):
    inline_field_list_type = OrderingInlineFieldList
