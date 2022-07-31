import datetime
from jose import jwt, ExpiredSignatureError

from app import config
from .models import User

secret_key = config.get_settings().secret_key
algo = config.get_settings().jwt_algo


def create_user(email, password):
    try:
        user_obj = User.create_user(email, password)
    except Exception as e:
        user_obj = None
    return user_obj


def authenticate(email, password):
    try:
        user_obj = User.objects.get(email=email)
    except Exception as e:
        user_obj = None
    if not user_obj.verify_password(password):
        user_obj = None
    return user_obj


def login(user_obj, expires=60):
    raw_data = {
        "user_id": f"{user_obj.user_id}",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=expires)
    }
    return jwt.encode(raw_data, secret_key, algorithm=algo)


def verify_user_id(token):
    data = {}
    try:
        data = jwt.decode(token, secret_key, algorithms=[algo])
    except ExpiredSignatureError as e:
        print(e)
    except:
        pass
    if 'user_id' not in data:
        return None
    return data
