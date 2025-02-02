from datetime import datetime
from pydantic import BaseModel

class ImageRequest(BaseModel):
    image: str

class Base64ImageInput(BaseModel):
    base64_string: str
    file_extension: str = "png"

class RoverData(BaseModel):
    initial_id: int
    rover_status: int
    user_id: int

class ImageData(BaseModel):
    id: int
    rover_id: int
    random_id: int
    battery_status: float
    temp: float
    humidity: float
    result_image: str
    image_data: str
    created_at: datetime