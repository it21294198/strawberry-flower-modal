from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends

from database import DatabaseManager
from db_manager import get_db_manager
from models.userSchemas import UserModel

router = APIRouter()



# Create user route
@router.post("/users/", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserModel, db_manager: DatabaseManager = Depends(get_db_manager)):
    # Ensure email uniqueness
    existing_user = await db_manager.mongo_manager.db['users'].find_one({'email': user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    print("Email uniqueness OK")

    # generate ID
    user_id = await generate_unique_user_id()
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
@router.put("/users/{userId}/roverIds", response_model=UserModel)
async def update_rover_ids(userId: int, roverIds: List[int], db_manager: DatabaseManager = Depends(get_db_manager)):
    user = await db_manager.mongo_manager.db['users'].find_one({'userId': userId})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update the roverIds and set the updated_at timestamp
    updated_user = user
    updated_user['roverIds'] = roverIds
    updated_user['updated_at'] = datetime.now()

    # Replace the user in the database
    await db_manager.mongo_manager.db['users'].replace_one({'userId': userId}, updated_user)

    return updated_user



###

# generate a unique userId
async def generate_unique_user_id(db_manager: DatabaseManager = Depends(get_db_manager)):
    while True:
        user_id = int(datetime.now().timestamp() * 1000)  # Generate current time in milliseconds

        # Check if the userId exists in the database
        existing_user = await db_manager.mongo_manager.db['users'].find_one({'userId': user_id})

        if not existing_user:
            return user_id  # Return unique userId if not found
        else:
            # Regenerate userId if it already exists
            continue