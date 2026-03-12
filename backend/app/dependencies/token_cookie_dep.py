from typing import Annotated, Any

from fastapi import Depends, Request

from app.core import AppException, ErrorCode, get_settings

from .service_dep import JWTServiceDep


class JWTCookie:
    """
    Use like a class Dependencies to decode & validate JWT tokens from request cookies.

    Example:
        @router.get("/require_jwt_token")
        def func(
            jwt_access_payload: Annotated[dict, Depends(JWTCookie(fresh=True))],
            jwt_refresh_payload: Annotated[dict, Depends(JWTCookie(refresh=True))],
        ):
            pass
    """

    def __init__(
        self, refresh: bool = False, optional: bool = False, fresh: bool = False
    ):
        """
        Use like a class Dependencies to decode & validate JWT tokens from request cookies.
        Args:
            refresh (bool): if True token is refresh_token, else token is access_token
            optional: if True return None when cookie not provided, otherwise raise AppException.
            fresh: Use for access_token only, if True access_token mus be fresh(if not fresh raises AppException).
        """
        if refresh and fresh:
            raise ValueError("fresh can only be used with access tokens")

        self.refresh: bool = refresh
        self.optional: bool = optional
        self.fresh: bool = fresh

    def __call__(
        self, request: Request, jwt_service: JWTServiceDep
    ) -> dict[str, Any] | None:
        """
        Validates JWT token from request cookies and return payload as dict.
        If request cookies not provided and optional=False, raise AppException.
        Args:
            request: fastapi request object(auto injected as dependency by fastapi)
            jwt_service: jwt service object(auto injected as dependency by fastapi)

        Returns: payload as dict.

        """
        if self.refresh:
            refresh_token = request.cookies.get(get_settings().JWT_REFRESH_COOKIE_NAME)
            if not refresh_token:
                if self.optional:
                    return None
                else:
                    raise AppException(
                        ErrorCode.UNAUTHORIZED, "Require JWT Refresh Cookie"
                    )
            return jwt_service.validate_refresh_token(refresh_token)
        else:
            access_token = request.cookies.get(get_settings().JWT_ACCESS_COOKIE_NAME)
            if not access_token:
                if self.optional:
                    return None
                else:
                    raise AppException(
                        ErrorCode.UNAUTHORIZED,
                        "Require JWT Access Cookie" + type(access_token).__name__,
                    )
            return jwt_service.validate_access_token(
                access_token, require_fresh=self.fresh
            )


# Require access token
AccessTokenDep = Annotated[dict[str, Any], Depends(JWTCookie())]

# Require fresh access token
FreshAccessTokenDep = Annotated[dict[str, Any], Depends(JWTCookie(fresh=True))]

# Access token payload or None
OptionalAccessTokenDep = Annotated[
    dict[str, Any] | None, Depends(JWTCookie(optional=True))
]

# Require refresh token
RefreshTokenDep = Annotated[dict[str, Any], Depends(JWTCookie(refresh=True))]
