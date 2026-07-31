from auth.app import create_app
from auth.exception.handlers_exc import register_error_handlers


app = create_app()

register_error_handlers(app)
