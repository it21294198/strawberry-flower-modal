import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from dotenv import load_dotenv


from database import DatabaseManager
from db_con import get_db_connection

from demo_page import demo_page
from openCV_method import find_flower_cv
from upload_image import upload_base64_image
from yolo_method import find_flower_yolo

load_dotenv()

app = FastAPI()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
POSTGRES_URL = os.getenv("POSTGRES_URL")

# disable CORS for localhost and direct file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# http request format
class ImageRequest(BaseModel):
    image: str


# DB connection
db_manager = DatabaseManager()

@app.on_event("startup")
async def startup_db():
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME, POSTGRES_URL)

@app.on_event("shutdown")
async def shutdown_db():
    await db_manager.close_all()



# routes
@app.get("/", response_class=HTMLResponse)
async def root():
    return demo_page()



@app.post("/find-flower-cv")
async def find_flower_with_cv(request: ImageRequest):
    try:
        # extract the Base64 part of the input string
        if "," in request.image:
            b64img = request.image.split(",")[1]
        else:
            b64img = request.image

        # call OpenCV method
        result_base64 = find_flower_cv(b64img)

        # return as JSON
        return {"image": f"data:image/png;base64,{result_base64}"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image with cv: {str(e)}")



@app.post("/find-flower-yolo")
async def find_flower_with_yolo(request: ImageRequest):
    try:
        # extract the Base64 part of the input string
        if "," in request.image:
            b64img = request.image.split(",")[1]
        else:
            b64img = request.image

        # call YOLO inference function
        response = find_flower_yolo(b64img)

        # return as JSON
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image with YOLO: {str(e)}")

@app.get("/db-health")
async def health_check():
    health_status = await db_manager.check_health()
    overall_status = "healthy" if all(status == "healthy" for status in health_status.values()) else "unhealthy"
    return JSONResponse(content={"status": overall_status, "details": health_status})

class RoverData(BaseModel):
    initial_id: int
    rover_status: int
    user_id: int

@app.post("/rovers/")
def add_rover(data: RoverData):
    """Route to add a new rover to the database."""
    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # SQL query to insert data into the rovers table
        insert_query = """
        INSERT INTO rovers (initial_id, rover_status, user_id)
        VALUES (%s, %s, %s)
        RETURNING rover_id, created_at;
        """
        
        # Execute the query with provided data
        cursor.execute(insert_query, (data.initial_id, data.rover_status, data.user_id))
        result = cursor.fetchone()
        
        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()
        
        # Return the inserted rover ID and timestamp
        return {"rover_id": result[0], "created_at": result[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add rover: {str(e)}")

# Input model
class Base64ImageInput(BaseModel):
    base64_string: str
    file_extension: str = "png"  # Default to PNG; can be "jpg" or others if needed

@app.post("/upload-image/")
async def upload_image(data: Base64ImageInput):
    try:
        # Call the utility function to upload the base64 image
        blob_url = upload_base64_image(data.base64_string, data.file_extension)
        return {"message": "Image uploaded successfully", "blob_url": blob_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))