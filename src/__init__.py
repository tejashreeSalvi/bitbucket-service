# src/__init__.py
from flask import Flask
from flask_restx import Api

app = Flask(__name__)
api = Api(app, version='1.0', title='Bitbucket API', description='API for Bitbucket operations')

from src.controller import bitbucket_api
api.add_namespace(bitbucket_api, path='/bitbucket')

if __name__ == '__main__':
    app.run(debug=True)
