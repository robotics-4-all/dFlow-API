import subprocess
import tarfile
import os

from dflow.utils import build_model


class Dflow(BaseException):
    pass


class DflowService:
    TMP_DIR = '/tmp/goaldsl'

    def validate_model(self, fd) -> bool:
        u_id = uuid.uuid4().hex[0:8]
        fpath = os.path.join(
            DflowService.TMP_DIR,
            f'model_for_validation-{u_id}.dflow'
        )
        with open(fpath, 'w') as f:
            f.write(fd.read().decode('utf8'))

    def run_subprocess(self, exec_path):
        pid = subprocess.Popen(['python3', exec_path], close_fds=True)
        return pid

    def make_tarball(self, fout, source_dir):
        with tarfile.open(fout, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))

    def generate(self, fd):
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
        self.make_tarball(tarball_path, out_dir)
        return tarball_path
