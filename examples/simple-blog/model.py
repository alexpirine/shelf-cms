from flask.ext.security import UserMixin, RoleMixin

from shelf.base import db
from shelf.plugins.library import PictureModelMixin
from shelf.plugins.workflow import WorkflowModelMixin, WORKFLOW_STATES

class Picture(db.Model, PictureModelMixin):
    id = db.Column(db.Integer, primary_key=True)

class Post(db.Model, WorkflowModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    picture_id = db.Column(db.Integer, db.ForeignKey('picture.id'))

    picture = db.relationship("Picture")

    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    state = db.Column(db.Enum(*WORKFLOW_STATES))
