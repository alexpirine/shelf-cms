from flask import request
from flask.ext.admin.babel import lazy_gettext as _
from flask.ext.security import current_user
from flask.ext.security.forms import PasswordField
from flask.ext.security.forms import EqualTo
from flask.ext.security.forms import password_required, password_length
from flask.ext.security.recoverable import update_password
from shelf.admin.view import SQLAModelView

class UserModelView(SQLAModelView):
    column_list = ('email', "active")
    default_forbidden_columns = ("password",)
    can_edit = True
    can_create = True
    can_delete = True
    can_export = True

    def __init__(self, *args, **kwargs):
        self.forbidden_columns = self.default_forbidden_columns
        super(UserModelView, self).__init__(*args, **kwargs)

    def get_create_form(self):
        form = super(UserModelView, self).get_edit_form()

        class ImprovedForm(form):
            new_password = PasswordField(_("new password"), validators = [password_required, password_length])
            new_password_confirm = PasswordField(_("retype password"), validators=[EqualTo('new_password', message=_("Passwords do not match"))])

            def validate(self):
                if not super(ImprovedForm, self).validate():
                    return False

                return True

            def populate_obj(self, obj):
                super(ImprovedForm, self).populate_obj(obj)

                if self.new_password.data:
                    update_password(obj, self.new_password.data)

        return ImprovedForm

    def get_edit_form(self):
        form = super(UserModelView, self).get_edit_form()

        class ImprovedForm(form):
            new_password = PasswordField(_("new password"))
            new_password_confirm = PasswordField(_("retype password"), validators=[EqualTo('new_password', message=_("Passwords do not match"))])

            def validate(self):
                if not super(ImprovedForm, self).validate():
                    return False

                return True

            def populate_obj(self, obj):
                super(ImprovedForm, self).populate_obj(obj)

                if self.new_password.data:
                    update_password(obj, self.new_password.data)

        return ImprovedForm

    def edit_form(self, obj=None):
        form = super(UserModelView, self).edit_form(obj)

        if not current_user.has_role('superadmin'):
            delattr(form, "roles")
            delattr(form, "active")

            if current_user != obj:
                delattr(form, "new_password")
                delattr(form, "new_password_confirm")

        return form

    def scaffold_list_columns(self):
        columns = super(UserModelView, self).scaffold_list_columns()
        for column in self.forbidden_columns:
            columns.remove(column)
        return columns

    def scaffold_form(self):
        form = super(UserModelView, self).scaffold_form()
        for column in self.forbidden_columns:
            delattr(form, column)
        return form

    def is_accessible(self):
        if request.endpoint == "userview.edit_view" and \
                int(request.args['id']) == current_user.id:
            return current_user.is_authenticated and \
                    (current_user.has_role('admin') or \
                    current_user.has_role('superadmin'))
        return current_user.is_authenticated and \
                current_user.has_role('superadmin')
