from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from database import DatabaseManager
from db_manager import get_db_manager

router = APIRouter()

@router.get("/db-health")
async def health_check(db_manager: DatabaseManager = Depends(get_db_manager)):
    health_status = await db_manager.check_health()
    overall_status = "healthy" if all(status == "healthy" for status in health_status.values()) else "unhealthy"

    return JSONResponse(content={
        "status": overall_status,
        "details": health_status
    })
