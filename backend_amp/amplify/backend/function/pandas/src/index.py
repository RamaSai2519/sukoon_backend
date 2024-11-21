import awsgi
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from services.controller import *
from flask_jwt_extended import JWTManager
from shared.configs import CONFIG as config

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES

api = Api(app)
JWTManager(app)
CORS(app, supports_credentials=True)

api.add_resource(BulkInsertUsersService, '/pandas/bulk_users')
api.add_resource(RecommendExpertService, '/pandas/recommend_expert')


def handler(event, context):
    return awsgi.response(app, event, context)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
