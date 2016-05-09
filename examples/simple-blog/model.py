from shelf import db
from shelf import LazyConfigured
from shelf.plugins.library import PictureModelMixin
from shelf.plugins.workflow import WorkflowModelMixin, WORKFLOW_STATES
from sqlalchemy_defaults import Column

class Picture(LazyConfigured, PictureModelMixin):
    id = Column(db.Integer, primary_key=True)

class Post(LazyConfigured, WorkflowModelMixin):
    id = Column(db.Integer, primary_key=True)
    picture_id = Column(db.Integer, db.ForeignKey('picture.id'), nullable=True)
    picture = db.relationship("Picture")
    title = Column(db.String(150))
    content = Column(db.Text)
    state = Column(db.Enum(*WORKFLOW_STATES))
