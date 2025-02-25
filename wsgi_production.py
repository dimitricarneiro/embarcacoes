from werkzeug.middleware.dispatcher import DispatcherMiddleware

from app import create_app

app = create_app()

application = DispatcherMiddleware(app,
                                   {
                                       '/embarcacoes': app
                                   }
                                   )
                                
