import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

import settings
from app.api import api
from utils.exceptions import exception_handlers, http_middleware
from utils.fastapi.application import CAFastAPI
from utils.log import redirect_log

docs_url = '/docs' if settings.DEBUG else None
redoc_url = '/redoc' if settings.DEBUG else None

# main app
app = CAFastAPI(title='csr_to_ca', debug=settings.DEBUG,
                version='0.0.1', description="""
This document interface is limited to the internal use of the csr_to_ca system
## Important
- An array/list in the Query argument is passed with "&" concatenating multiple key/value pairs
- Suggest adding gzip to the request header Accept-Encoding
""",
                docs_url=docs_url, redoc_url=redoc_url,
                exception_handlers=exception_handlers,
                on_startup=[redirect_log]
                )
app.include_router(api)

if settings.CORS_ORIGINS_APP:
    app.add_middleware(CORSMiddleware,
                           allow_origins=settings.CORS_ORIGINS_APP,
                           allow_credentials=True,
                           allow_methods=["*"],
                           allow_headers=["*"])

app.middleware('http')(http_middleware)
app.add_middleware(GZipMiddleware)

if __name__ == '__main__':
    print("The csr to ca system is launched")
    uvicorn.run("main:app",
                host=settings.WEB_HOST,
                port=settings.WEB_PORT)
