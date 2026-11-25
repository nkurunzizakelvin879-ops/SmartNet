import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    from background_monitor import start_worker
    start_worker(app)
    debug = os.getenv("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes"}
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=debug)
