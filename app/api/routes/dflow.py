import base64
import os
from typing import Optional, Dict

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
             status_code=HTTP_200_OK
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
             status_code=HTTP_200_OK
             )
async def validate_model_b64(
    fenc: str = '',
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    resp = {
        'status': 200,
        'message': ''
    }
    fdec = base64.b64decode(fenc)
    try:
        dflow_service.validate_model_b64(fdec)
    except Exception as e:
        resp['status'] = 404
        resp['message'] = str(e)
        print(e)
    return resp


@router.post("/codegen/file",
             response_class=FileResponse,
             name="codegen:gen_from_file",
             status_code=HTTP_200_OK
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


@router.post("/codegen/b64",
             response_class=FileResponse,
             name="codegen:gen_model_b64",
             status_code=HTTP_200_OK
             )
async def gen_model_b64(
    fenc: str = '',
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    fdec = base64.b64decode(fenc)
    try:
        tarball_path = dflow_service.generate_b64(fdec)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"{str(e)}",
        )
    return FileResponse(tarball_path,
                        filename=os.path.basename(tarball_path),
                        media_type='application/x-tar')


@router.post("/model",
             # response_class=Dict,
             name="model:store_model",
             status_code=HTTP_200_OK
             )
async def store_model(
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    fd = model_file.file
    model_raw = dflow_service.unpack_model_from_file(fd)
    user_id = current_user.id
    dmodel = await dmodel_repo.add_model_for_user(user_id=user_id,
                                                  model_raw=model_raw)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User profile does not exist",
        )


@router.post("/model/b64",
             # response_class=Dict,
             name="model:store_model_b64",
             status_code=HTTP_200_OK
             )
async def store_model_b64(
    fenc: str = '',
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    model_raw = base64.b64decode(fenc)
    user_id = current_user.id
    dmodel = await dmodel_repo.add_model_for_user(user_id=user_id,
                                                  model_raw=model_raw)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User profile does not exist",
        )


@router.get("/model/{model_id}",
            # response_class=DModelPublic,
            name="model:get_model_by_id",
            status_code=HTTP_200_OK
            )
async def get_model_by_id(
    model_id: int,
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ) -> DModelPublic:
    dmodel = await dmodel_repo.get_model_by_id(model_id=model_id)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User profile does not exist",
        )
    # print(dmodel)
    resp = DModelPublic(**dmodel.dict())
    return resp


@router.get("/merge",
            response_class=FileResponse,
            name="model:merge_models",
            status_code=HTTP_200_OK
            )
async def merge_models(
    user_repo: UserRepository = Depends(get_repository(UserRepository)),
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ) -> FileResponse:
    users = await user_repo.get_users()
    models = []
    for user in users:
        username = dict(user.items())['username']
        dmodel = await dmodel_repo.get_last_model_for_user(username=username)
        if dmodel is not None:
            models.append(dmodel)
    merged_model = dflow_service.merge(models)
    if not len(models):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Model storage is empty!",
        )
    return FileResponse(
        merged_model,
        filename=os.path.basename(merged_model)
    )


@router.delete("/model/{model_id}",
               # response_class=DModelPublic,
               name="model:delete_model_by_id",
               status_code=HTTP_200_OK
               )
async def delete_model_by_id(
    model_id: int,
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    dmodel = await dmodel_repo.delete_model_by_id(model_id=model_id)
    return 200


@router.get("/model/{model_id}/file",
            response_class=FileResponse,
            name="model:get_model_by_id",
            status_code=HTTP_200_OK
            )
async def get_model_file_by_id(
    model_id: int,
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ) -> FileResponse:

    dmodel = await dmodel_repo.get_model_by_id(model_id=model_id)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="",
        )
    model_file = dflow_service.store_model_file_tmp(dmodel.raw, dmodel.id)

    return FileResponse(model_file,
                        filename=os.path.basename(model_file))


@router.get("/user/{username}/model/last",
            # response_class=DModelPublic,
            name="model:get_last_model_for_user",
            status_code=HTTP_200_OK
            )
async def get_last_model_for_user(
    username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$"),
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ) -> DModelPublic:

    dmodel = await dmodel_repo.get_last_model_for_user(username=username)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Model does not exist",
        )
    return DModelPublic(**dmodel.dict())


@router.get("/user/{username}/model/last/file",
            response_class=FileResponse,
            name="model:get_last_model_file_for_user",
            status_code=HTTP_200_OK
            )
async def get_last_model_file_for_user(
    username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9_-]+$"),
    dmodel_repo: DModelRepository = Depends(get_repository(DModelRepository)),
    current_user: UserInDB = Depends(get_current_active_user)
    ) -> FileResponse:

    dmodel = await dmodel_repo.get_last_model_for_user(username=username)
    if not dmodel:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Model does not exist",
        )
    model_file = dflow_service.store_model_file_tmp(dmodel.raw, dmodel.id)

    return FileResponse(model_file,
                        filename=os.path.basename(model_file))
