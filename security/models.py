import uuid

import numpy as np
from django.db import models
from ndarraydjango.fields import NDArrayField
from django.contrib.auth.models import AbstractUser, User

class TOTPSecret(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)

class FaceTemplate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    template = NDArrayField(shape=(128,), dtype=np.float64)
    image = models.ImageField(upload_to='face_templates/')
    create_at = models.DateTimeField(auto_now_add=True)


class EventType(models.TextChoices):
    USER_CREATED_OK = "USER_CREATED_OK", "User created OK"
    USER_CREATED_FAIL = "USER_CREATED_FAIL", "User created FAIL"
    REGISTER_PWD_OK = "REGISTER_PWD_OK", "Registration password OK"
    REGISTER_PWD_FAIL = "REGISTER_PWD_FAIL", "Registration password FAIL"
    SETUP_OTP_OK = "SETUP_OTP_OK", "Setup OTP OK"
    SETUP_OTP_FAIL = "SETUP_OTP_FAIL", "Setup OTP FAIL"
    SETUP_FACE_OK = "SETUP_FACE_OK", "Setup Face OK"
    SETUP_FACE_FAIL = "SETUP_FACE_FAIL", "Setup Face FAIL"
    LOGIN_PWD_OK = "LOGIN_PWD_OK", "Login password OK"
    LOGIN_PWD_FAIL = "LOGIN_PWD_FAIL", "Login password FAIL"
    OTP_OK = "OTP_OK", "OTP OK"
    OTP_FAIL = "OTP_FAIL", "OTP FAIL"
    FACE_OK = "FACE_OK", "Face OK"
    FACE_FAIL = "FACE_FAIL", "Face FAIL"

class SecurityEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(choices=EventType.choices, max_length=64)

class LoginSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pwd_ok = models.BooleanField(default=False)
    otp_ok = models.BooleanField(default=False)
    face_ok = models.BooleanField(default=False)

    def __str__(self):
        return f"LoginSession(user={self.user}, created_at={self.created_at}, pwd_ok={self.pwd_ok}, otp_ok={self.otp_ok}, face_ok={self.face_ok})"

class RegistrationSession(models.Model):
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pwd_ok = models.BooleanField(default=False)
    otp_ok = models.BooleanField(default=False)
    face_ok = models.BooleanField(default=False)    

    def __str__(self):
        return f"RegistrationSession(user={self.user}, created_at={self.created_at}, pwd_ok={self.pwd_ok}, otp_ok={self.otp_ok}, face_ok={self.face_ok})"
