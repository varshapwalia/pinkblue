import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
  DEBUG = False
  TESTING = False
  CSRF_ENABLED = True
  SECRET_KEY = 'thisissecret'

class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True
  BASE_URL = 'http://localhost:5000/'
  # MongoDB
  MONGODB_DB = 'pinkblue'
  MONGODB_HOST = '127.0.0.1'
  MONGODB_PORT = 27017
  MONGODB_USERNAME = 'admin'
  MONGODB_PASSWORD = 'password'


class ProductionConfig(Config):
  DEBUG = False
  DEVELOPMENT = False
  BASE_URL = 'https://pinkblue.herokuapp.com/'
  # MongoDB
  MONGODB_DB = 'pinkblue'
  MONGODB_USERNAME = ''
  MONGODB_PASSWORD = ''
  MONGODB_HOST = ''