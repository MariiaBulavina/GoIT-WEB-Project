import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.database.models import User, UserRole
from src.services.auth import auth_service
from src.services.roles import RoleAccess
from src.schemas.users import UserDb, UserResponse, Action, UserProfile
from src.database.db import get_db
from src.conf.config import settings
from src.repository import users as repositories_users
from src.repository import posts as posts_repository
from src.schemas.posts import PostResponse

router = APIRouter(prefix='/users', tags=['users'])

access_to_routes = RoleAccess([UserRole.admin, UserRole.moderator])

cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )


@router.get('/me', response_model=UserDb)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Current user
    :return: The user object
    """
    return user


@router.patch('/me', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(...), user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The update_avatar_user function updates the avatar of a user.

    :param file: UploadFile: Image for a new avatar 
    :param user: User: Current user
    :param db: Session: Connection to the database
    :return: User: The updated user
    """
    public_id = f'FastApiApp/{user.email}'
    res = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=res.get('version'))

    user =  await repositories_users.update_avatar_url(user.email, res_url, db)

    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    
    return user


@router.get('/', response_model=UserProfile)
async def get_user_profile(username: str, db: Session = Depends(get_db)) -> User:
    """
    Function to get user profile.

    :param username: str: User name
    :param db: Session: Connection to the database
    :return: User object
    """
    found_user = await repositories_users.get_user_by_username(username, db)
    
    if found_user:
        user = await repositories_users.get_user_profile(found_user, db)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    

@router.get('/{user_id}', response_model=UserProfile)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db), user: User = Depends(auth_service.get_current_user)) -> User:
    """
    Function to get user profile.

    :param user_id: int: User id
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: User object
    """
    found_user = await repositories_users.get_user_by_id(user_id, db)
    if found_user:
        user = await repositories_users.get_user_profile(found_user, db)
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


@router.patch('/{user_id}', dependencies=[Depends(access_to_routes)], response_model=UserResponse)
async def manage_user(user_id: int, action: Action, role: UserRole = UserRole.user, user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    Function to manage a user's role or ban status.

    :param user_id: int: id of the user to manage
    :param action: Action: The action to perform. This can be 'change_user_role', 'ban', or 'unban'
    :param role: UserRole, optional: The new role to assign to the user
    :param user: User: The currently authenticated user
    :param db: Session: The database session
    :return: UserResponse

    """
    user_to_change = await repositories_users.get_user_by_id(user_id, db)

    if not user_to_change:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if action == Action.change_user_role:

        if user.user_role == UserRole.admin:

            if role is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You must specify a new role')

            changed_user = await repositories_users.change_role(user_to_change.email, role, db)
            return {'user': changed_user, 'detail': f'User has been changed to {role}'}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission')

    elif action == Action.ban:

        if user.user_role == UserRole.admin or user.user_role == UserRole.moderator:

            if user_to_change.is_active:

                changed_user = await repositories_users.ban_user(user_to_change.email, db)
                return {'user': changed_user, 'detail': 'User has been banned'}
            else: 
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The user is already banned')
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission')
        
    elif action == Action.unban:

        if user.user_role == UserRole.admin:

            if not user_to_change.is_active:

                changed_user = await repositories_users.unban_user(user_to_change.email, db)
                return {'user': changed_user, 'detail': 'User has been unbanned'}
            else: 
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The user is already active')
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission')
        

@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Function to get posts belonging to the current user.

    :param user_id: int: Post author id
    :param request: Request: HTTP request
    :param db: Session: Connection to the database
    :param user: User: The currently authenticated user
    :return: list[PostResponse]: List of posts
    """
    return await posts_repository.get_user_posts(user_id=user_id, db=db)
