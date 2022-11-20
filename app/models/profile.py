from typing import Optional

from pydantic import EmailStr, constr, HttpUrl

from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from app.models.token import AccessToken


class UserProfileBase(CoreModel):
    full_name: Optional[str]
    phone_number: Optional[str]
    bio: Optional[str]
    image: Optional[HttpUrl]


class UserProfileCreate(UserProfileBase):
    """
    The only field required to create a profile is the users id
    """

    user_id: int


class UserProfileUpdate(UserProfileBase):
    """
    Allow users to update any or no fields, as long as it's not user_id
    """

    pass


class UserProfileInDB(IDModelMixin, DateTimeModelMixin, UserProfileBase):
    user_id: int
    username: Optional[str]
    email: Optional[EmailStr]


class UserProfilePublic(UserProfileInDB):
    pass
