from flask import Flask
from config import Config
from extensions import db, login_manager
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app); login_manager.init_app(app)
    from models import User
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.devices import devices_bp
    from routes.customers import customers_bp
    from routes.settings import settings_bp
    app.register_blueprint(auth_bp); app.register_blueprint(main_bp)
    app.register_blueprint(devices_bp,url_prefix="/devices")
    app.register_blueprint(customers_bp,url_prefix="/customers")
    app.register_blueprint(settings_bp)
    @login_manager.user_loader
    def load_user(uid): return db.session.get(User,int(uid))
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@smartnet.local").first():
            u=User(full_name="SmartNet Admin",email="admin@smartnet.local",role="admin")
            u.set_password("ChangeMe123!"); db.session.add(u); db.session.commit()
    return app
