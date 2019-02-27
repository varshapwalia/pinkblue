import sys
from flask import Flask, Blueprint, redirect, current_app, request, session, g, abort, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
@login_required
def index():
  #returns the index page
  return render_template("main/index.html")