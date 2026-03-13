from fastapi import UploadFile

from app.core import AppException, ErrorCode, get_settings


def validate_file_name(file_name: str) -> str:
    """
    Check if the file name extension is valid

    Args:
        file_name: file name with extension

    Returns:
        The input file_name if validate success

    Raises:
        AppException(ErrorCode.FILE_NAME_EXTENSION_ERROR): when file extension
            is not in settings.SUPPORTED_FILE_EXTENSIONS

    """
    settings = get_settings()
    index = file_name.rfind(".")
    if index == -1:
        raise AppException(
            ErrorCode.UNSUPPORTED_FILE_TYPE,
            f"Can not find file extension in filename '{file_name}'",
        )
    extension = file_name[index::]
    if extension not in settings.SUPPORTED_FILE_TYPE:
        raise AppException(
            ErrorCode.UNSUPPORTED_FILE_TYPE,
            f"File extension '{extension}' not supported",
        )
    return file_name


def validate_file(file: UploadFile) -> UploadFile:
    validate_file_name(file.filename)
    return file
