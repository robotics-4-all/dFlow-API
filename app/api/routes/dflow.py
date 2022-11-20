import base64
import os
import subprocess
import tarfile
import uuid
from typing import Optional

import docker
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.user import UserRepository
from app.models.profile import UserProfilePublic
from app.models.token import AccessToken
from app.models.user import UserCreate, UserInDB, UserPublic
from app.services import auth_service
from fastapi import (APIRouter, Body, Depends, File, HTTPException, Path,
                     UploadFile, status)
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import (HTTP_200_OK, HTTP_201_CREATED,
                              HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                              HTTP_404_NOT_FOUND,
                              HTTP_422_UNPROCESSABLE_ENTITY)


docker_client = docker.from_env()

TMP_DIR = '/tmp/goaldsl'

router = APIRouter()


@router.post("/validation/file",
             response_model=UserPublic,
             name="validation:validate_mode_file",
             status_code=HTTP_201_CREATED
             )
async def validate_model_file(
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    print(f'Validation for request: file=<{file.filename}>,' + \
          f' descriptor=<{file.file}>')
    resp = {
        'status': 200,
        'message': ''
    }
    fd = file.file
    u_id = uuid.uuid4().hex[0:8]
    fpath = os.path.join(
        TMP_DIR,
        f'model_for_validation-{u_id}.dflow'
    )
    with open(fpath, 'w') as f:
        f.write(fd.read().decode('utf8'))
    try:
        #
        # TODO here!!
        ##
        pass
    except Exception as e:
        resp['status'] = 404
        resp['message'] = e
    return resp


@router.post("/validation/b64",
             response_model=UserPublic,
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
    u_id = uuid.uuid4().hex[0:8]
    fpath = os.path.join(
        TMP_DIR,
        'model_for_validation-{}.dflow'.format(u_id)
    )
    with open(fpath, 'wb') as f:
        f.write(fdec)
    try:
        # model, _ = build_model(fpath)
        #
        # TODO here!!
        ##
        pass
    except Exception as e:
        resp['status'] = 404
        resp['message'] = e
    return resp


@router.post("/codegen/file",
             response_model=UserPublic,
             name="codegen:gen_from_file",
             status_code=HTTP_201_CREATED
             )
async def gen_from_file(
    model_file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
    ):
    print(f'Generate for request: file=<{model_file.filename}>,' + \
          f' descriptor=<{model_file.file}>')
    resp = {
        'status': 200,
        'message': ''
    }
    fd = model_file.file
    u_id = uuid.uuid4().hex[0:8]
    model_path = os.path.join(
        TMP_DIR,
        f'model-{u_id}.dflow'
    )
    tarball_path = os.path.join(
        TMP_DIR,
        f'{u_id}.tar.gz'
    )
    gen_path = os.path.join(
        TMP_DIR,
        f'gen-{u_id}'
    )
    with open(model_path, 'w') as f:
        f.write(fd.read().decode('utf8'))
    try:
        # out_dir = generate_model(model_path, gen_path)
        #
        # TODO here!!
        ##
        make_tarball(tarball_path, out_dir)
        print(f'Sending tarball {tarball_path}')
        return FileResponse(tarball_path,
                            filename=os.path.basename(tarball_path),
                            media_type='application/x-tar')
    except Exception as e:
        print(e)
        resp['status'] = 404
        return resp


def run_subprocess(exec_path):
    pid = subprocess.Popen(['python3', exec_path], close_fds=True)
    return pid


def make_tarball(fout, source_dir):
    with tarfile.open(fout, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
