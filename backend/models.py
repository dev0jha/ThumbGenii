from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime  
from typing import Optional, List
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship

def _uuid() -> str:
    return str(uuid4())

def _now() -> datetime:
    return datetime.now()

class Thumbnail(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="job.id")
    style: str = Field(default="")
    status: str = Field(default="pending")
    error_message: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=_now)
    
    jobs: Optional["Job"] = Relationship(back_populates="thumbnails")
class Job(SQLModel, table=True):
   id: Optional[int] = Field(default=None, primary_key=True)
   prompt: str = Field(default="")
   num_thumbnails: int = Field(default=1 ,ge=1, le=10)
   status: str = Field(default="pending")
   headshot_url: Optional[str] = Field(default="")
   error_message: Optional[str] = Field(default=None)
   created_at: datetime = Field(default_factory=_now)
   
   thumbnails: List[Thumbnail] = Relationship(back_populates="jobs")