from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

import logging
# from gaesessions import get_current_session

################################################################################
# Model

class EvernoteUser(db.Model):
    token = db.StringProperty()
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now_add=True)
    # how "old" of an image to show
    update_day_count = db.IntegerProperty(default=0)

################################################################################
# Controllers

# index
class Index:
    def get(self):
        self.response.out.write(template.render("templates/index.html"),{})

#class OpenID:
#    pass

# post action
class Post:
    def get(self):
        self.response.out.write(template.render("templates/post.html",{}))
    def post(self):
        # should be ajax?
        self.response.out.write(template.render("templates/posted.html",{}))
