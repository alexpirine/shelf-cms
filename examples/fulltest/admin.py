# coding: utf-8

from wtforms.fields import TextField

from flask.ext.admin.form import DateTimePickerWidget

from shelf.admin.view import SQLAModelView
from shelf.plugins.page import PageModelView
from shelf.plugins.library import PictureField, LibraryViewMixin, FileAdmin
from shelf.plugins.library import RemoteFileField, RemoteFileModelMixin
from shelf.plugins.wysiwyg import FullWysiwygField, WysiwygViewMixin, ClassicWysiwygField
from shelf.plugins.i18n import LocalizedField, LocalizedViewMixin
from shelf.plugins.workflow import WorkflowViewMixin, StateField

from models import Post, Tag, Page

class DateTimeField(TextField):
    widget = DateTimePickerWidget()

    def __init__(self, *args, **kwargs):
        if "allow_blank" in kwargs:
            del kwargs["allow_blank"]
        TextField.__init__(self, *args, **kwargs)


def init_admin(admin, session):
    admin.add_view(BlogModelView(Post, session, name="Articles", category="Blog"))
    admin.add_view(TagModelView(Tag, session, name="Tags", category="Blog"))
    admin.add_view(BasePageModelView(Page, session, name="Pages"))
    admin.add_view(FileAdmin(name=u"Bibliothèque"))


class TagModelView(SQLAModelView, LocalizedViewMixin):
    form_excluded_columns = ("posts")

    form_overrides = {
        "name": LocalizedField
    }
    form_args = {
        "name": {"default": "", "unbound_field": TextField()}
    }


class BlogModelView(SQLAModelView, LibraryViewMixin, WysiwygViewMixin,
                    RemoteFileModelMixin, LocalizedViewMixin, WorkflowViewMixin):
    column_list = ('title', 'publication_date', "tags", "state", "mode")

    form_columns = (
        'title',
        "state",
        'publication_date',
        "mode",
        'abstract', 'text',
        "video_link",
        "picture", "attachment",
    )

    form_shortcuts = (
        'title',
        'publication_date',
        'abstract', 'text',
        "attachment",
    )

    form_export_fields = (
        'title',
        'publication_date',
        'abstract', 'text',
        "attachment",
    )

    column_labels = {
        "title": "Titre",
        "abstract": u"Résumé",
        "picture": "Photo",
        "attachment": "Fichier",
        "state": "Etat"
    }

    column_descriptions = {
        "publication_date": u"Si la date de publication est dans le futur, l'article n'apparaîtra qu'à la date indiquée",
    }

    form_overrides = {
        "state": StateField,
        "title": LocalizedField,
        "date": DateTimeField,
        "abstract": LocalizedField,
        "text": LocalizedField,
        "picture": PictureField,
        "attachment": RemoteFileField
    }

    form_args = {
        "title": {"default": "", "unbound_field": TextField()},
        "abstract": {"default": "", "unbound_field": ClassicWysiwygField()},
        "text": {"default": "", "unbound_field": FullWysiwygField()},
        "picture": {"width": 400, "height": 400},
    }


class BasePageModelView(WysiwygViewMixin, PageModelView, LocalizedViewMixin):
    form_columns = ("l_title", "l_description",)
    can_create = False
    can_delete = False
    page_size = 50
    column_list = ('name', "l_title", "l_description")
    column_labels = {
        "name": "Nom",
        "l_title": "Titre",
        "l_description": "Meta-description"
    }
    form_overrides = {
        "l_title": LocalizedField,
        "l_description": LocalizedField,
    }
    form_args = {
        "l_title": {"default": "", "unbound_field": TextField()},
        "l_description": {"default": "", "unbound_field": TextField()}
    }


class IndexPageModelView(BasePageModelView):
    form_columns = ("l_title", "l_description", "intro")

    form_overrides = {
        "l_title": LocalizedField,
        "l_description": LocalizedField,
        "intro": LocalizedField
    }
    form_args = {
        "l_title": {"default": "", "unbound_field": TextField()},
        "l_description": {"default": "", "unbound_field": TextField()},
        "intro": {"default": "", "unbound_field": TextField()},
    }


class ContactPageModelView(BasePageModelView):
    form_columns = ("l_title", "l_description", "text")

    form_overrides = {
        "l_title": LocalizedField,
        "l_description": LocalizedField,
        "text": LocalizedField
    }
    form_args = {
        "l_title": {"default": "", "unbound_field": TextField()},
        "l_description": {"default": "", "unbound_field": TextField()},
        "text": {"default": "", "unbound_field": FullWysiwygField()},
    }


