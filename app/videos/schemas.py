import uuid
from pydantic import BaseModel, validator, root_validator

from app.users.exceptions import InvalidUserIdException
from .exceptions import InvalidYoutubeVideoURLException, VideoAlreadyAddedException
from .extractors import extract_video_id
from .models import Video


class VideoCreateSchema(BaseModel):
    url: str
    user_id: uuid.UUID
    title: str

    @validator("url")
    def validate_video_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not a valid youtube url")
        return url

    @root_validator
    def validate_data(cls, values):
        url = values.get("url")
        if url is None:
            raise ValueError(
                "A valid url is required.")
        user_id = values.get("user_id")
        title = values.get("title") if values.get("title") != "" else None
        try:
            video_obj, created = Video.get_or_create_video(
                url, user_id, title=title)
        except InvalidYoutubeVideoURLException:
            raise ValueError(
                f"{url} is not a valid youtube url")
        except VideoAlreadyAddedException:
            raise ValueError(
                f"{url} has already been added to your account.")
        except InvalidUserIdException:
            raise ValueError(
                "There's problem with your account, please try again.")
        except:
            raise ValueError(
                "There's problem with your account, please try again.")
        if video_obj is None:
            raise ValueError(
                "There's problem with your account, please try again.")
        if not isinstance(video_obj, Video):
            raise ValueError(
                "There's problem with your account, please try again.")
        return video_obj.as_data()


class VideoEditSchema(BaseModel):
    url: str
    title: str

    @validator("url")
    def validate_video_url(cls, v, values, **kwargs):
        url = v
        video_id = extract_video_id(url)
        if video_id is None:
            raise ValueError(f"{url} is not a valid youtube url")
        return url
