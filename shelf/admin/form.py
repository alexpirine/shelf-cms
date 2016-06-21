from flask_admin.contrib.sqla import form
from flask_admin.contrib.sqla import fields
from flask_admin._backwards import get_property
from flask_admin.model.helpers import prettify_name
from flask_admin.model.form import converts
from shelf.plugins.order import OrderingInlineFieldList
from wtforms import fields
from prices import Price

class ShortcutValidator(object):
    field_flags = ('shortcut',)

    def __init__(self, *args, **kwargs):
        pass


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


class DecimalPriceField(fields.DecimalField):
    def process_formdata(self, valuelist):
        if valuelist and len(valuelist[0]):
            self.data = PrettyPrice(valuelist[0].replace(',', '.'))
        else:
            self.data = None

    def process_data(self, value):
        if value and value.gross:
            super(DecimalPriceField, self).process_data(value.gross)
        else:
            super(DecimalPriceField, self).process_data(0)


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

    @converts('PriceDecimal')
    def handle_decimal_price_types(self, column, field_args, **extra):
        places = getattr(column.type, 'scale', 2)
        if places is not None:
            field_args['places'] = places
        return DecimalPriceField(**field_args)

class InlineModelConverter(form.InlineModelConverter):
    inline_field_list_type = OrderingInlineFieldList
