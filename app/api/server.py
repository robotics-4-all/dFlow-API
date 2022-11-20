from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core import config, tasks

from app.api.routes import router as api_router


def get_application():
    app = FastAPI(title="dFlow-Platform-API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    app.add_event_handler("startup", tasks.create_start_app_handler(app))
    app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))

    return app


app = get_application()
