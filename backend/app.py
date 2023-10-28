#!/bin/python3
from flask import Flask

app = Flask(__name__)


@app.route('/locations')
def locations():
        return 'Hello, World!'
