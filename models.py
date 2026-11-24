from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(120), nullable=False)
    email=db.Column(db.String(160), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    role=db.Column(db.String(30), default="admin")
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
class Device(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(120), nullable=False)
    device_type=db.Column(db.String(50), nullable=False)
    ip_address=db.Column(db.String(45))
    location=db.Column(db.String(160))
    status=db.Column(db.String(20), default="Unknown", nullable=False)
    notes=db.Column(db.Text)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
class Customer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(120), nullable=False)
    email=db.Column(db.String(160))
    phone=db.Column(db.String(40))
    plan=db.Column(db.String(100))
    monthly_fee=db.Column(db.Float, default=0)
    status=db.Column(db.String(20), default="Active")
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
