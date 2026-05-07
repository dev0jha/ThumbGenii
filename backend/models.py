from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime  
from typing import Optional, List
from uuid import uuid4

from sqlmodel import SQLModel, Field, Relationship

def _uuid() -> str:
    return str(uuid4())