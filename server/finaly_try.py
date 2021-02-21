from fastapi import FastAPI,status,Response
from typing import List, Optional
from pydantic import BaseModel, parse,validator,ValidationError,constr,Schema
from pydantic.class_validators import Validator


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DB ~~~~~~~~~~~~~~~~~~~~~~~ #
from sqlalchemy import Column, Integer, String,TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "postgresql://odoo12:odoo12@localhost/test_audio"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
BaseORM = declarative_base()
sessionLocal = sessionmaker(bind=engine)
db=sessionLocal()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ DB ~~~~~~~~~~~~~~~~~~~~~~~ #
class GenericUpdateModel(BaseModel):
    audioFileMetadata: dict

class BaseData(BaseModel):
    audioFileType: str
    audioFileMetadata: dict

    @validator('audioFileType')
    def check_valid_type(ftype):
        valid_argumentspecs= ['song','podcast','audiobook']
        if ftype not in valid_argumentspecs:
            raise ValueError('Invalid Audio File Type:'+ftype)
        return ftype

class audioFileItem(BaseModel):
    id: Optional[int]
    duration: int
    name: constr(min_length=0, max_length=100)
    upload_date :datetime.datetime

    # TODO : FIX validation issue
    # Accepted format "upload_date":"2019-06-20T01:02:03+05:00"

    @validator('duration')
    def postive_duration_only(duration_value):
        if duration_value <= 0:
            raise ValueError('Duration cannot be negative')
        return duration_value

    def _get_cleaned_record(existing_rec,update_data):
        for key in update_data.keys():
            if key in existing_rec.dict().keys():
                existing_rec.__setattr__(key,update_data.get(key))
        return existing_rec.parse_obj(existing_rec)
    
    class Config:
        orm_mode = True

class audioFileSong(audioFileItem): 
    pass

class audioFilePodcast(audioFileItem):
    host: constr(min_length=0, max_length=100)
    participants: Optional[list]

    @validator('participants')
    def validate_participants(list_data):
        if list_data:
            if len(list_data) > 10:
                    raise ValueError('Cannot have more than 10 participants')
            else:
                for id,name in enumerate(list_data):
                    if len(name) >100:
                        raise ValueError("Participant: "+name+" cannot have name length more than 100")
        return list_data
    


class audioFileBook(audioFileItem):
    author: constr(min_length=0, max_length=100)
    narrator: constr(min_length=0, max_length=100)  


class orm_audioFileItem():
    id = Column(Integer, primary_key=True, autoincrement=True,index=True)
    upload_date = Column(TIMESTAMP)
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

runner = FastAPI()

@runner.on_event("startup")
def on_app_start():
    BaseORM.metadata.create_all(bind=engine)

@runner.get("/{audioFileType}")
@runner.get("/{audioFileType}/{audioFileID}")
def fetch_record(audioFileType:str=False,audioFileID:int=False):
    _validator_class=False
    _data_class=False
    existing_records=False
    try:
        if audioFileType == "song":
            _validator_class=audioFileSong
            _data_class=orm_audioFileSong
        elif audioFileType == "podcast":
            _validator_class=audioFilePodcast
            _data_class=orm_audioFilePodcast
        elif audioFileType == "audiobook":
            _validator_class=audioFileBook
            _data_class=orm_audioFileBook
        if _validator_class and _data_class:
            if audioFileID:
                existing_record= _data_class._get_by_id(_data_class,db,audioFileID)
                if existing_record:
                    existing_record_validated=_validator_class.from_orm(existing_record)
                    return existing_record_validated
            else:
                existing_records= _data_class._get_all(_data_class,db)
                return existing_records
    except ValidationError as e:
        return e.errors()

@runner.put("/create")
def create_record(body_data:BaseData):
    _validator_class=False
    _data_class=False
    audioFileType=body_data.audioFileType
    audioFileMetadata=body_data.audioFileMetadata
    try:
        if audioFileType == "song":
            _validator_class=audioFileSong
            _data_class=orm_audioFileSong
        elif audioFileType == "podcast":
            _validator_class=audioFilePodcast
            _data_class=orm_audioFilePodcast
        elif audioFileType == "audiobook":
            _validator_class=audioFileBook
            _data_class=orm_audioFileBook
        if _validator_class and _data_class:
            data_cleaned=_validator_class.parse_obj(audioFileMetadata).dict()
            record_id=_data_class.create(_data_class,db,data_cleaned)
            return {'id':record_id}
        else:
            return {'id':False}
    except ValidationError as e:
        return e.errors()

@runner.delete("/{audioFileType}/{audioFileID}")
def unlink_record(audioFileType:str,audioFileID:int,response: Response):
    response.status_code = status.HTTP_400_BAD_REQUEST
    _data_class=False
    rec_status=False
    try:
        if audioFileType == "song":
            _data_class=orm_audioFileSong
        elif audioFileType == "podcast":
            _data_class=orm_audioFilePodcast
        elif audioFileType == "audiobook":
            _data_class=orm_audioFileBook
        if _data_class:
            rec_status= _data_class._unlink_id(_data_class,db,audioFileID)
            if rec_status:
                response.status_code = status.HTTP_202_ACCEPTED
    except ValidationError as e:
        return e.errors()
    
    return {"deleted":rec_status}

@runner.patch("/{audioFileType}/{audioFileID}")
def update_record(audioFileType:str,audioFileID:int,update_data:GenericUpdateModel,response: Response):
    update_dict=update_data.dict().get('audioFileMetadata',{})
    response.status_code = status.HTTP_400_BAD_REQUEST
    _validator_class=False
    _data_class=False
    existing_record=False
    try:
        if audioFileType == "song":
            _validator_class=audioFileSong
            _data_class=orm_audioFileSong
        elif audioFileType == "podcast":
            _validator_class=audioFilePodcast
            _data_class=orm_audioFilePodcast
        elif audioFileType == "audiobook":
            _validator_class=audioFileBook
            _data_class=orm_audioFileBook
        if _validator_class and _data_class:
            existing_record= _data_class._get_by_id(_data_class,db,audioFileID)
            if existing_record:
                existing_record_validated=_validator_class.from_orm(existing_record)
                cleaned_data=existing_record_validated._get_cleaned_record(update_dict)
                _data_class._update_rec(existing_record,db,cleaned_data.dict())
                response.status_code = status.HTTP_200_OK
                return _data_class._get_by_id(_data_class,db,audioFileID)
            else:
                return {"error":"record not found"}
    except ValidationError as e:
        return e.errors()
    return {}
    
