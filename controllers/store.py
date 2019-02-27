import sys
from flask import Flask, Blueprint, redirect, current_app, request, session, g, abort, render_template, Response
from flask_login import login_required, current_user

from models.store import *

store = Blueprint('store', __name__)

#showcase the item list to verify
@store.route('/items', methods=['GET'])
@login_required
def merchant_items():
  try:
    if request.method == 'GET':
      items = fetch_items()
      return render_template("store/items_list.html",items=items)
  except Exception as e:
    return render_template("store/items_list.html")

@store.route('/approve_action', methods=['GET'])
@login_required
def approve_action():
  try:
    if request.method == 'GET':
      items = fetch_approval_items()
      return render_template("store/action.html",items=items)
  except Exception as e:
    print e
    return render_template("store/action.html")

@store.route('/action_taken/<iid>', methods=['GET'])
@login_required
def action_taken(iid):
  try:
    if request.method == 'GET':
      items = action_taken_item(iid)
      return redirect("/approve_action")
  except Exception as e:
    print e
    return redirect("/approve_action")

@store.route('/add_items', methods=['GET','POST'])
@login_required
def add_items():
  try:
    if request.method == 'POST':
      items = save_item(request.form)
      return redirect("/items")
    elif request.method == 'GET':
      return render_template("store/add.html",items=items)
  except Exception as e:
    print e
    return render_template("store/add.html")

@store.route('/add_approval_items', methods=['GET','POST'])
@login_required
def add_approval_items():
  try:
    if request.method == 'POST':
      items = save_for_approval_item(request.form)
      return redirect("/items")
    elif request.method == 'GET':
      return render_template("store/add.html",items=items)
  except Exception as e:
    print e
    return render_template("store/add.html")

@store.route('/remove_item/<iid>', methods=['GET','POST'])
@login_required
def remove_item(iid):
  try:
    if request.method == 'GET':
      delete_item(iid)
      return redirect("/items")
  except Exception as e:
    print e
    return redirect("/items")

@store.route('/remove_approval_item/<iid>', methods=['GET','POST'])
@login_required
def remove_approval_item(iid):
  try:
    if request.method == 'GET':
      delete_approval_item(iid)
      return redirect("/items")
  except Exception as e:
    print e
    return redirect("/items")

@store.route('/edit_items/<iid>', methods=['GET','POST'])
@login_required
def edit_items(iid):
  try:
    if request.method == 'POST':
      items = edit_item(request.form,iid)
      return redirect("/items")
    elif request.method == 'GET':
      item = get_item(iid)
      return render_template("store/edit.html",item=item)
  except Exception as e:
    print e
    return render_template("store/edit.html")

@store.route('/edit_approval_items/<iid>', methods=['GET','POST'])
@login_required
def edit_approval_items(iid):
  try:
    if request.method == 'POST':
      items = edit_for_approval_item(request.form,iid)
      return redirect("/items")
    elif request.method == 'GET':
      item = get_item(iid)
      return render_template("store/edit.html",item=item)
  except Exception as e:
    print e
    return render_template("store/edit.html")