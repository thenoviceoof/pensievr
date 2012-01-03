from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.app_identity import get_application_id
import urllib
# import urlparse
import cgi

import logging
from gaesessions import get_current_session

import oauth2 as oauth

################################################################################
# Model

class EvernoteUser(db.Model):
    # info about the user
    user_id = db.StringProperty()
    # timestamps
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now_add=True)
    # how "old" of an image to show
    update_day_count = db.IntegerProperty(default=0)

################################################################################
# Controllers

DOMAIN = "sandbox.evernote.com"
# DOMAIN = "www.evernote.com"

TEMP_CRED_URI = "https://%s/oauth" % DOMAIN
OWNER_AUTH_URI = "https://%s/OAuth.action" % DOMAIN
TOKEN_REQUEST_URI = "https://%s/oauth" % DOMAIN

from config import API_KEY, API_SECRET

# index
class Index(webapp.RequestHandler):
    def get(self):
        if True:
            self.response.out.write(template.render("templates/index.html",{}))
        else:
            self.response.out.write(template.render("templates/post.html",{}))

# get the request token (temporary) and redirect to the authorization page
class OAuth(webapp.RequestHandler):
    def get(self):
        # get request token
        consumer = oauth.Consumer(API_KEY, API_SECRET)
        client = oauth.Client(consumer)

        callback_uri = "https://%s.appspot.com/callback" % get_application_id()
        callback_uri = urllib.quote(callback_uri)
        request_token_url = TEMP_CRED_URI + "?oauth_callback=%s" % callback_uri
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        # deprecated in 2.6+, use urlparse instead
        request_token = dict(cgi.parse_qsl(content))

        oauth_token = request_token['oauth_token']
        oauth_token_secret = request_token['oauth_token_secret']
        # set these in session for the callback
        session = get_current_session()
        if session.is_active():
            session['oauth_token'] = oauth_token
            session['oauth_token_secret'] = oauth_token_secret

        # redirect to the auth page
        self.redirect(OWNER_AUTH_URI + "?oauth_token=%s" % oauth_token)
    def post(self):
        self.get()

# callback endpoint of the OAuth process
class OAuthCallback(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        if not(session.is_active()):
            raise Exception("Session is not active")

        oauth_token = session['oauth_token']
        oauth_token_secret= session['oauth_token_secret']
        token = oauth.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)
        consumer = oauth.Consumer(API_KEY, API_SECRET)
        client = oauth.Client(consumer, token)

        resp, content = client.request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))

        oauth_token = access_token['oauth_token']
        oauth_token_secret = access_token['oauth_token_secret']
        user_id = access_token['edam_userId']

        # store the oauth_token in the session - only temporary data
        session['oauth_token'] = oauth_token
        session['oauth_token_secret'] = oauth_token_secret

        user = EvernoteUser.get_or_insert(user_id)
        user.user_id = user_id
        user.put()

# post action
class Post(webapp.RequestHandler):
    # ajax call
    def post(self):
        # !!! actually make the Evernote call
        self.response.out.write(template.render("templates/posted.html",{}))

application = webapp.WSGIApplication(
    [('/', Index),
     ('/post', Post),
     ('/oauth', OAuth),
     ('/callback', OAuthCallback),
     ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
