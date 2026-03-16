from flask import Flask
from flask.json.provider import DefaultJSONProvider
import numpy as np
import os

class NumpyJSONProvider(DefaultJSONProvider):
    """Convierte tipos NumPy/Pandas a tipos Python nativos para JSON."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def create_app():
    app = Flask(__name__)
    app.json_provider_class = NumpyJSONProvider
    app.json = NumpyJSONProvider(app)

    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from .routes import main
    app.register_blueprint(main)

    return app