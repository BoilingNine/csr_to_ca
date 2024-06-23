from typing import Dict, Any, Optional

from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import status

from utils.exceptions import CSRException


class CAFastAPI(FastAPI):
    """
    FastAPI application for the patient managements And Delete 422 rsp code.
    """

    def openapi(self) -> Dict[str, Any]:
        self.openapi_schema = super().openapi()
        for _, method_item in self.openapi_schema.get('paths').items():
            for _, param in method_item.items():
                responses = param.get('responses')
                # remove 422 response
                if '422' in responses:
                    del responses['422']
                if '404' in responses:
                    del responses['404']
        return self.openapi_schema


class CSRHTTPBearer(HTTPBearer):
    """
    Override HTTPBearer to support custom message structure
    """

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise CSRException(
                    code=status.HTTP_403_FORBIDDEN, msg="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise CSRException(
                    code=status.HTTP_403_FORBIDDEN,
                    msg="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
