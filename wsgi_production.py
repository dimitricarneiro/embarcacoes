from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app import create_app, db

app = create_app()

application = DispatcherMiddleware(app)

