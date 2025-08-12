from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
import uuid






class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,otp=None,**extra_fields):
        if not email:
            raise ValueError('Email is requierd')
        email=self.normalize_email(email)
        user=self.model(email=email,otp=otp,**extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None):
        user=self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    
    

    

class CustomUser(AbstractBaseUser):
    # id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id=models.BigAutoField(primary_key=True)
    email=models.EmailField(unique=True)
    otp=models.CharField(max_length=4, blank=True, null=True)
    is_admin=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser