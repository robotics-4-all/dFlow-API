import base64
import os
from typing import Optional, Dict

import docker
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.dmodel import DModelRepository
from app.db.repositories.user import UserRepository

from app.models.user import UserInDB
from app.models.dmodel import DModelInsert, DModelInDB, DModelPublic


from app.services import dflow_service

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Path,
    UploadFile,
    status
)
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY
)
from fastapi.responses import FileResponse


router = APIRouter()


@router.post("/validation/file",
             response_model=Dict,
             name="validation:validate_mode_file",
             status_code=HTTP_201_CREATED
             )
async def validate_model_file(
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    print(f'Validation for request: file=<{model_file.filename}>,' + \
          f' descriptor=<{model_file.file}>')
    resp = {
        'status': 200,
        'message': ''
    }
    fd = model_file.file
    try:
        dflow_service.validate_model(fd)
    except Exception as e:
        resp['status'] = 404
        resp['message'] = str(e)
    return resp


@router.post("/validation/b64",
             response_model=Dict,
             name="validation:validate_model_b64",
             status_code=HTTP_201_CREATED
             )
async def validate_model_b64(
    fenc: str = '',
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    if len(fenc) == 0:
        return 404
    resp = {
        'status': 200,
        'message': ''
    }
    fdec = base64.b64decode(fenc)
    try:
        dflow_service.validate_model(fdec)
    except Exception as e:
        resp['status'] = 404
        resp['message'] = e
    return resp


@router.post("/codegen/file",
             response_class=FileResponse,
             name="codegen:gen_from_file",
             status_code=HTTP_201_CREATED
             )
async def gen_from_file(
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    print(f'Generate for request: file=<{model_file.filename}>,' + \
          f' descriptor=<{model_file.file}>')
    fd = model_file.file
    tarball_path = dflow_service.generate(fd)
    return FileResponse(tarball_path,
                        filename=os.path.basename(tarball_path),
                        media_type='application/x-tar')


@router.post("/model",
             # response_class=Dict,
             name="model:store_model",
             status_code=HTTP_201_CREATED
             )
async def store_model(
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    fd = model_file.file
    model_raw = dflow_service.unpack_model_from_file(fd)
    user_id = current_user.id
    print(user_id)
    print(model_raw)

    return 501
#
#
# @router.get("/model/{id}",
#             response_class=Dict,
#             name="model:get_model_by_id",
#             status_code=HTTP_200_OK
#             )
# async def get_model_by_id(
#     id: str,
#     current_user: UserInDB = Depends(get_current_active_user)
#     ):
#     print(f'Generate for request: file=<{model_file.filename}>,' + \
#           f' descriptor=<{model_file.file}>')
#     fd = model_file.file
#
#     return 501
