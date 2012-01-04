from gaesessions import SessionMiddleware
import datetime

def webapp_add_wsgi_middleware(app):
    app = SessionMiddleware(app, cookie_key="6353f9b2e7c47f73b48eef4544968bcd",
                            lifetime=datetime.timedelta(hours=24))
    return app
