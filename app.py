import os
from flask import Flask,render_template, redirect, current_app, request, session, g, abort, Blueprint, flash, Response, make_response,jsonify, url_for, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, RoleNeed, UserNeed, Permission
from flask_mongoengine import MongoEngine
from bson.objectid import ObjectId
from flask_cors import CORS
# import requests
import json

# Extra packages
from datetime import datetime, timedelta
from bcrypt import hashpw, gensalt
from operator import itemgetter
from mongoengine.queryset import queryset_manager

# Importing Controllers
from controllers.main import main
from controllers.store import store

app = Flask(__name__)
CORS(app)

# Configure flask
app.config.from_object('config.ProductionConfig')
# app.config.from_object('config.DevelopmentConfig')

# login user
login_manager = LoginManager()
principals = Principal(app)
login_manager.init_app(app)
login_manager.login_view = "login"


# Connnect with mongodb
# Mongodb Settings are there in APP_SETTINGS
db = MongoEngine(app)
CORS(app)

# Blueprint urls
app.register_blueprint(main)
app.register_blueprint(store)

#Models
from models.store import *
from models.user import *



# Loading user data for authentication
@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    """ loading user data after logged in """
    # Set the identity user object
    identity.user = current_user
    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))
    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role))


# Creating user session
class SessionUser():
    """ Creating Session for Logged in user """
    def __init__(self, userid=None, username=None, password=None, roles=None, role_name=None, block=False):
        self.userid = userid
        self.username = username
        self.password = password
        self.roles = roles
        self.role_name = role_name
        self.block = block
        try:
            self.userlog_id = session['userlog_id']
        except Exception as e:
            self.userlog_id = None
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def is_block(self):
        return self.block
    def get_id(self):
        return unicode(self.userid)
    def get_userlog_id(self):
        return unicode(self.userlog_id)
    def __repr__(self):
        return '<User %r>' % self.username
    def check_password(self,password):
        return hashpw(password.encode('utf-8'),self.password.encode('utf-8'))==self.password

# Loading user data
@login_manager.user_loader
def load_user(userid):
    """ Loading user data from database """
    # Return an instance of the User model
    user = CmsUser.objects(id=userid).first()
    if user and (not user.block):
        return SessionUser(userid=str(user.id),username=user.email,password=user.password, roles=user.userrole.allowed, role_name=user.userrole.name, block = user.block)
    return None

# Fetching user from database
def get_user_by_email(email):
    """ Loading user data from database using email address """
    user = CmsUser.objects(email=email.lower()).first()
    if user:
        return SessionUser(userid=str(user.id),username=user.email,password=user.password, roles=user.userrole.allowed, role_name = user.userrole.name, block = user.block)
    return None

# Manage Login
@app.route('/login',methods=["GET","POST"])
def login():
    """ Login User """
    if request.method == 'POST':
        try:
            user = get_user_by_email(request.form['email'])
            # Compare passwords (use password hashing production)
            if user and (not user.is_block()):
                if user.check_password(request.form['password']):
                    # Keep the user info in the session using Flask-Login
                    cmsuser = CmsUser.objects(id=user.get_id()).first()
                    userlog = CmsUserLog(user=cmsuser,login_time=datetime.now()).save()
                    cmsuser.userlog.append(userlog)
                    cmsuser.save()
                    session['userlog_id'] = str(userlog.id)
                    login_user(user)
                    # Tell Flask-Principal the identity changed
                    identity_changed.send(current_app._get_current_object(), identity=Identity(user.get_id()))
                    return Response("Success")
            elif user and user.is_block():
                return Response('You are not allowed to use this panel. Please Contact Admin for more details.')
            return Response("Wrong Email or Password")
        except Exception as e:
            print e
            pass
        return Response("Some Error Occured while loggin in. Please Try Again.")
    if request.method == 'GET':
        return render_template('main/login.html')

# Manage Logout
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    """ Logout User and destroy its session """
    # Remove the user information from the session
    userlog = CmsUserLog.objects.filter(id=current_user.get_userlog_id()).first()
    userlog.logout_time = datetime.now()
    userlog.save()
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    return redirect(app.config['BASE_URL'])

def get_password(password):
    """ convert password string into hash """
    return hashpw(password.encode('utf-8'), gensalt())

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect('/login')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

# Will give you a list of urls
@app.route('/list_urls', methods=['GET'])
def list_urls():
  try:
    import urllib
    # print(current_app.url_map)
    # output = list(current_app.url_map.iter_rules())
    output = []
    for rule in app.url_map.iter_rules():
      options = {}
      temp = {}
      for arg in rule.arguments:
        options[arg] = "[{0}]".format(arg)

      methods = ','.join(rule.methods)
      url = url_for(rule.endpoint, **options)
      # print (methods,url)
      temp['url'] = url
      temp['methods'] = methods
      output.append(temp)

    return render_template_string('''
                                  <table>
                                          <tr>
                                              <td> URLs </td> 
                                              <td> Methods </td> 
                                          </tr>
                                  {% for url in output %}
                                          <tr>
                                              <td>{{ url['url'] }}</td> 
                                              <td>{{ url['methods'] }}</td> 
                                          </tr>
                                  {% endfor %}
                                  </table>
                              ''', 
                              output=output)
    
  except Exception as e:
    return jsonify({"success":0,"message":"Exception raised","error":str(e),"data":"Error Occured!"})

if __name__ == '__main__':
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)