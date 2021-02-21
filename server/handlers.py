from sqlalchemy import Column, Integer, String,TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker as sessionLocal
from .database import BaseORM
class orm_audioFileItem():
    id = Column(Integer, primary_key=True, autoincrement=True,index=True)
    # upload_date = Column(TIMESTAMP)
    upload_date = Column(String(200))
    duration = Column(Integer,)
    name = Column(String(100))

    def _get_by_id(_self_name,db:sessionLocal,id:int):
        return db.query(_self_name).get(id)

    def create(_self_name,db:sessionLocal,values:dict):
        if 'id' in values.keys():
            values.pop('id')
        rec=_self_name(**values)
        db.add(rec)
        db.commit()
        if rec.id:
            return rec.id

    def _get_all(_self_name,db:sessionLocal):
        return db.query(_self_name).all()


    def _update_rec(existing_rec,db:sessionLocal,values:dict):
        if 'id' in values.keys():
            values.pop('id')
        for key in values.keys():
            if key in existing_rec.__dict__.keys():
                if values.get(key,False):
                    existing_rec.__setattr__(key,values[key])

        print(existing_rec.__dict__)
        db.commit()
        return existing_rec
    
    def _unlink_id(_class_data,db:sessionLocal,id:int):
        existing_rec=db.query(_class_data).get(id)
        print("\n\n",existing_rec)
        if existing_rec:
            db.delete(existing_rec)
            db.commit()
            return True
        else:
            return False
class orm_audioFileSong(orm_audioFileItem,BaseORM):
    __tablename__ = "audiofilesong"

class orm_audioFilePodcast(orm_audioFileItem,BaseORM):
    __tablename__ = "audiofilepocast"
    host = Column(String(100))
    participants = Column(String(1100))

class orm_audioFileBook(orm_audioFileItem,BaseORM):
    __tablename__ = "audiofilebook"
    author = Column(String(100))
    narrator = Column(String(100))
