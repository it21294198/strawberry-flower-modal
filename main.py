import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from dotenv import load_dotenv

from database import DatabaseManager
from demo_page import demo_page
from openCV_method import find_flower_cv
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
