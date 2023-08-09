from django.contrib.auth.models import User
from .base import BaseModelMap

class UserMap(BaseModelMap):
    destmodel = User
    sourcetable = "auth_user"

UserMap().importdata()