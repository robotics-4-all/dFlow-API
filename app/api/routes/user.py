from fastapi import Depends, APIRouter, HTTPException, Path, Body

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository

from app.models.user import UserCreate, UserPublic, UserInDB
from app.models.profile import UserProfilePublic
from app.db.repositories.user import UserRepository

from app.models.token import AccessToken
from app.services import auth_service


router = APIRouter()


@router.post("/user",
             response_model=UserPublic,
             name="user:register-new-user",
             status_code=HTTP_201_CREATED)
async def register_new_user(
    new_user: UserCreate = Body(..., embed=True),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
    ) -> UserPublic:
    created_user = await user_repo.register_new_user(new_user=new_user)
    return created_user


@router.post("/user/login",
             response_model=AccessToken,
             name="user:login")
async def user_login(
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    ) -> AccessToken:
    username = form_data.username
    password = form_data.password
    user = await user_repo.authenticate_user(
        username=username, password=password)

    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Authentication was unsuccessful.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = AccessToken(
        access_token=auth_service.create_access_token_for_user(user=user),
        token_type="bearer"
    )
    return access_token


@router.get("/user/me",
            response_model=UserPublic,
            name="user:get-current-user")
async def get_currently_authenticated_user(
    current_user: UserInDB = Depends(get_current_active_user)) -> UserPublic:
    return current_user


@router.get("/user/{username}",
            response_model=UserPublic,
            name="user:get-user")
async def get_user(
    username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$"),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserPublic:
    user = await user_repo.get_user_by_username(username=username)
    if not user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User does not exist",
        )
    return user


@router.get("/user/{username}/profile",
            response_model=UserProfilePublic,
            name="user:get-user-profile")
async def get_user_profile(
    username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$"),
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
) -> UserProfilePublic:
    profile = await user_repo.profiles_repo.get_profile_by_username(username=username)
    if not profile:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User profile does not exist",
        )
    up = UserProfilePublic(**profile.dict())
    return up
