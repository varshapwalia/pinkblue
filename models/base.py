""" Database model base class """

from flask_mongoengine import MongoEngine
from datetime import datetime, timedelta

db = MongoEngine()

def current_datetime():
  # Changing according to the TimeZone
  # return datetime.now() + timedelta(minutes=330)
  return datetime.now()

class BaseDocument(db.Document):
    """A base document defining certain critical fields
    
    :param datetime created_at: The timestamp when the document was created
    :param datetime updated_at: The timestamp when the document was last updated
   
    """

    meta = {
        'abstract': True
    }
    created_at = db.DateTimeField()
    updated_at = db.DateTimeField()

    def save(self, *args, **kwargs):
        """Triggered when the document is saved, updates the fields"""
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super(BaseDocument, self).save(*args, **kwargs)

class DefaultDocument(db.Document):
    """A base document defining certain critical fields
    
    :param datetime created_at: The timestamp when the document was created
   
    """

    meta = {
        'abstract': True
    }
    created_at = db.DateTimeField()

    def save(self, *args, **kwargs):
        """Triggered when the document is saved, updates the fields"""
        self.created_at = datetime.now()
        return super(DefaultDocument, self).save(*args, **kwargs)