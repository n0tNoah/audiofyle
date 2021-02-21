from fastapi import FastAPI,status,Response
from typing import List, Optional
from pydantic import ValidationError
from pydantic.typing import NoneType
from .helpers import audioFileBook,audioFilePodcast,audioFileSong,BaseData,GenericUpdateModel
from .handlers import orm_audioFileSong,orm_audioFileBook,orm_audioFilePodcast,orm_audioFileItem
from .database import engine,BaseORM,sessionmaker
sessionLocal = sessionmaker(bind=engine)
db=sessionLocal()

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
    
