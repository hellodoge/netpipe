# Copyright 2020 hellodoge
# Licensed under the Apache License, Version 2.0

from flask import Flask
from flask import render_template, abort, request
from flask import Response

from flask_sqlalchemy import SQLAlchemy

import markdown

import config
from config import Configuration

import base64
import binascii
from os import urandom

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)


class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.String(length=config.MAX_LEN_OF_SECRET), nullable=False, unique=True)
    private = db.Column(db.String(length=config.MAX_LEN_OF_SECRET), nullable=False, unique=True)
    text = db.Column(db.UnicodeText)
    mime = db.Column(db.String(length=config.MAX_LEN_OF_MIME), default='text/html', nullable=False)

    @staticmethod
    def get_entity(entity_id: int, public_key: str) -> str:
        entity = Entity.query.get_or_404(entity_id)
        if entity.public != public_key:
            abort(404)
        return entity

    @staticmethod
    def set_text(entity_id: int, private_key: str, text: str) -> None:
        entity = Entity.query.get_or_404(entity_id)
        if entity.private != private_key:
            abort(404)
        entity.text = text
        db.session.commit()

    @staticmethod
    def append_text(entity_id: int, private_key: str, text: str) -> None:
        entity = Entity.query.get_or_404(entity_id)
        if entity.private != private_key:
            abort(404)
        entity.text = text if entity.text is None else entity.text + text  # TODO: do it query level
        db.session.commit()

    @staticmethod
    def set_mime(entity_id: int, private_key: str, mime: str) -> None:
        entity = Entity.query.get_or_404(entity_id)
        if entity.private != private_key:
            abort(404)
        entity.mime = mime
        db.session.commit()

    @staticmethod
    def new(text=None):

        public_key = urandom(config.LEN_OF_SECRET)
        private_key = urandom(config.LEN_OF_SECRET)

        entity = Entity(
            public = 'P' + base64.urlsafe_b64encode(public_key).decode('ascii'),
            private = 'p' + base64.urlsafe_b64encode(private_key).decode('ascii')
        )

        if text is not None:
            entity.text = text

        db.session.add(entity)
        db.session.commit()

        return entity


def decode_link(link: str) -> (int, str):
    parts = link.split('!')
    if len(parts) != 2:
        abort(404)

    try:
        entity_id = int(parts[0])
    except ValueError:
        abort(404)

    secret = parts[1]

    return entity_id, secret


def encode_link(entity_id: int, secret: str) -> str:
    return f'{entity_id}!{secret}'


@app.route('/', methods=['GET'])
def index():
    with open('README.md', 'r') as readme:
        content = markdown.markdown(readme.read(), extensions=['tables'])
        return render_template('index.html', content=content, site_url=request.url_root)


@app.route('/create', methods=['GET', 'POST'])
def create():
    entity = Entity.new(text=request.get_data(as_text=True) if request.method == 'POST' else None)

    return {
        'Public link': f'{request.url_root}/{encode_link(entity.id, entity.public)}',
        'Private link': f'{request.url_root}/{encode_link(entity.id, entity.private)}'
    }


@app.route('/<entity_public>', methods=['GET'])
def fetch(entity_public):
    entity_id, public = decode_link(entity_public)
    entity = Entity.get_entity(entity_id, public)
    text = entity.text if entity.text != None else ''
    return Response(text, mimetype=entity.mime)


@app.route('/<entity_private>/<text>', methods=['GET'])
def update_get(entity_private, text):
    entity_id, private = decode_link(entity_private)
    Entity.set_text(entity_id, private, text)
    return '', 200


@app.route('/<entity_private>', methods=['PUT'])
def update_put(entity_private):
    entity_id, private = decode_link(entity_private)
    Entity.set_text(entity_id, private, request.get_data(as_text=True))
    return '', 200


@app.route('/<entity_private>', methods=['PATCH'])
def append(entity_private):
    entity_id, private = decode_link(entity_private)
    Entity.append_text(entity_id, private, request.get_data(as_text=True))
    return '', 200

@app.route('/<entity_private>/mime', methods=['POST'])
def update_mime(entity_private):
    entity_id, private = decode_link(entity_private)
    Entity.set_mime(entity_id, private, request.get_data(as_text=True))
    return '', 200

if __name__ == '__main__':
    app.run()
