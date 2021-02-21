import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import SETTINGS
db_config=SETTINGS.get('db')
SQLALCHEMY_DATABASE_URL = db_config.get('type',"postgresql")+\
    "://"+db_config.get('user',"vishal")+\
        ":"+db_config.get('password',":(((((")+\
            "@"+db_config.get('host',"localhost")+\
            "/"+db_config.get('db_name',"test_audio")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
BaseORM = declarative_base()