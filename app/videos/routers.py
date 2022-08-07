from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from app import utils
from app.shortcuts import get_object_or_404, redirect, render, is_htmx
from app.users.decorators import login_required
from app.watch_events.models import WatchEvent
from .models import Video
from .schemas import VideoCreateSchema

router = APIRouter(
    prefix="/videos"
)


@router.get("/create", response_class=HTMLResponse)
@login_required
def video_create_view(request: Request, is_htmx=Depends(is_htmx)):
    if is_htmx:
        return render(request, "videos/htmx/create.html", {})
    return render(request, "videos/create.html", {})


@router.post("/create", response_class=HTMLResponse)
@login_required
def video_create_post_view(request: Request, url: str = Form(...), title: str = Form(...), is_htmx=Depends(is_htmx)):
    raw_data = {
        "url": url,
        "title": title,
        "user_id": request.user.username
    }
    data, errors = utils.valid_schema_data_or_errors(
        raw_data, VideoCreateSchema)
    context = {
        "data": data,
        "errors": errors,
        "url": url,
        "title": title,
    }
    redirect_path = data.get("path") or "/videos/create"
    if is_htmx:
        if len(errors) > 0:
            return render(request, "videos/htmx/create.html", context)
        context = {"path": redirect_path, "title": data.get("title")}
        return render(request, "videos/htmx/link.html", context)
    if len(errors) > 0:
        return render(request, "videos/create.html", context, status_code=400)
    return redirect(redirect_path)


@router.get("/", response_class=HTMLResponse)
def video_list_view(request: Request):
    q = Video.objects.all().limit(100)
    context = {
        "object_list": q
    }
    return render(request, "videos/list.html", context)


@router.get("/{host_id}", response_class=HTMLResponse)
def video_detail_view(request: Request, host_id: str):
    video_obj = get_object_or_404(Video, host_id=host_id)
    start_time = WatchEvent.get_resume_time(
        host_id, request.user.username) if request.user.is_authenticated else 0
    context = {
        "host_id": host_id,
        "object": video_obj,
        "start_time": start_time
    }
    return render(request, "videos/detail.html", context)
