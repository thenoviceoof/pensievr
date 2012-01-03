from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.app_identity import get_application_id
import urllib
# only becomes available in 2.6
#import urlparse
import cgi
import time

import logging
from gaesessions import get_current_session

import evernote

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
        session = get_current_session()
        if session.is_active() and session["done"]:
            posted = self.request.get("posted", None)
            # if we just redirected from posting, then 
            if posted:
                posted = time.time()
            pars = {"posted": posted}
            self.response.out.write(template.render("templates/post.html",pars))
        else:
            self.response.out.write(template.render("templates/index.html",{}))

# get the request token (temporary) and redirect to the authorization page
class OAuth(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        # since we're logging in again, kill the current session
        if session.is_active():
            session.terminate()

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
        session['oauth_token'] = oauth_token
        session['oauth_token_secret'] = oauth_token_secret
        session['done'] = False

        # redirect to the auth page
        self.redirect(OWNER_AUTH_URI + "?oauth_token=%s" % oauth_token)
    def post(self):
        self.get()

# callback endpoint of the OAuth process
class OAuthCallback(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        # make sure the session is active
        if not(session.is_active()):
            raise Exception("Session is not active")

        # get the oauth_verifier passed in
        oauth_verifier = self.request.get("oauth_verifier", None)
        if not(oauth_verifier):
            raise Exception("No verifier passed in")

        # retrieve from session
        oauth_token = session['oauth_token']
        oauth_token_secret= session['oauth_token_secret']

        # create the client
        token = oauth.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)
        consumer = oauth.Consumer(API_KEY, API_SECRET)
        client = oauth.Client(consumer, token)

        token_req = TOKEN_REQUEST_URI
        resp, content = client.request(token_req + "?", "GET")
        # deprecated in 2.6+, use urlparse instead
        access_token = dict(cgi.parse_qsl(content))

        log = logging.getLogger(__name__)
        log.info(access_token)

        oauth_token = access_token['oauth_token']
        user_id = access_token['edam_userId']
        shard = access_token["edam_shard"]

        # store the oauth_token in the session - only temporary data
        session['oauth_token'] = oauth_token
        session['shard'] = shard
        session['done'] = True

        user = EvernoteUser.get_or_insert(user_id)
        user.user_id = user_id
        user.put()

        self.redirect("/")

# post action
class Post(webapp.RequestHandler):
    # ajax call eventually?
    def post(self):
        post = self.request.get("post")
        # !!! actually make the Evernote call
        self.redirect("/?" + urllib.urlencode({"posted":"true"}))

# logout: clear the cookies/session
class Logout(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        # !!! make sure this is handled
        self.redirect("/?" + urllib.urlencode({"message":"logged out"}))

application = webapp.WSGIApplication(
    [('/', Index),
     ('/post', Post),
     ('/oauth', OAuth),
     ('/callback', OAuthCallback),
     ('/logout', Logout)
     ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
