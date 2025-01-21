import awsgi
from flask_cors import CORS
from flask_restful import Api
from services.controller import *
from flask import Flask, Response
from flask_jwt_extended import JWTManager
from shared.configs import CONFIG as config
from shared.uniservices.after_request import Handler


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES