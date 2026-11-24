import os
import secrets

from dotenv import load_dotenv

# Load local development settings from .env without overriding real environment values.
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///smartnet.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "0") == "1"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@smartnet.local").strip().lower()
    ADMIN_NAME = os.getenv("ADMIN_NAME", "SmartNet Admin").strip()
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
