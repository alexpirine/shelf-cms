from flask import Blueprint

class PreviewableViewMixin(object):
    pass

class PreviewableModelMixin(object):
    def get_url(self):
        raise NotImplementedError

config = {
    "name": "Preview",
    "description": "Simple preview of a model or a page",
    "admin": {
        "view_subclass": PreviewableViewMixin,
        "template": {
            "modelview.edit_view": {
                "extra_btn": "preview_button.html"
            },
            "modelview.create_view": {
                "extra_btn": "preview_button.html"
            }
        }
    }
}

class Preview(object):
    def __init__(self):
        self.config = config

    def init_app(self, app):
        self.bp = Blueprint("preview", __name__, url_prefix="/preview",
                static_folder="static", template_folder="templates")
        app.register_blueprint(self.bp)
