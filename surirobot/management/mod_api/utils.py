import os
import uuid

base_dir = './pictures'


def save_file(file):
    path = os.path.join(base_dir, str(uuid.uuid4()) + '.jpg')
    file.save(path)
    return path


def delete_file(path):
    os.remove(path)
