import uuid
from app.config import get_settings
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.query import DoesNotExist, MultipleObjectsReturned

from app.users.exceptions import InvalidUserIdException
from app.users.models import User
from app.shortcuts import templates
from .exceptions import InvalidYoutubeVideoURLException, VideoAlreadyAddedException
from .extractors import extract_video_id


settings = get_settings()


class Video(Model):
    __keyspace__ = settings.keyspace
    host_id = columns.Text(primary_key=True)
    db_id = columns.UUID(primary_key=True, default=uuid.uuid1)
    host_service = columns.Text(default='youtube')
    title = columns.Text()
    url = columns.Text()
    user_id = columns.UUID()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Video(title={self.title}, host_id={self.host_id}, host_service={self.host_service})"

    def as_data(self):
        return {f"{self.host_service}_id": self.host_id, "path": self.path, "title": self.title}

    def render(self):
        basename = self.host_service
        template_name = f"videos/renderers/{basename}.html"
        context = {"host_id": self.host_id, "title": self.title}
        t = templates.get_template(template_name)
        return t.render(context)

    def update_video_url(self, url, save=True):
        host_id = extract_video_id(url)
        if not host_id:
            return None
        self.url = url
        self.host_id = host_id
        if save:
            self.save()
        return url

    @property
    def path(self):
        return f"/videos/{self.host_id}"

    @staticmethod
    def get_or_create_video(url, user_id=None, **kwargs):
        host_id = extract_video_id(url)
        obj = None
        created = False
        try:
            obj = Video.objects.get(host_id=host_id)
        except MultipleObjectsReturned:
            q = Video.objects.allow_filtering().filter(host_id=host_id)
            obj = q.first()
        except DoesNotExist:
            obj = Video.add_video(url, user_id, **kwargs)
            created = True
        except:
            raise Exception("Invalid Exception")
        return obj, created

    @staticmethod
    def add_video(url, user_id=None, title=None):
        host_id = extract_video_id(url)
        if not host_id:
            raise InvalidYoutubeVideoURLException("Invalid Youtube Video URL")
        user = User.check_exists(user_id)
        if not user:
            raise InvalidUserIdException("Invalid user_id")
        q = Video.objects.filter(
            host_id=host_id, user_id=user_id).allow_filtering()
        if q.count() != 0:
            raise VideoAlreadyAddedException("Video already added")
        return Video.create(host_id=host_id, user_id=user_id, url=url, title=title)
