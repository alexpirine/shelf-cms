# coding: utf-8

import humanize
import os
import os.path as op

from PIL import ImageFile
from base64 import b64decode
from flask import Blueprint
from flask import current_app
from flask import flash
from flask import json
from flask import redirect
from flask import request
from flask.ext.admin import helpers
from flask.ext.admin.babel import gettext
from flask.ext.admin.form import RenderTemplateWidget
from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin.base import expose
from flask_admin.contrib import fileadmin
from operator import itemgetter
from shelf.security.mixin import LoginMixin
from werkzeug import secure_filename
from wtforms.fields import TextField

_unset_value = object()

db = SQLAlchemy()

# Copied from Django:
# https://docs.djangoproject.com/en/1.9/_modules/django/core/files/images/
def get_image_dimensions(file_or_path, close=False):
    """
    Returns the (width, height) of an image, given an open file or a path.  Set
    'close' to True to close the file at the end if it is initially in an open
    state.
    """
    p = ImageFile.Parser()
    if hasattr(file_or_path, 'read'):
        file = file_or_path
        file_pos = file.tell()
        file.seek(0)
    else:
        file = open(file_or_path, 'rb')
        close = True
    try:
        # Most of the time Pillow only needs a small chunk to parse the image
        # and get the dimensions, but with some TIFF files Pillow needs to
        # parse the whole file.
        chunk_size = 1024
        while 1:
            data = file.read(chunk_size)
            if not data:
                break
            try:
                p.feed(data)
            except zlib.error as e:
                # ignore zlib complaining on truncated stream, just feed more
                # data to parser (ticket #19457).
                if e.args[0].startswith("Error -5"):
                    pass
                else:
                    raise
            except struct.error:
                # Ignore PIL failing on a too short buffer when reads return
                # less bytes than expected. Skip and feed more data to the
                # parser (ticket #24544).
                pass
            if p.image:
                return p.image.size
            chunk_size *= 2
        return (None, None)
    finally:
        if close:
            file.close()
        else:
            file.seek(file_pos)

class RemoteFileModelMixin(object):
    def get_path(self):
        return self.path

    def set_path(self, path):
        if path and len(path) == 0:
            path = None
        self.path = path

    def __unicode__(self):
        return self.path


class PictureModelMixin(object):
    path = db.Column(db.String(255))
    width = db.Column(db.Integer, default=0)
    height = db.Column(db.Integer, default=0)

    def __unicode__(self):
        return self.path


class LibraryViewMixin(object):
    pass

config = {
    "name": "Library",
    "description": "Manage your website files and medias",
    "admin": {
        "view_subclass": LibraryViewMixin,
        "template": {
            "modelview.edit_view": {
                "tail_js":"shelf-library-field-tail.html"
            },
            "modelview.create_view": {
                "tail_js": "shelf-library-field-tail.html"
            }
        }
    }
}
'''"extend": {
    "admin": {
        "auto_join": "auto_joins",
        "form": "form",
        "list_column": "list_column"
    },
    "security": {
        "roles": ["librarian"]
    },
    "script": {
        "compute_thumbs": "compute_thumbs"
    }
},'''


class RemoteFileWidget(RenderTemplateWidget):
    def __init__(self):
        RenderTemplateWidget.__init__(self, "shelf-field-file.html")


class RemoteFileField(TextField):
    widget = RemoteFileWidget()

    def __init__(self, *args, **kwargs):
        if "allow_blank" in kwargs:
            del kwargs["allow_blank"]
        super(RemoteFileField, self).__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0]

    def process_data(self, value):
        TextField.process_data(self, value)

    def populate_obj(self, obj, name):
        if getattr(obj, name) is None:
            newfile = getattr(obj.__class__, name).mapper.class_()
            setattr(obj, name, newfile)
            if self.raw_data and len(self.raw_data):
                getattr(obj, name).set_path(self.raw_data[0])


class PictureWidget(RenderTemplateWidget):
    def __init__(self):
        RenderTemplateWidget.__init__(self, "shelf-field-picture.html")


class PictureField(TextField):
    widget = PictureWidget()

    def __init__(self, label='', validators=None, width=0, height=0, **kwargs):
        if "allow_blank" in kwargs:
            del kwargs["allow_blank"]

        super(PictureField, self).__init__(label, validators, **kwargs)

        self.width = width
        self.height = height

    def populate_obj(self, obj, name):
        if getattr(obj, name) is None:
            picture = getattr(obj.__class__, name).mapper.class_()
            setattr(obj, name, picture)
        else:
            picture = getattr(obj, name)

        picture.path = self.raw_data[0]

        full_path = os.path.join(current_app.config['MEDIA_ROOT'], picture.path)
        width, height = get_image_dimensions(full_path)

        if width is None or height is None:
            raise TypeError("The chosen file doesn't seem to be a valid image")

        picture.width = width
        picture.height = height


class FileAdmin(LoginMixin, fileadmin.FileAdmin):
    list_template = "shelf-library-list.html"
    icon_list_template = "shelf-library-icon-list.html"
    upload_template = "shelf-library-upload.html"
    modal_template = "shelf-library-modal-list.html"
    icon_modal_template = "shelf-library-modal-icon-list.html"
    upload_modal_template = "shelf-library-modal-upload.html"

    mime_by_ext = {
        'text': ('.pdf', '.txt', '.doc', '.html', '.xml', '.css'),
        'archive': ('.zip',),
        'image': ('.png', '.jpg', '.jpeg', '.gif'),
        'video': ('.mpg', '.mpeg', '.wmv', '.mp4', '.flv', '.mov'),
    }

    def __init__(self, base_path = None, base_url = None, *args, **kwargs):
        if base_path is None and 'MEDIA_ROOT' in current_app.config:
            base_path = current_app.config['MEDIA_ROOT']

        if base_url is None and 'MEDIA_URL' in current_app.config:
            base_url = current_app.config['MEDIA_URL']

        super(FileAdmin, self).__init__(base_path, base_url, *args, **kwargs)

    @expose('/modal-icons/')
    @expose('/modal-icons/b/<path:path>')
    def modal_iconic_index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}

        # Parent directory
        parent_path = None
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path) and not f.startswith('.'):
                file_size = op.getsize(fp)
                file_size = humanize.naturalsize(file_size, format = '%0.f')

                mimes[rel_path] = 'other'
                for mime in self.mime_by_ext:
                    if op.splitext(rel_path)[1] in self.mime_by_ext[mime]:
                        mimes[rel_path] = mime

                if mimes[rel_path] == 'image':
                    dimensions = get_image_dimensions(fp)
                else:
                    dimensions = (None, None)

                items.append((f, rel_path, op.isdir(fp), file_size, dimensions))


        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.icon_modal_template,
                           dir_path=path, parent_path=parent_path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)

    @expose('/modal-upload/', methods = ("GET",))
    @expose('/modal-upload/b/<path:path>', methods = ("GET",))
    def modal_upload(self, path=None):
        """
            Upload view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        prev_view_type = request.args.get('pvt', None)
        if prev_view_type != 'list':
            prev_view_type = 'icons'

        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}

        # Parent directory
        parent_path = None
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path) and not f.startswith('.'):
                file_size = op.getsize(fp)
                file_size = humanize.naturalsize(file_size, format = '%0.f')
                items.append((f, rel_path, op.isdir(fp), file_size))
                mimes[rel_path] = 'other'
                for mime in self.mime_by_ext:
                    if op.splitext(rel_path)[1] in self.mime_by_ext[mime]:
                        mimes[rel_path] = mime

        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.upload_modal_template,
                           dir_path=path, parent_path=parent_path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           prev_view_type=prev_view_type,
                           actions_confirmation=actions_confirmation)

    @expose('/modal/')
    @expose('/modal/b/<path:path>')
    def modal_index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}

        # Parent directory
        parent_path = None
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path) and not f.startswith('.'):
                file_size = op.getsize(fp)
                file_size = humanize.naturalsize(file_size, format = '%0.f')

                mimes[rel_path] = 'other'
                for mime in self.mime_by_ext:
                    if op.splitext(rel_path)[1] in self.mime_by_ext[mime]:
                        mimes[rel_path] = mime

                if mimes[rel_path] == 'image':
                    dimensions = get_image_dimensions(fp)
                else:
                    dimensions = (None, None)

                items.append((f, rel_path, op.isdir(fp), file_size, dimensions))

        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.modal_template,
                           dir_path=path, parent_path=parent_path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)


    @expose('/asyncupload', methods=("POST",))
    def async_upload(self):
        mfile = request.form['file']
        mname = request.form['name']
        mpath = request.form['path']
        ffile = op.join(self._normalize_path(mpath)[1], mname)
        encoded = mfile.replace(' ', '+')
        decoded = b64decode(encoded)
        with open(ffile, 'w') as f:
            f.write(decoded)
        return "True"

    @expose('/upload/', methods=('GET', 'POST'))
    @expose('/upload/<path:path>', methods=('GET', 'POST'))
    def upload(self, path=None):
        """
            Upload view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.can_upload:
            flash(gettext('File uploading is disabled.'), 'error')
            return redirect(self._get_dir_url('.index', path))

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        form = self.upload_form()

        if helpers.validate_form_on_submit(form):
            filename = op.join(directory,
                               secure_filename(form.upload.data.filename))

            if op.exists(filename):
                flash(gettext('File "%(name)s" already exists.', name=filename),
                      'error')
            else:
                try:
                    self.save_file(filename, form.upload.data)
                    self.on_file_upload(directory, path, filename)
                    flash('%s was correctly uploaded' % form.upload.data.filename)
                    return redirect(self._get_dir_url('.index', path))
                except Exception as ex:
                    flash(gettext('Failed to save file: %(error)s', error=ex))
        elif request.form and 'async' in request.form:
            total_uploaded = 0
            for tmp_filename in json.loads(request.form['async']):
                filename = op.join(directory,
                               secure_filename(form.upload.data.filename))
                if op.exists(filename):
                    total_uploaded = total_uploaded + 1

            if total_uploaded == 0:
                flash('Nothing was uploaded', 'error')
            elif total_uploaded == 1:
                flash('%s was correctly uploaded' % tmp_filename)
                return redirect(self._get_dir_url('.index', path))
            else:
                flash('%d files were correctly uploaded' % total_uploaded)
                return redirect(self._get_dir_url('.index', path))

        return self.render(self.upload_template, form=form, dir_path=path)

    @expose('/')
    @expose('/b/<path:path>')
    def icon_index(self, path=None):
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}

        # Parent directory
        parent_path = None
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path) and not f.startswith('.'):
                file_size = op.getsize(fp)
                file_size = humanize.naturalsize(file_size, format = '%0.f')
                items.append((f, rel_path, op.isdir(fp), file_size))
                mimes[rel_path] = 'other'
                for mime in self.mime_by_ext:
                    if op.splitext(rel_path)[1] in self.mime_by_ext[mime]:
                        mimes[rel_path] = mime


        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.icon_list_template,
                           dir_path=path, parent_path=parent_path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)

    @expose('/list/')
    @expose('/list/b/<path:path>')
    def index(self, path=None):
        """
            Index view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        # Get directory listing
        items = []
        mimes = {}

        # Parent directory
        parent_path = None
        if directory != base_path:
            parent_path = op.normpath(op.join(path, '..'))
            if parent_path == '.':
                parent_path = None

        for f in os.listdir(directory):
            fp = op.join(directory, f)
            rel_path = op.join(path, f)

            if self.is_accessible_path(rel_path) and not f.startswith('.'):
                file_size = op.getsize(fp)
                file_size = humanize.naturalsize(file_size, format = '%0.f')
                items.append((f, rel_path, op.isdir(fp), file_size))
                mimes[rel_path] = 'other'
                for mime in self.mime_by_ext:
                    if op.splitext(rel_path)[1] in self.mime_by_ext[mime]:
                        mimes[rel_path] = mime


        # Sort by name
        items.sort(key=itemgetter(0))

        # Sort by type
        items.sort(key=itemgetter(2), reverse=True)

        # Generate breadcrumbs
        accumulator = []
        breadcrumbs = []
        for n in path.split(os.sep):
            accumulator.append(n)
            breadcrumbs.append((n, op.join(*accumulator)))

        # Actions
        actions, actions_confirmation = self.get_actions_list()

        return self.render(self.list_template,
                           dir_path=path, parent_path=parent_path,
                           breadcrumbs=breadcrumbs,
                           get_dir_url=self._get_dir_url,
                           get_file_url=self._get_file_url,
                           items=items,
                           mimes=mimes,
                           actions=actions,
                           actions_confirmation=actions_confirmation)


class Library(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = Blueprint("library", __name__, url_prefix="/library",
            static_folder="static", template_folder="templates")
        app.register_blueprint(self.bp)

