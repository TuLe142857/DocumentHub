from fastapi import UploadFile
import hashlib
from typing import BinaryIO
def get_file_extension(filename: str) -> str:
    index = filename.rfind(".")
    if index == -1:
        raise ValueError(f"Can not find extension in filename '{filename}'")
    return filename[index::]

def sha256_checksum(file: BinaryIO) -> str:
    sha256 = hashlib.sha256()
    while chunk := file.read(1024*1024):
        sha256.update(chunk)
    file.seek(0)
    return sha256.hexdigest()

def md5_checksum(file: BinaryIO) -> str:
    md5 = hashlib.md5()
    while chunk := file.read(1024*1024):
        md5.update(chunk)
    file.seek(0)
    return md5.hexdigest()