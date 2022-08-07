import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException

from app import utils
from app.shortcuts import get_object_or_404, redirect, render, is_htmx
from app.users.decorators import login_required
from app.watch_events.models import WatchEvent
from .models import Playlist
from .schemas import PlaylistCreateSchema, PlaylistVideoAddSchema

router = APIRouter(
    prefix="/playlists"
)


@router.get("/create", response_class=HTMLResponse)
@login_required
def playlist_create_view(request: Request):
    return render(request, "playlists/create.html", {})


@router.post("/create", response_class=HTMLResponse)
@login_required
def playlist_create_post_view(request: Request, title: str = Form(...)):
    raw_data = {
        "title": title,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_errors(
        raw_data, PlaylistCreateSchema)
    context = {
        "data": data,
        "errors": errors,
    }
    if len(errors) > 0:
        return render(request, "playlists/create.html", context, status_code=400)
    obj = Playlist.objects.create(**data)
    redirect_path = obj.path or "/playlists/create"
    return redirect(redirect_path)


@router.get("/", response_class=HTMLResponse)
def playlist_list_view(request: Request):
    q = Playlist.objects.all().limit(100)
    context = {
        "object_list": q
    }
    return render(request, "playlists/list.html", context)


@router.get("/{db_id}", response_class=HTMLResponse)
def playlist_detail_view(request: Request, db_id: uuid.UUID):
    playlist_obj = get_object_or_404(Playlist, db_id=db_id)
    context = {
        "db_id": db_id,
        "object": playlist_obj,
        "videos": playlist_obj.get_videos()
    }
    return render(request, "playlists/detail.html", context)


@router.get("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
def add_video_to_playlist_view(
    request: Request,
    db_id: uuid.UUID,
    is_htmx=Depends(is_htmx)
):
    context = {
        "db_id": db_id
    }
    if not is_htmx:
        raise HTTPException(status_code=400)
    return render(request, "playlists/htmx/add-video.html", context)


@router.post("/{db_id}/add-video", response_class=HTMLResponse)
@login_required
def add_video_to_playlist_post_view(
    request: Request,
    db_id: uuid.UUID,
    url: str = Form(...),
    title: str = Form(...),
    is_htmx=Depends(is_htmx)
):
    raw_data = {
        "url": url,
        "title": title,
        "user_id": request.user.username,
        "playlist_id": db_id
    }
    data, errors = utils.valid_schema_data_or_errors(
        raw_data, PlaylistVideoAddSchema)
    context = {
        "data": data,
        "errors": errors,
        "url": url,
        "title": title,
        "db_id": db_id
    }
    redirect_path = data.get("path") or "/playlists/create"
    if not is_htmx:
        raise HTTPException(status_code=400)
    if len(errors) > 0:
        return render(request, "playlists/htmx/add-video.html", context)
    context = {"path": redirect_path, "title": data.get("title")}
    return render(request, "videos/htmx/link.html", context)


@router.post("/{db_id}/{host_id}/delete", response_class=HTMLResponse)
@login_required
def add_video_to_playlist_post_view(
    request: Request,
    db_id: uuid.UUID,
    host_id: str,
    is_htmx=Depends(is_htmx),
    index: Optional[int] = Form(default=None)
):
    if not is_htmx:
        raise HTTPException(status_code=400)
    try:
        playlist_obj = get_object_or_404(Playlist, db_id=db_id)
    except:
        return HTMLResponse("Error. please reload the page.")
    if isinstance(index, int):
        host_ids = playlist_obj.host_ids
        host_ids.pop(index)
        playlist_obj.add_host_ids(host_ids, replace_all=True)
    return HTMLResponse("Deleted.")
