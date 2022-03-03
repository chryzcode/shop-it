from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils.text import slugify


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=300)
    store_name = models.CharField(max_length=150, unique=True)
    avatar = models.ImageField(upload_to="user-profile-images/", null=True)
    slugified_store_name = models.SlugField(max_length=255, unique=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        if not self.slugified_store_name:
            self.slugified_store_name = slugify(self.store_name)
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.store_name
