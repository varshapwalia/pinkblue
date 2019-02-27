from flask_mongoengine import MongoEngine
from ..base import BaseDocument, DefaultDocument, current_datetime
from bson.objectid import ObjectId

db = MongoEngine()

class Items(BaseDocument):
  """A base document defining certain critical fields
    
    #Essential Params
    :param StringField item_id: Unique id sent by clover api
    :param StringField name: name of the item
    :param StringField price: Price of the item
    :param ReferenceField merchant: Reference which merchant it belongs to.
    
    """
  #Essential Params
  item_id = db.StringField(required=True)
  name = db.StringField(required=True)
  price = db.FloatField(required=True)
  quantity = db.IntField(required=True)
  vendor = db.StringField(required=True)
  batch_no = db.IntField(required=True)
  active_status = db.BooleanField(Default=False)
  

  meta = {
    'indexes': ['-created_at'],
    'ordering': ['-created_at']
  }

class ApprovalItems(BaseDocument):
  """A base document defining certain critical fields
    
    #Essential Params
    :param StringField item_id: Unique id sent by clover api
    :param ReferenceField item: item

    """
  #Essential Params
  action_type = db.StringField(required=True,unique=True) #ADD, DEL , EDIT
  item = db.ReferenceField('Items')
  

  meta = {
    'indexes': ['-created_at'],
    'ordering': ['-created_at']
  }

def save_item(form):
  name = form["name"]
  item_id = form["item_id"]
  price = form["price"]
  quantity = form["quantity"]
  batch = form["batch"]
  vendor = form["vendor"]
  Items(name=name,item_id=item_id,price=price,quantity=quantity,batch_no=batch,vendor=vendor,active_status=True).save()

def delete_item(iid):
  item = Items.objects(id=ObjectId(iid)).first()
  item.delete()
  return True

def edit_item(form,iid):
  name = form["name"]
  item_id = form["item_id"]
  price = form["price"]
  quantity = form["quantity"]
  batch = form["batch"]
  vendor = form["vendor"]
  item = Items.objects(id=ObjectId(iid)).first()
  if item:
    item.name = name
    item.item_id = item_id
    item.price = float(price)
    item.quantity = int(quantity)
    item.batch = int(batch)
    item.vendor = vendor
    item.save()

def get_item(iid):
  item = Items.objects(id=ObjectId(iid)).first()
  if item:
    return item

def save_for_approval_item(form):
  name = form["name"]
  item_id = form["item_id"]
  price = form["price"]
  quantity = form["quantity"]
  batch = form["batch"]
  vendor = form["vendor"]
  item = Items(name=name,item_id=item_id,price=price,quantity=quantity,batch_no=batch,vendor=vendor).save()
  ApprovalItems(item=item,action_type="ADD").save()

def edit_for_approval_item(form,iid):
  name = form["name"]
  item_id = form["item_id"]
  price = float(form["price"])
  quantity = int(form["quantity"])
  batch = int(form["batch"])
  vendor = form["vendor"]
  item = Items.objects(id=ObjectId(iid)).first()
  if item:
    item.name = name
    item.item_id = item_id
    item.price = price
    item.quantity = quantity
    item.batch = batch
    item.vendor = vendor
    item.active_status = False
    item.save()
    ApprovalItems(item=item,action_type="EDIT").save()

def delete_approval_item(iid):
  item = Items.objects(id=ObjectId(iid)).first()
  if item:
    item.active_status=False
    item.save()
    ApprovalItems(item=item,action_type="DEL").save()


def fetch_items():
  items = Items.objects(active_status=True).all()
  if items:
    return items
  else:
    return False

def fetch_approval_items():
  approval_items=ApprovalItems.objects.all()
  if approval_items:
    return approval_items
  else:
    return False

def action_taken_item(iid):
  aitem = ApprovalItems.objects(id=ObjectId(iid)).first()
  atype = aitem.action_type
  if atype=="ADD":
    aitem.item.active_status=True
    aitem.item.save()
    aitem.delete()
  elif atype=="EDIT":
    aitem.item.active_status=True
    aitem.item.save()
    aitem.delete()
  elif atype=="DEL":
    aitem.item.delete()
    aitem.delete()
  else:
    return False