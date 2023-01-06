"""
Database Models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)



class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email : str, password="" , **extra_fields) -> models:
        """Create, save, and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email : str, password : str , **extra_fields) -> models:
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def check_password(self, user: models) -> bool:
        return super().check_password(user)
    
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email=models.EmailField(max_length=244,unique=True)
    name=models.TextField(max_length=255)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD="email"
