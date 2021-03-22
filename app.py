# Copyright 2020 hellodoge
# Licensed under the Apache License, Version 2.0

from flask import Flask
from flask import render_template, abort, request

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
    public = db.Column(db.Binary(length=config.LEN_OF_SECRET), nullable=False)
    private = db.Column(db.Binary(length=config.LEN_OF_SECRET), nullable=False)
    text = db.Column(db.UnicodeText)

    @staticmethod
    def get_text(entity_id: int, public_key: bytes) -> str:
        entity = Entity.query.get_or_404(entity_id)
        if entity.public != public_key:
            abort(404)
        return entity.text if entity.text is not None else ''

    @staticmethod
    def set_text(entity_id: int, private_key: bytes, text: str) -> None:
        entity = Entity.query.get_or_404(entity_id)
        if entity.private != private_key:
            abort(404)
        entity.text = text
        db.session.commit()

    @staticmethod
    def append_text(entity_id: int, private_key: bytes, text: str) -> None:
        entity = Entity.query.get_or_404(entity_id)
        if entity.private != private_key:
            abort(404)
        entity.text = text if entity.text is None else entity.text + text  # TODO: do it query level
        db.session.commit()

    @staticmethod
    def new(text=None):
        entity = Entity(
            public=urandom(config.LEN_OF_SECRET),
            private=urandom(config.LEN_OF_SECRET)
        )
        if text is not None:
            entity.text = text
        db.session.add(entity)
        db.session.commit()
        return entity


def decode_link(link: str) -> (int, bytes):
    if len(link) < config.BASE64_LEN_OF_SECRET + 1:
        abort(404)

    secret, entity_id = None, None

    try:
        secret = base64.urlsafe_b64decode(link)
    except binascii.Error:
        abort(404)

    id_encoded = link[config.BASE64_LEN_OF_SECRET:]
    try:
        entity_id = int(id_encoded, 16)
    except ValueError:
        abort(404)

    return entity_id, secret


def encode_link(entity_id: int, secret: bytes) -> str:
    secret_encoded = base64.urlsafe_b64encode(secret).decode('ascii')
    id_encoded = hex(entity_id)

    return secret_encoded + id_encoded[2:]


@app.route('/', methods=['GET'])
def index():
    with open('README.md', 'r') as readme:
        content = markdown.markdown(readme.read(), extensions=['tables'])
        return render_template('index.html', content=content, site_url=Configuration.SITE_URL)


@app.route('/create', methods=['GET', 'POST'])
def create():
    entity = Entity.new(text=request.get_data(as_text=True) if request.method == 'POST' else None)

    return {
        'Public link': f'{Configuration.SITE_URL}/{encode_link(entity.id, entity.public)}',
        'Private link': f'{Configuration.SITE_URL}/{encode_link(entity.id, entity.private)}'
    }


@app.route('/<entity_public>', methods=['GET'])
def fetch(entity_public):
    entity_id, public = decode_link(entity_public)
    return Entity.get_text(entity_id, public)


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


if __name__ == '__main__':
    app.run()
