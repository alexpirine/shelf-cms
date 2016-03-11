from wtforms.fields import FieldList
from flask import current_app, Blueprint
from wtforms.utils import unset_value
from sqlalchemy.sql.expression import desc
from flask.ext.admin.form import RenderTemplateWidget


class LocalizedViewMixin(object):
    pass


class LocalizedModelMixin(object):
    def get_langs(self):
        return self.translations

    def get_lang(self, lang):
        trads = {}
        if self.lang == lang:
            return self.value
        else:
            for trad in self.translations:
                if trad.lang not in trads:
                    trads[trad.lang] = trad.value
            if lang in trads:
                return trads[lang]

    def set_lang(self, lang, value):
        trads = {}
        if self.lang == lang:
            self.value = value
        else:
            for trad in self.translations:
                if trad.lang not in trads:
                    trads[trad.lang] = trad
            if lang in trads:
                trads[lang].value = value
            else:
                cls = self.__class__(value=value, lang=lang)
                self.translations.append(cls)

    def __unicode__(self):
        return self.value


def localized_order_by(query, joins, sort_joins, sort_field, sort_desc):
    table = sort_field.mapper.tables[0]
    query = query.outerjoin(str(sort_field).split('.')[1])
    joins.add(table.name)

    if sort_desc:
        query = query.order_by(desc(sort_field.mapper.class_.value))
    else:
        query = query.order_by(sort_field.mapper.class_.value)

    return query, joins

config = {
    "name": "Localized",
    "description": "Models, fields, buttons and utility functions to add several languages to a website",
    "model": {
        "model_subclass": LocalizedModelMixin,
        "view_subclass": LocalizedViewMixin,
        "sort": localized_order_by,
    },
    "admin": {
        "view_subclass": LocalizedViewMixin,
        "template": {
            "modelview.edit_view": {
                "tail_js":"shelf-i18n-field-tail.html"
            },
            "modelview.create_view": {
                "tail_js": "shelf-i18n-field-tail.html"
            }
        }
    }
}

class LocalizedWidget(RenderTemplateWidget):
    def __init__(self):
        RenderTemplateWidget.__init__(self, "localized-widget.html")

class LocalizedField(FieldList):
    widget = LocalizedWidget()

    def process(self, formdata, data=unset_value):
        if not(data is unset_value or not data):
            res = []
            for lang in self.langs:
                res.append(data.get_lang(lang))
            FieldList.process(self, formdata, data=res)
        else:
            FieldList.process(self, formdata, data=data)

    def populate_obj(self, obj, name):
        model = getattr(obj, name)
        if model:
            if not isinstance(model, LocalizedModelMixin):
                raise ValueError
            for i in range(len(self.langs)):
                model.set_lang(self.langs[i], self.data[i])
        else:
            model = getattr(obj.__class__, name).mapper.class_(
                    lang=self.langs[0]
            )
            for i in range(len(self.langs)):
                model.set_lang(self.langs[i], self.data[i])
            setattr(obj, name, model)

    def _extract_indices(self, prefix, formdata):
        """
        Yield indices of any keys with given prefix.

        formdata must be an object which will produce keys when iterated.  For
        example, if field 'foo' contains keys 'foo-0-bar', 'foo-1-baz', then
        the numbers 0 and 1 will be yielded, but not neccesarily in order.
        """
        offset = len(prefix) + 1
        for k in formdata:
            if k.startswith(prefix):
                k = k[offset:].split('-', 1)[0]
                if k in self.langs:
                    yield self.langs.index(k)

    def _add_entry(self, formdata=None, data=unset_value, index=None):
        assert not self.max_entries or len(self.entries) < self.max_entries, \
            'You cannot have more than max_entries entries in this FieldList'
        if index is None:
            index = self.last_index + 1
        self.last_index = index
        name = '%s-%s' % (self.short_name, self.langs[index])
        field_id = '%s-%s' % (self.id, self.langs[index])
        field = self.unbound_field.bind(form=None, name=name, prefix=self._prefix, id=field_id, _meta=self.meta,
                                        translations=self._translations)
        field.process(formdata, data)
        self.entries.append(field)
        return field

    def __init__(self, unbound_field, label=None, validators=None, min_entries=0,
                 max_entries=None, default=tuple(), **kwargs):
        self.langs = current_app.config.get("SHELF_I18N_LANGS", ("en", "fr"))
        if "allow_blank" in kwargs:
            del kwargs["allow_blank"]
        FieldList.__init__(self, unbound_field, label, validators,
                len(self.langs),
                len(self.langs),
                default,
                **kwargs)


class InternationalField(LocalizedField):
    def __init__(self, unbound_field, label=None, validators=None, min_entries=0,
                 max_entries=None, default=tuple(), **kwargs):
        self.langs = current_app.config.get("SHELF_I18N_COUNTRIES", ("en", "fr"))
        if "allow_blank" in kwargs:
            del kwargs["allow_blank"]
        FieldList.__init__(self, unbound_field, label, validators,
                len(self.langs),
                len(self.langs),
                default,
                **kwargs)


class Localized(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = Blueprint("i18n", __name__, url_prefix="/i18n",
                static_folder="static", template_folder="templates")
        app.register_blueprint(self.bp)
