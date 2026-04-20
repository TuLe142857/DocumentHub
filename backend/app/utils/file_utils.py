import hashlib
from typing import BinaryIO

import fitz


def get_file_extension(filename: str) -> str:
    """
    Args:
        filename:

    Returns:
        file extension (include '.')

    Raises:
        ValueError: can not find the file extension in filename

    Examples:
        >>> get_file_extension("test.pdf")
        >>> ".pdf"
    """
    index = filename.rfind(".")
    if index == -1:
        raise ValueError(f"Can not find extension in filename '{filename}'")
    return filename[index::]


def sha256_checksum(file: BinaryIO) -> str:
    """
    Automatic seek file cursor to 0 after complete.
    Args:
        file:
    Returns:
        sha256 checksum(hex digit) as string

    """
    sha256 = hashlib.sha256()
    while chunk := file.read(1024 * 1024):
        sha256.update(chunk)
    file.seek(0)
    return sha256.hexdigest()


def md5_checksum(file: BinaryIO) -> str:
    """
    Automatic seek file cursor to 0 after complete.
    Args:
        file:
    Returns:
        md5 checksum(hex digit) as string
    """
    md5 = hashlib.md5()
    while chunk := file.read(1024 * 1024):
        md5.update(chunk)
    file.seek(0)
    return md5.hexdigest()


def extract_pdf_thumbnail(pdf_bytes: bytes, *, img_format: str = "png") -> bytes:
    """
    Extract thumbnail from PDF file
    Args:
        pdf_bytes:
        img_format:

    Returns:
        image as a bytes object
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img_bytes = pix.tobytes(img_format)
    doc.close()
    return img_bytes


def count_pdf_pages(pdf_bytes: bytes) -> int:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = doc.page_count
    doc.close()
    return page_count
