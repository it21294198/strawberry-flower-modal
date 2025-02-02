from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import MONGO_URI, MONGO_DB_NAME
from database import DatabaseManager
from demo_page import demo_page
from routes import flower, health, rover

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(flower.router)
app.include_router(health.router)
app.include_router(rover.router)

# DB connection
db_manager = DatabaseManager()

@app.on_event("startup")
async def startup_db():
    await db_manager.connect_all(MONGO_URI, MONGO_DB_NAME)

@app.on_event("shutdown")
async def shutdown_db():
    await db_manager.close_all()

@app.get("/", response_class=HTMLResponse)
async def root():
    return demo_page()