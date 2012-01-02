from gaesessions import SessionMiddleware

def webapp_add_wsgi_middleware(app):
    # add lifetime=datetime.timedelta(hours=2)) as param
    app = SessionMiddleware(app, cookie_key="6353f9b2e7c47f73b48eef4544968bcd")
    return app
