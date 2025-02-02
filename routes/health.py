from fastapi import APIRouter
from fastapi.responses import JSONResponse
from database import DatabaseManager

router = APIRouter()
db_manager = DatabaseManager()

@router.get("/db-health")
async def health_check():
    health_status = await db_manager.check_health()
    overall_status = "healthy" if all(status == "healthy" for status in health_status.values()) else "unhealthy"

    return JSONResponse(content={
        "status": overall_status,
        "details": health_status
    })
