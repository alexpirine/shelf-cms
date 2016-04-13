# -*- coding: utf-8 -*-


def init_filters(app):
    app.add_template_filter(generate_youtube_embed_url, "youtube")


def generate_youtube_embed_url(youtube_url):
    try:
        return youtube_url.replace(
            "https://www.youtube.com/watch?v=",
            "https://www.youtube.com/embed/")
    except AttributeError:
        return None
