from typing import Any, Callable
from urllib.parse import urlparse

from app.dependencies import get_s3


def validate_s3_url(
    bucket: str,
    expires_in: int = 5 * 60,
    extra_params: dict[str, Any] | None = None,
    base_url: str | None = None,
) -> Callable[[str], str]:
    """Factory to create a Pydantic validator that converts S3 keys to presigned URLs.

    Args:
        bucket: The name of the S3 bucket.
        expires_in: Expiration time of the generated presigned URL in seconds.
        extra_params: Optional additional parameters passed to `s3.generate_presigned_url`.
            The parameters `Bucket` and `Key` cannot be overridden.
        base_url: Optional base URL to override the domain in the generated presigned URL.

    Returns:
        A function that takes an object key and returns a presigned URL.
    """

    params = extra_params if (extra_params is not None) else dict()
    params["Bucket"] = bucket

    def validate_function(key: str) -> str:
        s3 = get_s3()
        params["Key"] = key
        url = s3.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires_in,
        )
        if base_url is not None:
            parsed_url = urlparse(url)
            final_url = base_url + parsed_url.path + "?" + parsed_url.query
            return final_url
        return url

    return validate_function
