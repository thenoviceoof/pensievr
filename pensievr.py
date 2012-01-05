from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.app_identity import get_application_id
import urllib
#import urlparse # module only becomes available in 2.6
import cgi
import datetime # for posting date tracking 
import math # for log
import time
import re

import logging
from gaesessions import get_current_session

import evernote

import oauth2 as oauth

################################################################################
# Model

class EvernoteUser(db.Model):
    # info about the user
    user_id = db.StringProperty()
    notebook_id = db.StringProperty()
    # timestamps
    create_date = db.DateTimeProperty(auto_now_add=True)
    update_date = db.DateTimeProperty(auto_now_add=True)
    # how "old" of an image to show
    update_day_count = db.IntegerProperty(default=0)

################################################################################
# Controllers

from config import API_KEY, API_SECRET, DOMAIN, DEBUG

TEMP_CRED_URI = "https://%s/oauth" % DOMAIN
OWNER_AUTH_URI = "https://%s/OAuth.action" % DOMAIN
TOKEN_REQUEST_URI = "https://%s/oauth" % DOMAIN

# index
class Index(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        pars = {}
        if session.is_active() and session.get("done", None):
            posted = session.get("posted", None)
            # if we just redirected from posting, then 
            if posted:
                posted = time.time()
                session["posted"] = None
            pars["posted"] = posted
            # grab the number of posts
            user_id = session['user']
            user = EvernoteUser.get_by_key_name(user_id)
            count = user.update_day_count
            pars["count"] = "%02d" % math.floor(math.log(count+1, 2))
            self.response.out.write(template.render("templates/post.html",pars))
        else:
            if session.is_active() and session.get("message",None):
                pars["message"] = session["message"]
                session["message"] = None
            self.response.out.write(template.render("templates/index.html",pars))

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
        session['user'] = user_id

        user = EvernoteUser.get_or_insert(user_id)
        if not(user.user_id):
            user.user_id = user_id
            user.put()

        self.redirect("/")

import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors

USERSTORE_URI = "https://%s/edam/user" % DOMAIN
NOTESTORE_URI_BASE = "https://%s/edam/note/" % DOMAIN

NOTEBOOK_NAME = "Pensievr Notebook"

DEFAULT_NOTE_TITLE = "Untitled"
NOTE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>%s</en-note>
"""

# post action
class Post(webapp.RequestHandler):
    # ajax call eventually?
    def post(self):
        # check if we have session info
        session = get_current_session()
        if not(session.is_active()) or not(session["done"]):
            raise Exception("Session is not active")

        post = self.request.get("post")
        loc_lat  = self.request.get("loc_lat")
        loc_long = self.request.get("loc_long")
        local_time_stamp = self.request.get("time")

        # set up the thrift userStore
        userStoreHttpClient = THttpClient.THttpClient(USERSTORE_URI)
        userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
        userStore = UserStore.Client(userStoreProtocol)
        # check EDAM version
        versionOK = userStore.checkVersion("Python EDAMTest",
                                           UserStoreConstants.EDAM_VERSION_MAJOR,
                                           UserStoreConstants.EDAM_VERSION_MINOR)
        if not(versionOK):
            raise Exception("EDAM versions do not match")

        # unwrap the session variables
        oauth_token = session['oauth_token']
        shard = session['shard']
        user_id = session['user']
        user = EvernoteUser.get_by_key_name(user_id)
        notebook_id = user.notebook_id

        # set up the thrift protocol for noteStore
        noteStoreUri =  NOTESTORE_URI_BASE + shard
        noteStoreHttpClient = THttpClient.THttpClient(noteStoreUri)
        noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
        noteStore = NoteStore.Client(noteStoreProtocol)

        # get or make the notebook
        pensievr_nb = None
        if not(notebook_id):
            # first look for the notebook
            notebooks = noteStore.listNotebooks(oauth_token)
            for notebook in notebooks:
                if notebook.name == NOTEBOOK_NAME:
                    pensievr_nb = notebook
            # if we don't have a pensievr notebook, make one
            tmp_nb = Types.Notebook()
            tmp_nb.name = NOTEBOOK_NAME
            tmp_nb.defaultNotebook = False
            tmp_nb.published = False
            if not(pensievr_nb):
                pensievr_nb = noteStore.createNotebook(oauth_token, tmp_nb)
            # update the user
            notebook_id = pensievr_nb.guid
            user.notebook_id = notebook_id
            user.put()
        else:
            # check if the notebook is deleted - throw exception
            pensievr_nb = noteStore.getNotebook(oauth_token, notebook_id)

        # extract tags from the post
        tag_names = re.findall("#(\w+)", post)

        # make the note
        note = Types.Note()
        note.title = DEFAULT_NOTE_TITLE
        note.content = NOTE_TEMPLATE % post
        note.notebookGuid = notebook_id
        note.tagNames = tag_names
        # add in geolocation if we have it
        if loc_lat and loc_long:
            note_attr = Types.NoteAttributes()
            note_attr.latitude = float(loc_lat)
            note_attr.longitude = float(loc_long)
            note.attributes = note_attr
        createdNote = noteStore.createNote(oauth_token, note)

        # update the user days posted count
        timestamp = datetime.datetime.fromtimestamp(float(local_time_stamp)/1000)
        posted_date = timestamp.date()
        if user.update_date.date() != posted_date:
            user.update_date = timestamp
            user.update_day_count = user.update_day_count + 1
            user.put()

        session["posted"] = True
        self.redirect("/")

# logout: clear the cookies/session
class Logout(webapp.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.is_active():
            session.terminate()
        session["message"] = "Logged Out"
        self.redirect("/")

application = webapp.WSGIApplication(
    [('/', Index),
     ('/post', Post),
     ('/oauth', OAuth),
     ('/callback', OAuthCallback),
     ('/logout', Logout),
     ],
    debug=DEBUG)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
