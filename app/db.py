"""Database object"""
from flask_sqlalchemy import SQLAlchemy, model

DB: model.DefaultMeta = SQLAlchemy()
