from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from app import create_app

app = create_app()

# Monta a aplicação apenas em '/embarcacoes'
application = DispatcherMiddleware(
    lambda environ, start_response: (
        start_response("404 Not Found", [("Content-Type", "text/plain")]),
        [b"Not Found"]
    ),
    {
        '/embarcacoes': app
    }
)

if __name__ == '__main__':
    run_simple('localhost', 5000, application, use_reloader=False)
