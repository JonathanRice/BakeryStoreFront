"""
    This module will describe the data model behind the CodeBlogger application.
"""

__all__ = ['BlogEntry', 'Entry', 'CommentEntry', 'DbFile', 'Product']

from google.appengine.ext import db

class Entry(db.Model):
    title = db.StringProperty()
    markdown = db.TextProperty()
    html = db.TextProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    mod_date = db.DateTimeProperty(auto_now_add=True)

class BlogEntry(Entry):
    author = db.UserProperty()
    
class CommentEntry(Entry):
    blog = db.ReferenceProperty(BlogEntry)
    name = db.TextProperty()
    #parentComment = db.ReferenceProperty(CommentEntry)
    #We will add nested comments later.
    
class DbFile(db.Model):
    name = db.StringProperty(required=True)
    data = db.BlobProperty(required=True)
    type = db.StringProperty(required=False)

class Product(db.Model):
    name = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    price = db.FloatProperty(required=True)
    imagePath = db.StringProperty(required=True)
    imageFile = db.ReferenceProperty(DbFile, required=True, collection_name='imageFile')
    imageDetailPath = db.StringProperty(required=False)
    imageDetailFile = db.ReferenceProperty(DbFile, required=False, collection_name='imageDetailFile')
    
    def delete(self):
        try:
            if self.imageFile:
                self.imageFile.delete()
        except:
            pass  #Someone deleted my image, or the delete failed,...
        super(Product, self).delete()

class Store(db.Model):
    name = db.StringProperty(required=True)
    merchantid = db.StringProperty(required=True)
    useSandbox = db.StringProperty(required=True, default="true")
    aboutUsDescription = db.TextProperty(required=False)
    currentPromotion = db.TextProperty(required=False)
    newsAndInfo = db.TextProperty(required=False)
    talkBox = db.TextProperty(required=False)
