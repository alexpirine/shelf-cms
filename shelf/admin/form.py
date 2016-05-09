from flask.ext.admin.contrib.sqla import form
from flask_admin._backwards import get_property
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

    def _get_label(self, name, field_args):
        """
            Label for field name. If it is not specified explicitly,
            then the views prettify_name method is used to find it.
            :param field_args:
                Dictionary with additional field arguments
        """
        if 'label' in field_args:
            return field_args['label']

        column_labels = get_property(self.view, 'column_labels', 'rename_columns')

        if column_labels and name in column_labels:
            return column_labels.get(name)

        prettify_override = getattr(self.view, 'prettify_name', None)
        if prettify_override:
            return prettify_override(name)

        return prettify_name(name)

    def _get_description(self, name, field_args):
        if 'description' in field_args:
            return field_args['description']

        column_descriptions = getattr(self.view, 'column_descriptions', None)

        if column_descriptions and name in column_descriptions:
            return column_descriptions.get(name)

        if hasattr(self.view.model, name):
            model_field = getattr(self.view.model, name)
            if 'description' in model_field.info and model_field.info['description']:
                return "%s%s" % (model_field.info['description'][:1].upper(), model_field.info['description'][1:])

        return None

class InlineModelConverter(form.InlineModelConverter):
    inline_field_list_type = OrderingInlineFieldList
