import json
import pathlib
from cassandra.cqlengine.management import sync_table
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic.error_wrappers import ValidationError
from starlette.middleware.authentication import AuthenticationMiddleware

from . import db, utils
from .playlists.models import Playlist
from .playlists.routers import router as playlist_router
from .shortcuts import redirect, render
from .users.backends import JWTCookieBackend
from .users.decorators import login_required
from .users.auth import create_user
from .users.models import User
from .users.schemas import UserLoginSchema, UserSignupSchema
from .videos.models import Video
from .videos.routers import router as video_router
from .watch_events.models import WatchEvent
from .watch_events.routers import router as watch_event_router

app = FastAPI()
app.add_middleware(AuthenticationMiddleware, backend=JWTCookieBackend())
app.include_router(video_router)
app.include_router(watch_event_router)
app.include_router(playlist_router)
DB_SESSION = None

from .handlers import *  # nopep8


@app.on_event("startup")
def on_startup():
    global DB_SESSION
    DB_SESSION = db.get_session()
    sync_table(Playlist)
    sync_table(User)
    sync_table(Video)
    sync_table(WatchEvent)


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html", {})
    return render(request, "home.html", {})


@app.get("/account", response_class=HTMLResponse)
@login_required
def account_view(request: Request):
    return render(request, "account.html")


@app.get("/login", response_class=HTMLResponse)
def login_get_view(request: Request):
    session_id = request.cookies.get("session_id") or None
    return render(request, "auth/login.html", {"logged_in": session_id is not None})


@app.post("/login", response_class=HTMLResponse)
def login_post_view(request: Request,
                    email: str = Form(...),
                    password: str = Form(...),
                    ):

    raw_data = {
        "email": email,
        "password": password,
    }

    data, errors = utils.valid_schema_data_or_errors(
        raw_data, UserLoginSchema)

    context = {
        "data": data,
        "errors": errors
    }

    if len(errors) > 0:
        return render(request, "auth/login.html", context, status_code=400)

    return redirect("/", cookies=data)


@app.get("/signup", response_class=HTMLResponse)
def signup_get_view(request: Request):
    return render(request, "auth/signup.html", {})


@app.post("/signup", response_class=HTMLResponse)
def signup_post_view(request: Request,
                     email: str = Form(...),
                     password: str = Form(...),
                     password_confirm: str = Form(...)
                     ):

    raw_data = {
        "email": email,
        "password": password,
        "password_confirm": password_confirm
    }
    data, errors = utils.valid_schema_data_or_errors(
        raw_data, UserSignupSchema)

    context = {
        "data": data,
        "errors": errors
    }

    if len(errors) > 0:
        return render(request, "auth/signup.html", context, status_code=400)

    user_obj = create_user(data['email'], data['password'].get_secret_value())

    return redirect("/login")
