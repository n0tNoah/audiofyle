from typing import List, Optional
from pydantic import BaseModel, validator,ValidationError,constr
import datetime

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

