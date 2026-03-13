from app.core import AppException, ErrorCode


def validate_tag_name(tag_name: str) -> str:
    tag_name = tag_name.strip()
    if " " in tag_name:
        raise AppException(
            ErrorCode.VALIDATION_ERROR, f"Tag name cannot contain spaces {tag_name}"
        )
    if not tag_name.islower():
        raise AppException(
            ErrorCode.VALIDATION_ERROR, "Tag name cannot contain uppercase"
        )
    return tag_name


def validate_tag_name_list(tag_names: list[str]) -> list[str]:
    return [validate_tag_name(_) for _ in tag_names]
