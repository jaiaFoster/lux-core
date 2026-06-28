# core/api/app.py
#
# LUX Core REST API
# Flask app entry point. Internal only for V1.

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register route blueprints here as they are built
# from core.api.routes.opportunities import opportunities_bp
# from core.api.routes.matches import matches_bp
# app.register_blueprint(opportunities_bp)
# app.register_blueprint(matches_bp)


@app.route("/health")
def health():
    return {"status": "ok", "service": "lux-core"}


if __name__ == "__main__":
    app.run(debug=True, port=5000)
