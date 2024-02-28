from django.db import models
from uuid import uuid4
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import os
from datetime import datetime


class UserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_active", True)
        if not username:
            raise ValueError("username is required")
        if not email:
            raise ValueError("email field is required")
        email = self.normalize_email(email)
        user = self.model(username=username, password=password, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get('is_staff'):
            raise ValueError("Super user must have is_staff=True")
        if not extra_fields.get('is_superuser'):
            raise ValueError('Super user must have is_superuser=True')
        return self.create_user(username, email, password, **extra_fields)


def path_and_rename(instance,filename):
    upload_to = 'images/'
    ext = filename.split(".")[-1]
    filename = 'user_{}.{}'.format(int(datetime.now().timestamp()), ext)
    return os.path.join(upload_to, filename)

class Users(AbstractBaseUser):
    GENDER_CHOICES = (
        (1, 'Male'),
        (2, 'Female'),
        (3, 'other')
    )
    _id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    country = models.CharField(max_length=50)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES)
    password = models.CharField(max_length=200)
    pic = models.TextField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'gender', 'phone']

    objects = UserManager()

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
