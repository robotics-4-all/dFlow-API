import subprocess
import tarfile
import uuid
import os

from dflow.utils import build_model
from dflow.generator import codegen


class Dflow(BaseException):
    pass


class DflowService:
    TMP_DIR = '/tmp/dflow'

    def __init__(self):
        if not os.path.exists(DflowService.TMP_DIR):
            os.mkdir(DflowService.TMP_DIR)


    def validate_model(self, fd):
        u_id = uuid.uuid4().hex[0:8]
        fpath = os.path.join(
            DflowService.TMP_DIR,
            f'model_for_validation-{u_id}.dflow'
        )
        with open(fpath, 'w') as f:
            f.write(fd.read().decode('utf8'))
        model, _ = build_model(fpath)

    def validate_model_b64(self, model_b64):
        u_id = uuid.uuid4().hex[0:8]
        fpath = os.path.join(
            DflowService.TMP_DIR,
            f'model_for_validation-{u_id}.dflow'
        )
        with open(fpath, 'wb') as f:
            f.write(model_b64)
        model, _ = build_model(fpath)

    def run_subprocess(self, exec_path):
        pid = subprocess.Popen(['python3', exec_path], close_fds=True)
        return pid

    def make_tarball(self, fout, source_dir):
        with tarfile.open(fout, "w:gz") as tar:
            tar.add(source_dr, arcname=os.path.basename(source_dir))

    def generate(self, fd):
        u_id = uuid.uuid4().hex[0:8]
        model_path = os.path.join(
            DflowService.TMP_DIR,
            f'model-{u_id}.dflow'
        )
        tarball_path = os.path.join(
            DflowService.TMP_DIR,
            f'{u_id}.tar.gz'
        )
        gen_path = os.path.join(
            DflowService.TMP_DIR,
            f'gen-{u_id}'
        )
        with open(model_path, 'w') as f:
            f.write(fd.read().decode('utf8'))
        out_dir = codegen(model_path, output_path=gen_path)
        self.make_tarball(tarball_path, out_dir)
        return tarball_path

    def unpack_model_from_file(self, fd):
        return fd.read().decode('utf8')

    def store_model_file_tmp(self, model_raw, model_id):
        gen_path = os.path.join(
            DflowService.TMP_DIR,
            f'dmodel-{model_id}.dflow'
        )
        with open(gen_path, 'w') as f:
            f.write(model_raw)
        return gen_path

    def merge(self, source_files, model_id):
        sections = ['entities', 'synonyms', 'gslots', 'triggers', 'dialogues', 'eservices']
        merged_strings = {k: '' for k in sections}

        for fd in source_files:
            data = self.unpack_model_from_file(fd)

            # Use list os sections to find keywords in file
            indexes = []
            for section in sections:
                i = data.find(section)
                indexes.append(i)
            # Sort sections based on appearance in file
            indexes, sections = zip(*sorted(zip(indexes, sections)))

            # Extract each section in reverse order
            for i in reversed(range(len(indexes))):
                ind = indexes[i]
                # ind == -1 if keyword doesn't exist in data
                if ind >= 0:
                    part = data[ind:]
                    data = data[:ind]
                    end_i = part.rfind('end')
                    merged_strings[sections[i]] += part[len(sections[i]):end_i]

        # Add section name the begining and 'end' in the end of each section
        for section in merged_strings:
            merged_strings[section] = section + merged_strings[section] + '\nend'

        gen_path = os.path.join(
            DflowService.TMP_DIR,
            f'dmodel-{model_id}.dflow'
        )
        with open(gen_path, 'w') as f:
            f.write(merged_strings)
        return gen_path
