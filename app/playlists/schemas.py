import uuid
from pydantic import BaseModel, validator, root_validator

from app.videos.extractors import extract_video_id
from app.videos.models import Video
from .models import Playlist


class PlaylistCreateSchema(BaseModel):
    user_id: uuid.UUID
    title: str


class PlaylistVideoAddSchema(BaseModel):
    url: str
    user_id: uuid.UUID
    title: str
    playlist_id: uuid.UUID

    @validator("url")
    def validate_video_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not a valid youtube url")
        return url

    @validator("playlist_id")
    def validate_playlist_id(cls, v, values, **kwargs):
        q = Playlist.objects.filter(db_id=v)
        if q.count() == 0:
            raise ValueError(f"{v} is not a valid Playlist")
        return v

    @root_validator
    def validate_data(cls, values):
        url = values.get("url")
        if url is None:
            raise ValueError(
                "A valid url is required.")
        user_id = values.get("user_id")
        playlist_id = values.get("playlist_id")
        title = values.get("title") if values.get("title") != "" else None
        try:
            video_obj, created = Video.get_or_create_video(
                url, user_id, title=title)
        except:
            raise ValueError(
                "There's problem with your account, please try again.")
        if not isinstance(video_obj, Video):
            raise ValueError(
                "There's problem with your account, please try again.")
        else:
            playlist_obj = Playlist.objects.get(db_id=playlist_id)
            playlist_obj.add_host_ids(host_ids=[video_obj.host_id])
            playlist_obj.save()
        return video_obj.as_data()
