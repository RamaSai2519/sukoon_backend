import awsgi
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from services.controller import *
from shared.configs import CONFIG as config