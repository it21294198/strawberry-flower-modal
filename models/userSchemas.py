from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class UserModel(BaseModel):
    username: str
    email: str
    userId: int # postgres ID
    roverIds: List[int]
    created_at: datetime
    updated_at: Optional[datetime] = None

class AdminModel(BaseModel):
    username: str
    email: str
    password: str
    created_at: datetime
    updated_at: Optional[datetime] = None