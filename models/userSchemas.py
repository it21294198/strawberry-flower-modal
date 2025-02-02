from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel



class RoverModel(BaseModel):
    roverId: int
    nickname: str

class UserModel(BaseModel):
    username: str
    email: str
    userId: int
    rovers: Optional[List[RoverModel]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AdminModel(BaseModel):
    username: str
    email: str
    password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None