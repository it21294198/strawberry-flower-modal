from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    email: str
    userId: int
    roverIds: List[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AdminModel(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None