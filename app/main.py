from flask import Flask, render_template
from dotenv import load_dotenv
import os

from app.routes.health import health_bp
from app.routes.recommend import recommend_bp
from app.routes.career_advisor import career_bp

def create_app():
    # ✅ LOAD .env FIRST
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="../frontend/templates",
        static_folder="../frontend/static"
    )

    # Optional debug check (keep for now)
    print("HF_API_TOKEN:", os.getenv("HF_API_TOKEN"))

    app.register_blueprint(health_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(career_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app
