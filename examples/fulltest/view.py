# coding: utf-8

from flask import render_template
from models import Post, IndexPage, ContactPage


def init_views(app):
    @app.route('/')
    def index_view():
        page = IndexPage.query.first()
        posts = Post.query.order_by(Post.publication_date).all()
        return render_template("index.html", posts=posts, page=page)

    @app.route('/contact')
    def contact_view():
        page = ContactPage.query.first()
        return render_template("contact.html", page=page)

    @app.route('/actu-<int:post_id>')
    def post_view(post_id):
        post = Post.query.get(post_id)
        return render_template("post.html", post=post)

    @app.template_filter('date')
    def simple_date_format(date, format=None):
        try:
            return date.strftime("%d/%m/%Y")
        except ValueError:
            return date
