import os
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-development-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///smartnet.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
