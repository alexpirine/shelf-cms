from flask import Blueprint
from wtforms.fields import HiddenField
from flask_security import current_user
from flask_principal import PermissionDenied

from ...security.decorators import allow_superadmin

REVIEWER_ROLE = u"reviewer"
PUBLISHER_ROLE = u"publisher"
DRAFT_STATE = u"draft"
REVIEW_STATE = u"review"
PUBLIC_STATE = u"published"
WORKFLOW_STATES = (DRAFT_STATE, REVIEW_STATE, PUBLIC_STATE)

class WorkflowViewMixin(object):
    pass

class StateField(HiddenField):
    def populate_obj(self, obj, name):
        curval = getattr(obj, name)
        if self.data == getattr(obj, name):
            return
        else:
            if curval == PUBLIC_STATE:
                if not obj.can_unpublish():
                    raise PermissionDenied
            elif self.data == REVIEW_STATE:
                if not obj.can_review():
                    raise PermissionDenied
            elif self.data == PUBLIC_STATE:
                if not obj.can_publish():
                    raise PermissionDenied
            setattr(obj, name, self.data)

config = {
    "name": "Workflow",
    "description": "Workflow fonctionnality",
    "security": {
        "roles": (
            (REVIEWER_ROLE, u"Allow user to put articles for review"),
            (PUBLISHER_ROLE, u"Allow user to publish or unpublish stuff")
        )
    },
    "admin": {
        "view_subclass": WorkflowViewMixin,
        "template": {
            "modelview.edit_view": {
                "extra_btn": "workflow-button.html",
                "tail_js": "js.html"
            },
        },
        "form": {
            "state": (StateField, {"default": DRAFT_STATE})
        }
    }
}

class WorkflowModelMixin(object):
    @allow_superadmin
    def can_publish(self):
        return current_user.has_role(PUBLISHER_ROLE)

    @allow_superadmin
    def can_review(self):
        return current_user.has_role(REVIEWER_ROLE)

    @allow_superadmin
    def can_unpublish(self):
        return current_user.has_role(PUBLISHER_ROLE)

    def is_public(self):
        return self.state == PUBLIC_STATE

    def is_private(self):
        return self.state == REVIEW_STATE

    def is_draft(self):
        return self.state == DRAFT_STATE or self.state is None

    @classmethod
    def get_public(cls):
        return cls.query.filter_by(cls.state == PUBLIC_STATE)

    @classmethod
    def get_private(cls):
        return cls.query.filter_by(cls.state == REVIEW_STATE)

    @classmethod
    def get_draft(cls):
        return cls.query.filter_by(cls.state == DRAFT_STATE)

class Workflow(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = Blueprint("workflow", __name__, url_prefix="/workflow",
                static_folder="static", template_folder="templates")
        app.register_blueprint(self.bp)
