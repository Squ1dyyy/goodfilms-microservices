from reviews.app import create_app
from reviews.exception.handlers_exc import register_error_handlers

app = create_app()

register_error_handlers(app)
