import secrets
import threading
import time
from sqlalchemy import inspect, text
from flask import Flask
from config import Config
from extensions import db, login_manager, csrf

_monitor_thread_started = False
_monitor_lock = threading.Lock()

def migrate_device_monitoring_columns():
    """Non-destructively add monitoring columns to existing installations."""
    inspector = inspect(db.engine)
    if "device" not in inspector.get_table_names(): return
    existing = {column["name"] for column in inspector.get_columns("device")}
    if "latency_ms" not in existing: db.session.execute(text("ALTER TABLE device ADD COLUMN latency_ms FLOAT"))
    if "last_seen" not in existing: db.session.execute(text("ALTER TABLE device ADD COLUMN last_seen DATETIME"))
    db.session.commit()

def scan_registered_devices(app):
    """Check registered IPs within an app context; one scan per cycle."""
    from routes.devices import ping_device
    from models import Device
    with app.app_context():
        for device in Device.query.filter(Device.ip_address.isnot(None), Device.ip_address != "").all():
            latency = ping_device(device.ip_address)
            device.latency_ms = latency
            device.status = "Online" if latency is not None else "Offline"
            if latency is not None:
                from datetime import datetime
                device.last_seen = datetime.utcnow()
        db.session.commit()

def monitoring_worker(app):
    interval = max(15, int(app.config.get("MONITOR_INTERVAL_SECONDS", 60)))
    while True:
        try: scan_registered_devices(app)
        except Exception as exc:
            app.logger.exception("SmartNet background monitor scan failed: %s", exc)
        time.sleep(interval)

def start_monitoring_worker(app):
    global _monitor_thread_started
    if not app.config.get("MONITORING_ENABLED", True) or app.testing: return
    with _monitor_lock:
        if _monitor_thread_started: return
        thread = threading.Thread(target=monitoring_worker, args=(app,), name="SmartNetMonitor", daemon=True)
        thread.start()
        _monitor_thread_started = True

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides: app.config.update(config_overrides)
    db.init_app(app); login_manager.init_app(app); csrf.init_app(app)
    from models import User
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.devices import devices_bp
    from routes.customers import customers_bp
    from routes.settings import settings_bp
    from routes.admin import admin_bp
    app.register_blueprint(auth_bp); app.register_blueprint(main_bp)
    app.register_blueprint(devices_bp, url_prefix="/devices")
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)
    @login_manager.user_loader
    def load_user(uid):
        try: return db.session.get(User, int(uid))
        except (TypeError, ValueError): return None
    with app.app_context():
        db.create_all()
        migrate_device_monitoring_columns()
        if not User.query.filter_by(email=app.config["ADMIN_EMAIL"]).first():
            initial_password=app.config["ADMIN_PASSWORD"] or secrets.token_urlsafe(18)
            admin=User(full_name=app.config["ADMIN_NAME"] or "SmartNet Admin",email=app.config["ADMIN_EMAIL"],role="admin")
            admin.set_password(initial_password); db.session.add(admin); db.session.commit()
            if not app.config["ADMIN_PASSWORD"]:
                print("\nSmartNet initial admin account")
                print(f"Email: {app.config['ADMIN_EMAIL']}")
                print(f"Temporary password (save it now): {initial_password}\n")
    start_monitoring_worker(app)
    return app
