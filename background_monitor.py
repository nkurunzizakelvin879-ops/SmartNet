"""Opt-in single-process background monitoring worker."""
import os
import threading
import time
from datetime import datetime

_worker_started = False
_worker_lock = threading.Lock()

def start_worker(app):
    global _worker_started
    if os.getenv("SMARTNET_BACKGROUND_MONITORING", "0").lower() not in ("1", "true", "yes"):
        return False
    # Flask debug reloader parent process must not start a duplicate worker.
    if app.debug and os.getenv("WERKZEUG_RUN_MAIN") != "true":
        return False
    with _worker_lock:
        if _worker_started:
            return False
        _worker_started = True

    interval = max(30, int(os.getenv("MONITORING_INTERVAL_SECONDS", "60")))

    def loop():
        while True:
            try:
                with app.app_context():
                    from extensions import db
                    from models import Device, MonitoringAlert
                    from monitoring_engine import ping_address
                    now = datetime.utcnow()
                    devices = Device.query.filter(
                        Device.monitoring_enabled.is_(True),
                        Device.ip_address.isnot(None),
                    ).all()
                    for device in devices:
                        previous = device.status
                        online, latency = ping_address(device.ip_address)
                        current = "Online" if online else "Offline"
                        device.status = current
                        device.last_checked = now
                        device.latency_ms = latency
                        if online:
                            device.last_seen = now
                        if previous not in ("Unknown", current):
                            db.session.add(MonitoringAlert(
                                device_id=device.id, device_name=device.name,
                                ip_address=device.ip_address, old_status=previous,
                                new_status=current, created_at=now,
                            ))
                    db.session.commit()
            except Exception:
                app.logger.exception("SmartNet background monitoring cycle failed")
                try:
                    with app.app_context():
                        from extensions import db
                        db.session.rollback()
                except Exception:
                    pass
            time.sleep(interval)

    thread = threading.Thread(target=loop, name="SmartNetMonitor", daemon=True)
    thread.start()
    app.logger.info("Background monitoring worker started; interval=%s seconds", interval)
    return True
