import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from db_con import get_db_connection
from demo_page import demo_page
from openCV_method import find_flower_cv
from yolo_method import find_flower_yolo

app = FastAPI()

# disable CORS for localhost and direct file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# check and make directories
# os.makedirs("cv_processed_img", exist_ok=True)
# os.makedirs("yolo_processed_img", exist_ok=True)

# http request format
class ImageRequest(BaseModel):
    image: str


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