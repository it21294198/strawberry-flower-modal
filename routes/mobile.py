import json
from datetime import datetime
from typing import List, Dict

import httpx
from fastapi import APIRouter, HTTPException, status, Depends

from config import RUST_ROVER_REGISTRATION_URL
from database import DatabaseManager
from db_manager import get_db_manager
from models.schemas import RoverPollinationData, FlowerCountSummary
from models.userSchemas import UserModel

router = APIRouter()



# Create user route
@router.post("/users/", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel, db_manager: DatabaseManager = Depends(get_db_manager)):
    if db_manager.mongo_manager.db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB connection is not established"
        )
    print("MongoDB connection is established.")

    # Ensure email uniqueness
    existing_user = await db_manager.mongo_manager.db['users'].find_one({'email': user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    print("Email uniqueness OK")

    # generate ID
    user_id = await generate_unique_user_id(db_manager)
    print(f"Unique userId Ok: {user_id}")
    user.userId = user_id

    # Add the created_at and updated_at
    user.created_at = datetime.now()
    user.updated_at = user.created_at

    # Insert the new user into the database
    await db_manager.mongo_manager.db['users'].insert_one(user.model_dump())
    return user



# Get user by email route
@router.get("/users/email/{email}", response_model=UserModel)
async def get_user_by_email(email: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    user = await db_manager.mongo_manager.db['users'].find_one({'email': email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user



# Get user by userId route
@router.get("/users/user-id/{userId}", response_model=UserModel)
async def get_user_by_user_id(userId: int, db_manager: DatabaseManager = Depends(get_db_manager)):
    user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user



# Get user by username route
@router.get("/users/username/{username}", response_model=UserModel)
async def get_user_by_username(username: str, db_manager: DatabaseManager = Depends(get_db_manager)):
    user = await db_manager.mongo_manager.db['users'].find_one({'username': username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user



# Update roverIds route
# @router.put("/users/{userId}/roverIds", response_model=UserModel)
# async def update_rover_ids(userId: int, roverIds: List[int], db_manager: DatabaseManager = Depends(get_db_manager)):
#     user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#
#     # Update the roverIds and set the updated_at timestamp
#     updated_user = user
#     updated_user['roverIds'] = roverIds
#     updated_user['updated_at'] = datetime.now()
#
#     # Replace the user in the database
#     await db_manager.mongo_manager.db['users'].replace_one({'userId': userId}, updated_user)
#
#     return updated_user



# register rover
@router.put("/users/{userId}/register-rover", response_model=UserModel)
async def register_rover(userId: int, db_manager: DatabaseManager = Depends(get_db_manager)):
    user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


    payload = {
        "roverId": 12345,
        "initialId": 12345,
        "roverStatus": 12345,
        "userId": userId
    }

    # make API call to rust server
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(RUST_ROVER_REGISTRATION_URL, json=payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Rust API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Request error: {str(e)}"
            )

    # Extract `info` and convert to integer
    try:
        if data: print("rust data okay")
        rover_id = int(data.get("info", 0))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid response format from Rust API"
        )

    # Update the user's `rovers` array in MongoDB
    await db_manager.mongo_manager.db['users'].update_one(
        {"userId": userId},
        {"$push": {"rovers": {"roverId": rover_id, "nickname": f"Rover-{rover_id}"}}}
    )

    # Fetch and return the updated user document
    updated_user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found after update"
        )

    return updated_user



# update rover nickname
@router.put("/users/{userId}/rovers/{roverId}/update-nickname", response_model=UserModel)
async def update_rover_nickname(
        userId: int,
        roverId: int,
        nickname: str,
        db_manager: DatabaseManager = Depends(get_db_manager),
):
    user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if the rover belongs to the user
    rover = next((r for r in user.get("rovers", []) if r["roverId"] == roverId), None)
    if not rover:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rover does not belong to this user"
        )

    # Update the rover's nickname
    await db_manager.mongo_manager.db['users'].update_one(
        {"userId": userId, "rovers.roverId": roverId},
        {"$set": {"rovers.$.nickname": nickname}}
    )

    # Fetch and return the updated user document
    updated_user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found after update"
        )

    return updated_user



# get all pollination count of a user's rovers' in a given time rage
@router.get("/users/{userId}/get-flower-count", response_model=FlowerCountSummary)
async def get_flower_count_in_range(
        userId: int,
        start_date: datetime,
        end_date: datetime,
        db_manager=Depends(get_db_manager)
):
    # Fetch user from MongoDB
    user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Extract rover IDs
    rovers = user.get("rovers", [])
    rover_ids = [rover["roverId"] for rover in rovers]

    if not rover_ids:
        return FlowerCountSummary(net_count=0, by_rover=[])

    # Query the operations collection for matching rover data
    operations_cursor = db_manager.mongo_manager.db['operations'].find({
        "rover_id": {"$in": rover_ids},
        "created_at": {"$gte": start_date, "$lte": end_date}
    })

    operations = await operations_cursor.to_list(None)

    # Process flower counts per rover
    rover_counts: Dict[int, int] = {}
    for operation in operations:
        rover_id = operation["rover_id"]
        image_data = operation.get("image_data", "[]")
        flower_count = count_flower_points_from_jason_string(json.dumps(image_data))
        rover_counts[rover_id] = rover_counts.get(rover_id, 0) + flower_count

    # Prepare response data
    pollination_data = [
        RoverPollinationData(rover_id=rover["roverId"],
                             rover_nickname=rover["nickname"],
                             flower_count=rover_counts.get(rover["roverId"], 0))
        for rover in rovers
    ]

    net_count = sum(rover_counts.values())

    return FlowerCountSummary(net_count=net_count, by_rover=pollination_data)



###

# generate a unique userId
async def generate_unique_user_id(db_manager: DatabaseManager):
    while True:
        user_id = int(datetime.now().timestamp() * 1000)  # Generate current time in milliseconds

        # Check if the userId exists in the database
        existing_user = await db_manager.mongo_manager.db['users'].find_one({'userId': user_id})

        if not existing_user:
            return user_id  # Return unique userId if not found
        else:
            # Regenerate userId if it already exists
            continue


# Parse the JSON string into a Python list and get count
def count_flower_points_from_jason_string(image_data):
    points = json.loads(image_data)
    return len(points)
