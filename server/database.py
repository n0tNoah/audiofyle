import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "postgresql://odoo12:odoo12@localhost/test_audio"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
BaseORM = declarative_base()