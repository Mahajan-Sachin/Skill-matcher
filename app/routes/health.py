from flask import Blueprint, jsonify
from app.db.connection import get_db_connection

health_bp = Blueprint("health", __name__)

@health_bp.route("/health/db", methods=["GET"])
def db_health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ✅ IMPORTANT FIX

        cursor.execute("SELECT 1")
        cursor.fetchone()  # ✅ consume result

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Database connection successful"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
