from datetime import datetime
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
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)


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
        raise HTTPException(
            status_code=400, detail=f"Error processing image with cv: {str(e)}")


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
        raise HTTPException(
            status_code=400, detail=f"Error processing image with YOLO: {str(e)}")


@app.get("/db-health")
async def health_check():
    health_status = await db_manager.check_health()
    overall_status = "healthy" if all(
        status == "healthy" for status in health_status.values()) else "unhealthy"
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
        cursor.execute(insert_query, (data.initial_id,
                       data.rover_status, data.user_id))
        result = cursor.fetchone()

        # Commit the transaction and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        # Return the inserted rover ID and timestamp
        return {"rover_id": result[0], "created_at": result[1]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add rover: {str(e)}")

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


@app.post("/rover/trigger/")
async def run_trigger():
    try:
        # Get database connection
        connection = get_db_connection()  # Ensure this supports async if necessary
        cursor = connection.cursor()

        # SQL query to get the count of operations
        get_count_query = "SELECT COUNT(*) FROM operations;"
        cursor.execute(get_count_query)
        result1 = cursor.fetchone()

        if result1 is None or result1[0] <= 0:
            return {"message": "No operations found."}

        count = result1[0]
        for _ in range(count):
            # SQL query to fetch the oldest operation
            get_data_query = """
            SELECT id, rover_id, random_id, battery_status, temp, humidity, 
                   result_image, image_data, created_at
            FROM operations
            WHERE random_id = 1
            ORDER BY created_at ASC
            LIMIT 5;
            """
            cursor.execute(get_data_query)
            result2 = cursor.fetchone()

            if result2 is None:
                break

            # Map query result to ImageData model
            data = ImageData(
                id=result2[0],
                rover_id=result2[1],
                random_id=result2[2],
                battery_status=result2[3],
                temp=result2[4],
                humidity=result2[5],
                result_image=result2[6],
                image_data=result2[7],
                created_at=result2[8],
            )

            # Remove "data:image/png;base64," from result_image string
            updated_result_image = data.result_image.replace(
                "data:image/png;base64,", "")
            blob_url = upload_base64_image(updated_result_image, "jpeg")

            # Add data to MongoDB using db_manager
            mongo_data = {
                "id": data.id,
                "rover_id": data.rover_id,
                "random_id": data.random_id,
                "battery_status": data.battery_status,
                "temp": data.temp,
                "humidity": data.humidity,
                "blob_url": blob_url,
                "image_data": data.image_data,
                "created_at": data.created_at,
            }

            await db_manager.add_to_mongo(mongo_data)

            # Delete the record from PostgreSQL
            delete_data_query = "UPDATE operations SET random_id = 5 WHERE id = %s;"
            cursor.execute(delete_data_query, (data.id))
            # cursor.execute(delete_data_query, (data.id,))

        # Commit the transaction and close the SQL connection
        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "Trigger executed and data added to MongoDB successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run trigger: {str(e)}")
