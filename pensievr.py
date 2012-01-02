from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.app_identity import get_application_id
import urllib

import logging
from gaesessions import get_current_session

import oauth2 as oauth

################################################################################
# Model

class EvernoteUser(db.Model):
    # auth info
    key = db.StringProperty()
    secret = db.StringProperty()
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

TEMP_CRED_URI = "https://{0}/oauth".format(DOMAIN)
OWNER_AUTH_URI = "https://{0}/OAuth.action".format(DOMAIN)
TOKEN_REQUEST_URI = "https://{0}/oauth".format(DOMAIN)

from config import API_KEY, API_SECRET

# index
class Index:
    def get(self):
        if True:
            self.response.out.write(template.render("templates/index.html"),{})
        else:
            self.response.out.write(template.render("templates/post.html",{}))

# get the request token (temporary) and redirect to the authorization page
class OAuth:
    def get(self):
        # get request token
        consumer = oauth.Consumer(API_KEY, API_SECRET)
        client = oauth.Client(consumer)

        callback_uri = "https://%s.appspot.com/callback" % get_application_id()
        callback_uri = urllib.urlencode(callback_uri)
        request_token_url = TEMP_CRED_URI + "?oauth_callback=%s" % callback_uri
        resp, content = client.request(request_token_url, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(urlparse.parse_qsl(content))

        oauth_token = request_token['oauth_token']
        oauth_token_secret = request_token['oauth_token_secret']
        # set these in session for the callback
        session = get_current_session()
        if session.is_active():
            session['oauth_token'] = oauth_token
            session['oauth_token_secret'] = oauth_token_secret

        # redirect to the auth page
        self.redirect(OWNER_AUTH_URI + "?oauth_token={0}".format(oauth_token))

# callback endpoint of the OAuth process
class OAuthCallback:
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

        # !!! fill in with storing the oauth_token
        user = EvernoteUser.get_or_insert(user_id)
        user.user_id = user_id
        user.token = oauth_token
        user.secret = oauth_token_secret
        user.save()

# post action
class Post:
    def post(self):
        # should be ajax?
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
