from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import close_client, ensure_indexes, ping
from app.exceptions import AppException
from app.routers.auth import router as auth_router
from app.routers.sucamec import router as sucamec_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ping()
    ensure_indexes()
    yield
    close_client()


app = FastAPI(title="MGA GADSO API - Modulo SIGEMO", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "message": exc.message},
    )


app.include_router(auth_router)
app.include_router(sucamec_router)
app.include_router(users_router)


@app.get("/api/health")
def health():
    return {"ok": True, "service": "mga-gadso-backend", "module": "sigemo"}
