from recomendations.app import create_app
from recomendations.exception.handlers_exc import register_error_handlers

app = create_app()

register_error_handlers(app)

